from bleak import BleakScanner
import asyncio

async def scan_devices():
    print("🔍 Bluetoothデバイスをスキャン中...")
    devices = await BleakScanner.discover()
    
    for device in devices:
        print(f"📡 デバイス名: {device.name}, アドレス: {device.address}")

# スクリプトを実行
asyncio.run(scan_devices())

from bleak import BleakClient
import asyncio

OURA_RING_ADDRESS = "XX:XX:XX:XX:XX:XX"  # Oura Ringのアドレスを入力

async def list_services():
    async with BleakClient(OURA_RING_ADDRESS) as client:
        services = await client.get_services()
        for service in services:
            print(f"\n🔹 サービス: {service.uuid}")
            for char in service.characteristics:
                print(f"   🟢 特性: {char.uuid} | プロパティ: {char.properties}")

# スクリプトを実行
asyncio.run(list_services())