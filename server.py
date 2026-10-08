"""Run with python3 server.py, then visit http://localhost:8000."""
import argparse
import json
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from zoneinfo import ZoneInfo
from chatbot import FAQBot, countdown

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / 'data/faqs.json').read_text())
BOT = FAQBot(DATA)


def today():
    return datetime.now(ZoneInfo(DATA['timezone'])).date()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / 'static'), **kwargs)

    def send_json(self, payload, status=200):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/api/calendar':
            self.send_json({'today': today().isoformat(), 'timezone': DATA['timezone'], 'events': [countdown(event, today()) for event in DATA['events'].values()]})
        else:
            super().do_GET()

    def do_POST(self):
        if self.path != '/api/chat':
            self.send_json({'error': 'Unknown endpoint.'}, 404)
            return
        try:
            length = int(self.headers.get('Content-Length', 0))
            if not 0 < length <= 4096:
                raise ValueError('Invalid request size.')
            payload = json.loads(self.rfile.read(length))
            question = payload.get('question') if isinstance(payload, dict) else None
            if not isinstance(question, str) or not question.strip() or len(question) > 500:
                raise ValueError('Enter a question between 1 and 500 characters.')
            self.send_json(BOT.answer(question.strip(), today()))
        except (ValueError, TypeError) as error:
            self.send_json({'error': str(error)}, 400)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    print(f'Clarivo: http://localhost:{args.port} (Ctrl+C to stop)')
    ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()
