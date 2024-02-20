import asyncio
from bleak import BleakClient
import socketio

# Socket.IO client setup
sio = socketio.AsyncClient()

address = "94:A9:A8:18:0B:AC"  # Your device MAC address
CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"  # The characteristic UUID

@sio.event
async def connect():
    print("Connected to the server.")

@sio.event
async def disconnect():
    print("Disconnected from the server.")

def notification_handler(sender, data):
    """Callback function that is called when a notification is received."""
    message = data.decode('utf-8')
    print(f"Received message from {sender}: {message}")
    # Forward the message to the server
    asyncio.create_task(sio.emit('message', message))

async def listen_for_messages(address):
    async with BleakClient(address) as client:
        if await client.is_connected():
            print(f"Connected to {address}")

            # Connect to the socket.io server
            await sio.connect('http://192.168.1.159:3000')  # Update with your server address
            print("Socket.IO Client connected")

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

async def main():
    await listen_for_messages(address)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
