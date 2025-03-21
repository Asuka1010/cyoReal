import asyncio
from bleak import BleakClient, BleakScanner
import threading
import datetime
import json
import requests

# 🔧 あなたのCloud FunctionのURLをここに貼る
CLOUD_FUNCTION_URL = "https://us-central1-<your-project-id>.cloudfunctions.net/submitHeartRate"

# ✅ 自分のID（デバイス名やニックネームでもOK）
DEVICE_ID = "yuto_device"

# ✅ BluetoothのUUID（Polar H10/H9共通）
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

# ✅ 心拍数データをCloud FunctionにPOST送信
async def hr_callback(sender, data):
    flags = data[0]
    heart_rate = data[1] if (flags & 0x01) == 0 else int.from_bytes(data[1:3], byteorder="little", signed=False)
    print(f"📡 {DEVICE_ID} HR: {heart_rate} bpm")

    payload = {
        "user": DEVICE_ID,
        "heart_rate": heart_rate
    }

    try:
        response = requests.post(CLOUD_FUNCTION_URL, json=payload)
        if response.status_code != 200:
            print("⚠️ Failed to send data:", response.text)
    except Exception as e:
        print("❌ Network error:", e)

# ✅ Polarに接続して心拍数を取得
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

# ✅ 実行（別スレッドで）
threading.Thread(target=lambda: asyncio.run(connect_polar()), daemon=True).start()
