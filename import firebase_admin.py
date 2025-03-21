import asyncio
import firebase_admin
from firebase_admin import credentials, firestore
from bleak import BleakClient, BleakScanner
import numpy as np
import threading
import datetime

# ✅ 自分用のIDを設定（"user_1" or "user_2"）
DEVICE_ID = "###"  # ← これをペアの人と区別するように変更！

# ✅ Firestore 初期化
cred = credentials.Certificate("###")  # 各自の秘密鍵パス
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ✅ BluetoothのUUID（Polar H10/H9）
HEART_RATE_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

# ✅ Polarデバイスを自動検出
async def find_polar_device():
    print("🔍 Searching for Polar H9/H10...")
    devices = await BleakScanner.discover()
    for device in devices:
        if device.name and ("Polar H10" in device.name or "Polar H9" in device.name):
            print(f"✅ Found {device.name}: {device.address}")
            return device.address
    print("❌ No Polar H10/H9 found.")
    return None

# ✅ 心拍数データをFirestoreにアップロード
async def hr_callback(sender, data):
    flags = data[0]
    heart_rate = data[1] if (flags & 0x01) == 0 else int.from_bytes(data[1:3], byteorder="little", signed=False)
    print(f"📡 {DEVICE_ID} HR: {heart_rate} bpm")

    timestamp = datetime.datetime.utcnow()
    doc_ref = db.collection("heart_rate_data").document()
    doc_ref.set({
        "device_id": DEVICE_ID,
        "heart_rate": heart_rate,
        "timestamp": timestamp
    })

# ✅ Polarに接続してHRデータ取得
async def connect_polar():
    address = await find_polar_device()
    if not address:
        return

    async with BleakClient(address) as client:
        print(f"✅ Connected to {address}")
        await client.start_notify(HEART_RATE_UUID, hr_callback)
        await asyncio.sleep(600)  # 10分間接続
        await client.stop_notify(HEART_RATE_UUID)
        print("✅ Stopped HR streaming.")

# ✅ 別スレッドで接続処理を実行
threading.Thread(target=lambda: asyncio.run(connect_polar()), daemon=True).start()
