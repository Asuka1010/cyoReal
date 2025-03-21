const functions = require("firebase-functions");
const admin = require("firebase-admin");
admin.initializeApp();

exports.receiveHeartRate = functions.https.onRequest(async (req, res) => {
  const data = req.body;

  if (!data || !data.user || !data.heart_rate) {
    return res.status(400).send("Missing data");
  }

  const docRef = admin.firestore().collection("heart_rate_data").doc();
  await docRef.set({
    user: data.user,
    heart_rate: data.heart_rate,
    timestamp: new Date().toISOString(),
  });

  return res.status(200).send("Data stored!");
});
