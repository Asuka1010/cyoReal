import firebase_admin
from firebase_admin import credentials, firestore

# Firebase の秘密鍵をロード
cred = credentials.Certificate("serviceAccountKey.json")
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")  
    firebase_admin.initialize_app(cred)

# Firestore クライアント
db = firestore.client()

# サンプルデータを書き込む
doc_ref = db.collection("heart_rate_data").document("test_device")
doc_ref.set({
    "timestamp": firestore.SERVER_TIMESTAMP,
    "heart_rate": 72,
    "user": "Asuka"
})

print("✅ Firestore にデータを書き込みました！")

import asyncio
import threading
import numpy as np
from flask import Flask
from flask_socketio import SocketIO
from bleak import BleakClient, BleakScanner

# Flask App (Backend Only)
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow cross-origin requests

# UUID for Heart Rate Service
HEART_RATE_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

# Data storage for correlation
real_hr_data = []
simulated_hr_data = []

async def scan_for_polar():
    """Scan for Bluetooth devices and return the address of a Polar H9/H10."""
    print("🔍 Scanning for Polar H9/H10 devices...")

    devices = await BleakScanner.discover()
    
    for device in devices:
        if device.name and ("Polar H10" in device.name or "Polar H9" in device.name):
            print(f"✅ Found {device.name}: {device.address}")
            return device.address  # Return first matching device found

    print("❌ No Polar H9/H10 devices found. Ensure Bluetooth is on and device is nearby.")
    return None  # No device found

async def hr_callback(sender, data):
    """Process incoming heart rate data and calculate correlation."""
    flags = data[0]
    hr_value = data[1] if (flags & 0x01) == 0 else int.from_bytes(data[1:3], byteorder="little", signed=False)

    print(f"📡 Heart Rate: {hr_value} bpm")

    # Simulate a second dataset with slight variation
    simulated_value = hr_value + np.random.normal(0, 2)

    # Store data for correlation
    real_hr_data.append(hr_value)
    simulated_hr_data.append(simulated_value)

    # Keep only last 30 seconds of data
    if len(real_hr_data) > 30:
        real_hr_data.pop(0)
        simulated_hr_data.pop(0)

    # Calculate correlation if enough data points exist
    correlation = np.corrcoef(real_hr_data, simulated_hr_data)[0, 1] if len(real_hr_data) > 5 else 0

    # Send data to frontend
    socketio.emit("heart_rate", {
        "real_heart_rate": hr_value,
        "simulated_heart_rate": simulated_value,
        "correlation": round(correlation, 2)
    })

async def connect_polar():
    """Scan for Polar H9/H10 and connect to it."""
    polar_address = await scan_for_polar()  # Find the device automatically
    if not polar_address:
        return  # No device found, exit function

    async with BleakClient(polar_address) as client:
        print(f"✅ Connected to {polar_address}!")

        try:
            await client.start_notify(HEART_RATE_UUID, hr_callback)
            await asyncio.sleep(600)  # Keep running for 10 minutes
        except Exception as e:
            print(f"❌ Error starting notifications: {e}")

        try:
            if client.is_connected:
                await client.stop_notify(HEART_RATE_UUID)
                print("✅ Stopped Heart Rate streaming.")
        except Exception as e:
            print(f"⚠️ Warning: Could not stop notifications: {e}")

# Run asyncio in background
def run_asyncio():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(connect_polar())

# Start Polar connection in a background thread
threading.Thread(target=run_asyncio, daemon=True).start()

# Start Flask Server
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
