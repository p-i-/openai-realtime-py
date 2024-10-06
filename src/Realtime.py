import base64
import logging
import threading

from Socket import Socket
from AudioIO import AudioIO

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class Realtime:
    def __init__(self, api_key, ws_url):
        self.socket = Socket(api_key, ws_url, on_msg=self.handle_message)
        self.audio_io = AudioIO(on_audio_callback=self.send_audio_to_socket)
        self.audio_thread = None  # Store thread references
        self.recv_thread = None

    def start(self):
        """ Start WebSocket and audio processing. """
        self.socket.connect()

        # Send initial request to start the conversation
        self.socket.send({
            'type': 'response.create',
            'response': {
                'modalities': ['audio', 'text'],
                'instructions': 'Please assist the user.'
            }
        })

        # Start processing microphone audio
        self.audio_thread = threading.Thread(target=self.audio_io.process_mic_audio)
        self.audio_thread.start()

        # Start audio streams (mic and speaker)
        self.audio_io.start_streams()

    def send_audio_to_socket(self, mic_chunk):
        """ Callback function to send audio data to the socket. """
        logging.info(f'🎤 Sending {len(mic_chunk)} bytes of audio data to socket.')
        encoded_chunk = base64.b64encode(mic_chunk).decode('utf-8')
        self.socket.send({'type': 'input_audio_buffer.append', 'audio': encoded_chunk})

    def handle_message(self, message):
        """ Handle incoming WebSocket messages. """
        event_type = message.get('type')
        logging.info(f'Received message type: {event_type}')

        if event_type == 'response.audio.delta':
            audio_content = base64.b64decode(message['delta'])
            self.audio_io.receive_audio(audio_content)
            logging.info(f'Received {len(audio_content)} bytes of audio data.')

        elif event_type == 'response.audio.done':
            logging.info('AI finished speaking.')

    def stop(self):
        """ Stop all processes cleanly. """
        logging.info('Shutting down Realtime session.')

        # Signal threads to stop
        self.audio_io._stop_event.set()
        self.socket.kill()

        # Stop audio streams
        self.audio_io.stop_streams()

        # Join threads to ensure they exit cleanly
        if self.audio_thread:
            self.audio_thread.join()
            logging.info('Audio processing thread terminated.')