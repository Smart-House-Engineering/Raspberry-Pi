import asyncio
from bleak import BleakClient

address = "94:A9:A8:18:0B:AC"  # Your device MAC address
CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"  # The characteristic UUID for HM-10 for sending/receiving data

async def send_hello_world(address):
    async with BleakClient(address) as client:
        if await client.is_connected():
            print(f"Connected to {address}")
            await client.write_gatt_char(CHARACTERISTIC_UUID, bytearray("Hello World", "utf-8"))
            print("Sent 'Hello World' to the device.")
        else:
            print(f"Failed to connect to {address}")

loop = asyncio.get_event_loop()
loop.run_until_complete(send_hello_world(address))
