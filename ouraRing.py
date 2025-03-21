from bleak import BleakScanner
import asyncio

async def scan_devices():
    print("🔍 Scanning for BLE devices...")
    devices = await BleakScanner.discover()
    
    for device in devices:
        print(f"📡 Device: {device.name}, Address: {device.address}")

# Run the scanner
asyncio.run(scan_devices())

from bleak import BleakClient
import asyncio

OURA_RING_ADDRESS = "XX:XX:XX:XX:XX:XX"  # Replace with your Oura Ring’s address

async def list_services():
    async with BleakClient(OURA_RING_ADDRESS) as client:
        services = await client.get_services()
        for service in services:
            print(f"\n🔹 Service: {service.uuid}")
            for char in service.characteristics:
                print(f"   🟢 Characteristic: {char.uuid} | Properties: {char.properties}")

# Run the script
asyncio.run(list_services())

from bleak import BleakClient
import asyncio

OURA_RING_ADDRESS = "XX:XX:XX:XX:XX:XX"  # Replace with your Oura Ring’s address
HEART_RATE_UUID = "00002a37-0000-1000-8000-00805f9b34fb"  # Replace with correct UUID

async def heart_rate_callback(sender, data):
    heart_rate = int.from_bytes(data[:2], byteorder="little", signed=True)
    print(f"💓 Real-time Heart Rate: {heart_rate} bpm")

async def connect_oura():
    async with BleakClient(OURA_RING_ADDRESS) as client:
        print("✅ Connected to Oura Ring!")
        await client.start_notify(HEART_RATE_UUID, heart_rate_callback)
        await asyncio.sleep(60)  # Stream for 60 seconds
        await client.stop_notify(HEART_RATE_UUID)
        print("✅ Stopped Streaming")

# Run the script
asyncio.run(connect_oura())
