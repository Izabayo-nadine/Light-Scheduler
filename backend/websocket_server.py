import asyncio
import websockets
import json
import subprocess
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LightSchedulerServer:
    def __init__(self):
        self.clients = set()
        self.current_schedule = None

    async def register(self, websocket):
        self.clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.clients)}")

    async def unregister(self, websocket):
      self.clients.remove(websocket)
      logger.info(f"Client disconnected. Total clients: {len(self.clients)}")


    async def broadcast(self, message):
        if self.clients:
            await asyncio.gather(
                *[client.send(json.dumps(message)) for client in self.clients]
            )

    def publish_to_mqtt(self, message):
        try:
            # Use mosquitto_pub to publish the message
            cmd = ['mosquitto_pub', '-t', 'light/schedule', '-m', message]
            subprocess.run(cmd, check=True)
            logger.info(f"Published to MQTT: {message}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to publish to MQTT: {e}")
            return False
        return True

    async def handle_message(self, websocket, message):
        try:
            data = json.loads(message)
            if data['type'] == 'schedule':
                # Format the schedule message
                schedule_msg = json.dumps({
                    'onTime': data['onTime'],
                    'offTime': data['offTime']
                })
                
                # Publish to MQTT
                if self.publish_to_mqtt(schedule_msg):
                    # Update current schedule
                    self.current_schedule = data
                    # Broadcast the update to all clients
                    await self.broadcast({
                        'type': 'status',
                        'message': 'Schedule updated successfully'
                    })
                else:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'Failed to update schedule'
                    }))
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'Invalid message format'
            }))
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await websocket.send(json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def handler(self, websocket):
        await self.register(websocket)
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client connection closed")
        finally:
            await self.unregister(websocket)


async def main():
    server = LightSchedulerServer()
    async with websockets.serve(server.handler, "localhost", 8765):
        logger.info("WebSocket server started on ws://localhost:8765")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user") 