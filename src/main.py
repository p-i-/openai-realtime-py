import os
import signal
import time
import logging
from dotenv import load_dotenv

from Realtime import Realtime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Load environment variables from a .env file
load_dotenv()

quitFlag = False

def signal_handler(sig, frame, realtime_instance):
    """Handle Ctrl+C and initiate graceful shutdown."""
    logging.info('Received Ctrl+C! Initiating shutdown...')
    realtime_instance.stop()
    global quitFlag
    quitFlag = True

def main():
    api_key = os.getenv('OPENAI_API_KEY')
    ws_url = 'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01'

    if not api_key:
        logging.error('OPENAI_API_KEY not found in environment variables!')
        return

    realtime = Realtime(api_key, ws_url)

    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, realtime))

    try:
        realtime.start()
        while not quitFlag:
            time.sleep(0.1)

    except Exception as e:
        logging.error(f'Error in main loop: {e}')
        realtime.stop()

    finally:
        logging.info('Exiting main.')
        realtime.stop()  # Ensures cleanup if any error occurs

if __name__ == '__main__':
    main()
