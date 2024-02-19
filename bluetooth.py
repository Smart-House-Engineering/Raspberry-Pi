import asyncio
from bleak import BleakClient

address = "94:A9:A8:18:0B:AC"  # Your device MAC address
CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"  # The characteristic UUID for HM-10 for sending/receiving data

def notification_handler(sender, data):
    """Callback function that is called when a notification is received."""
    print(f"Received message from {sender}: {data.decode('utf-8')}")

async def listen_for_messages(address):
    async with BleakClient(address) as client:
        if await client.is_connected():
            print(f"Connected to {address}")

            # Send "Hello World" to the device
            await client.write_gatt_char(CHARACTERISTIC_UUID, bytearray("Hello World", "utf-8"))
            print("Sent 'Hello World' to the device.")

            # Subscribe to notifications from the device
            await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
            print("Listening for messages from the device. Press Ctrl+C to stop...")

            # Keep the program running
            await asyncio.sleep(float('inf'))
        else:
            print(f"Failed to connect to {address}")

loop = asyncio.get_event_loop()
loop.run_until_complete(listen_for_messages(address))
