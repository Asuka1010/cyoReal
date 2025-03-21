#corrcoef.py

import firebase_admin
from firebase_admin import credentials, firestore
import numpy as np
import functions_framework  # Google Cloud Functions 用

# Firestore 初期化
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred)
db = firestore.client()

@functions_framework.http
def compute_correlation(request):
    try:
        # 最新の心拍数データをそれぞれ取得
        user1_docs = db.collection("heart_rate_user1").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(30).stream()
        user2_docs = db.collection("heart_rate_user2").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(30).stream()

        user1_hr = [doc.to_dict()["heart_rate"] for doc in user1_docs]
        user2_hr = [doc.to_dict()["heart_rate"] for doc in user2_docs]

        # データが足りない場合は処理しない
        if len(user1_hr) < 5 or len(user2_hr) < 5:
            return "Not enough data", 200

        # 配列の長さを揃える（短い方に合わせる）
        min_len = min(len(user1_hr), len(user2_hr))
        user1_hr = user1_hr[:min_len][::-1]  # 最新→古いを古い→最新に
        user2_hr = user2_hr[:min_len][::-1]

        correlation = float(np.corrcoef(user1_hr, user2_hr)[0, 1])

        # Firestore に保存
        db.collection("correlation_results").add({
            "correlation": correlation,
            "user1_last": user1_hr[-1],
            "user2_last": user2_hr[-1],
            "timestamp": firestore.SERVER_TIMESTAMP
        })

        return f"✅ Correlation: {correlation}", 200

    except Exception as e:
        return f"❌ Error: {str(e)}", 500
