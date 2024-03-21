import asyncio
from bleak import BleakClient
import socketio
import json

message_buffer = ''

# Socket.IO client setup
sio = socketio.AsyncClient()

# address = "94:A9:A8:18:0B:AC"  # Old house
address = "94:A9:A8:18:18:22"  # New House
CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"  # The characteristic UUID

ble_client = None

@sio.event
async def connect():
    print("Connected to the server.")

@sio.event
async def disconnect():
    print("Disconnected from the server.")

@sio.event
async def message(data):
    """Handle incoming messages from the WebSocket and forward them to the Bluetooth device."""
    print(f"Received message from server: {data}")
    if ble_client and ble_client.is_connected:
        # Convert the message to bytearray before sending
        await ble_client.write_gatt_char(CHARACTERISTIC_UUID, bytearray(data, "utf-8"))
        print(f"Forwarded message to the device: {data}")

def is_complete_json(json_str):
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        return False

async def forward_complete_message(message):
    """Parse and forward the complete message as JSON."""
    try:
        # Forward the parsed JSON object to the server
        message_json = json.loads(message)
        message_json['device_mac'] = address
        message=json.dumps(message_json)
        await sio.emit('message', message)
        print("Forwarded complete JSON to the server.")
    except Exception as e:
        # Log or handle any exceptions that occur during forwarding
        print(f"Error forwarding message: {e}")

def notification_handler(sender, data):
    """Callback function that is called when a notification is received."""
    global message_buffer
    message = data.decode('utf-8')
    
    # Append the new fragment to the buffer
    message_buffer += message
    # print(message_buffer)

    # Check if the buffer forms a complete JSON string
    if is_complete_json(message_buffer):
        print("Complete JSON message assembled, forwarding...")
        asyncio.create_task(forward_complete_message(message_buffer))
        message_buffer = ''  # Clear the buffer after forwarding
    # else:
        # print("Message fragment received, waiting for more data...")

async def listen_for_messages(address):
    global ble_client
    ble_client = BleakClient(address)
    async with ble_client as client:
        if await client.is_connected():
            print(f"Connected to {address}")

            # Connect to the socket.io server
            await sio.connect('http://192.168.1.159:3000')  # Update with your server address
            print("Socket.IO Client connected")

            # Send "Hello World" to the device
            # await client.write_gatt_char(CHARACTERISTIC_UUID, bytearray("Hello World", "utf-8"))
            # print("Sent 'Hello World' to the device.")

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
