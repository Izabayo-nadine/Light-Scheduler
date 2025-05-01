import paho.mqtt.client as mqtt
import json
import serial
import time
from datetime import datetime
import logging
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LightController:
    def __init__(self):
        self.serial_port = None
        self.current_schedule = None
        self.scheduler_thread = None
        self.running = False

    def connect_serial(self, port='COM9', baudrate=9600):
        try:
            self.serial_port = serial.Serial(port, baudrate, timeout=1)
            logger.info(f"Connected to Arduino on {port}")
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to connect to Arduino: {e}")
            return False

    def send_command(self, command):
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.write(command.encode())
                logger.info(f"Sent command to Arduino: {command}")
                return True
            except serial.SerialException as e:
                logger.error(f"Failed to send command to Arduino: {e}")
                return False
        return False

    def on_connect(self, client, userdata, flags, rc):
        logger.info("Connected to MQTT broker")
        client.subscribe("light/schedule")

    def on_message(self, client, userdata, msg):
        try:
            schedule = json.loads(msg.payload.decode())
            logger.info(f"Received schedule: {schedule}")
            self.current_schedule = schedule
            self.start_scheduler()
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def start_scheduler(self):
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.running = False
            self.scheduler_thread.join()
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self.schedule_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()

    def schedule_loop(self):
        while self.running:
            if self.current_schedule:
                current_time = datetime.now().strftime("%H:%M")
                on_time = self.current_schedule['onTime']
                off_time = self.current_schedule['offTime']

                if current_time == on_time:
                    self.send_command('1')
                elif current_time == off_time:
                    self.send_command('0')

            time.sleep(30)  # Check every 30 seconds

    def cleanup(self):
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

def main():
    controller = LightController()
    
    # Connect to Arduino
    if not controller.connect_serial():
        logger.error("Failed to connect to Arduino. Exiting...")
        return

    # Setup MQTT client
    client = mqtt.Client()
    client.on_connect = controller.on_connect
    client.on_message = controller.on_message

    try:
        # Connect to MQTT broker
        client.connect("localhost", 1883, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        logger.info("Stopping light controller...")
    finally:
        controller.cleanup()
        client.disconnect()

if __name__ == "__main__":
    main() 