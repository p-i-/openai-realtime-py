import os
import signal
import time
from dotenv import load_dotenv

from Realtime import Realtime
from log import logger as logging
from Tools import tools_message

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

    realtime = Realtime(api_key, ws_url, session_config)

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

session_config = {
    "modalities": ["text"],
    # "instructions": "You are a helpful assistant.",
    # "voice": "sage",
    # "input_audio_format": "pcm16",
    # "output_audio_format": "pcm16",
    # "input_audio_transcription": {
    #     "model": "whisper-1"
    # },
    # "turn_detection": {
    #     "type": "server_vad",
    #     "threshold": 0.5,
    #     "prefix_padding_ms": 300,
    #     "silence_duration_ms": 500
    # },
    "tools": tools_message,
    "tool_choice": "auto",
    # "temperature": 0.8,
    # "max_response_output_tokens": "inf"
}

if __name__ == '__main__':
    main()
