import threading
import pyaudio
import queue
import base64
import json
import os
import time
from websocket import create_connection, WebSocketConnectionClosedException
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

load_dotenv()

CHUNK_SIZE = 1024
RATE = 24000
FORMAT = pyaudio.paInt16
REENGAGE_DELAY_MS = 500


class Socket:
    def __init__(self, api_key, ws_url):
        self.api_key = api_key
        self.ws_url = ws_url
        self.ws = None
        self.on_msg = None
        self._stop_event = threading.Event()
        self.recv_thread = None
        self.lock = threading.Lock()

    def connect(self):
        self.ws = create_connection(self.ws_url, header=[f'Authorization: Bearer {self.api_key}', 'OpenAI-Beta: realtime=v1'])
        logging.info('Connected to WebSocket.')
        self.recv_thread = threading.Thread(target=self._receive_messages)
        self.recv_thread.start()

    def _receive_messages(self):
        while not self._stop_event.is_set():
            try:
                message = self.ws.recv()
                if message and self.on_msg:
                    self.on_msg(json.loads(message))
            except WebSocketConnectionClosedException:
                logging.error('WebSocket connection closed.')
                break
            except Exception as e:
                logging.error(f'Error receiving message: {e}')
        logging.info('Exiting WebSocket receiving thread.')

    def send(self, data):
        try:
            with self.lock:
                if self.ws:
                    self.ws.send(json.dumps(data))
        except WebSocketConnectionClosedException:
            logging.error('WebSocket connection closed.')
        except Exception as e:
            logging.error(f'Error sending message: {e}')

    def kill(self):
        self._stop_event.set()
        if self.ws:
            try:
                self.ws.send_close()
                self.ws.close()
                logging.info('WebSocket connection closed.')
            except Exception as e:
                logging.error(f'Error closing WebSocket: {e}')
        if self.recv_thread:
            self.recv_thread.join()

class AudioIO:
    def __init__(self, chunk_size=CHUNK_SIZE, rate=RATE, format=FORMAT):
        self.chunk_size = chunk_size
        self.rate = rate
        self.format = format
        self.audio_buffer = bytearray()
        self.mic_queue = queue.Queue()
        self.mic_on_at = 0
        self.mic_active = None
        self._stop_event = threading.Event()
        self.p = pyaudio.PyAudio()

    def _mic_callback(self, in_data, frame_count, time_info, status):
        if time.time() > self.mic_on_at:
            if not self.mic_active:
                logging.info('🎙️🟢 Mic active')
                self.mic_active = True
            self.mic_queue.put(in_data)
        else:
            if self.mic_active:
                logging.info('🎙️🔴 Mic suppressed')
                self.mic_active = False
        return (None, pyaudio.paContinue)

    def _spkr_callback(self, in_data, frame_count, time_info, status):
        bytes_needed = frame_count * 2
        current_buffer_size = len(self.audio_buffer)

        if current_buffer_size >= bytes_needed:
            audio_chunk = bytes(self.audio_buffer[:bytes_needed])
            self.audio_buffer = self.audio_buffer[bytes_needed:]
            self.mic_on_at = time.time() + REENGAGE_DELAY_MS / 1000
        else:
            audio_chunk = bytes(self.audio_buffer) + b'\x00' * (bytes_needed - current_buffer_size)
            self.audio_buffer.clear()

        return (audio_chunk, pyaudio.paContinue)

    def start_streams(self):
        self.mic_stream = self.p.open(
            format=self.format,
            channels=1,
            rate=self.rate,
            input=True,
            stream_callback=self._mic_callback,
            frames_per_buffer=self.chunk_size
        )
        self.spkr_stream = self.p.open(
            format=self.format,
            channels=1,
            rate=self.rate,
            output=True,
            stream_callback=self._spkr_callback,
            frames_per_buffer=self.chunk_size
        )
        self.mic_stream.start_stream()
        self.spkr_stream.start_stream()

    def stop_streams(self):
        self.mic_stream.stop_stream()
        self.mic_stream.close()
        self.spkr_stream.stop_stream()
        self.spkr_stream.close()
        self.p.terminate()

    def send_mic_audio(self, socket):
        while not self._stop_event.is_set():
            if not self.mic_queue.empty():
                mic_chunk = self.mic_queue.get()
                logging.info(f'🎤 Sending {len(mic_chunk)} bytes of audio data.')
                encoded_chunk = base64.b64encode(mic_chunk).decode('utf-8')
                socket.send({'type': 'input_audio_buffer.append', 'audio': encoded_chunk})

    def receive_audio(self, audio_chunk):
        self.audio_buffer.extend(audio_chunk)


class Realtime:
    def __init__(self, api_key, ws_url):
        self.socket = Socket(api_key, ws_url)
        self.audio_io = AudioIO()

    def start(self):
        self.socket.on_msg = self.handle_message
        self.socket.connect()

        # Still works if we omit this, just doesn't speak to us first.
        self.socket.send({
            'type': 'response.create',
            'response': {
                'modalities': ['audio', 'text'],
                'instructions': 'Please assist the user.'
            }
        })

        audio_send_thread = threading.Thread(target=self.audio_io.send_mic_audio, args=(self.socket,))
        audio_send_thread.start()

        self.audio_io.start_streams()

    def handle_message(self, message):
        event_type = message.get('type')
        logging.info(f'Received message type: {event_type}')

        if event_type == 'response.audio.delta':
            audio_content = base64.b64decode(message['delta'])
            self.audio_io.receive_audio(audio_content)
            logging.info(f'Received {len(audio_content)} bytes of audio data.')

        elif event_type == 'response.audio.done':
            logging.info('AI finished speaking.')

    def stop(self):
        logging.info('Shutting down Realtime session.')
        self.audio_io.stop_streams()
        self.socket.kill()


def main():
    api_key = os.getenv('OPENAI_API_KEY')
    ws_url = 'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01'

    realtime = Realtime(api_key, ws_url)

    try:
        realtime.start()
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        logging.info('Gracefully shutting down...')
        realtime.stop()


if __name__ == '__main__':
    main()