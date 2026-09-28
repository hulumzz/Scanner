import ctypes
import os
import secrets
import socket
import sys
import threading
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import uvicorn
import webview

HOST = '127.0.0.1'
STARTUP_TIMEOUT_SECONDS = 25


def _data_root() -> Path:
    local_app_data = os.environ.get('LOCALAPPDATA')
    if local_app_data:
        root = Path(local_app_data) / 'KKScanner'
    else:
        root = Path.home() / '.kk_scanner'
    root.mkdir(parents=True, exist_ok=True)
    return root


def _load_or_create_secret(root: Path) -> str:
    secret_file = root / 'session.secret'
    if secret_file.exists():
        value = secret_file.read_text(encoding='utf-8').strip()
        if value:
            return value

    value = secrets.token_urlsafe(64)
    secret_file.write_text(value, encoding='utf-8')
    return value


def _configure_environment(root: Path) -> None:
    database_file = root / 'kk_scanner.db'
    webview_data = root / 'webview'
    webview_data.mkdir(parents=True, exist_ok=True)

    os.environ['APP_ENV'] = 'desktop'
    os.environ['DESKTOP_AUTO_LOGIN'] = 'true'
    os.environ['DATABASE_URL'] = f"sqlite:///{database_file.as_posix()}"
    os.environ['SECRET_KEY'] = _load_or_create_secret(root)
    os.environ.setdefault('ENABLE_VISION_FALLBACK', 'false')


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, 0))
        return int(sock.getsockname()[1])


class ScannerServer(threading.Thread):
    def __init__(self, port: int):
        super().__init__(name='kk-scanner-server', daemon=True)
        self.port = port
        self.server: uvicorn.Server | None = None
        self.error: Exception | None = None

    def run(self) -> None:
        try:
            from app.main import app

            config = uvicorn.Config(
                app=app,
                host=HOST,
                port=self.port,
                log_level='warning',
                access_log=False,
            )
            self.server = uvicorn.Server(config)
            self.server.run()
        except Exception as exc:
            self.error = exc

    def stop(self) -> None:
        if self.server is not None:
            self.server.should_exit = True


def _wait_until_ready(server: ScannerServer) -> bool:
    deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
    health_url = f'http://{HOST}:{server.port}/healthz'

    while time.monotonic() < deadline:
        if server.error is not None:
            return False
        try:
            with urlopen(health_url, timeout=1) as response:
                if response.status == 200:
                    return True
        except (URLError, TimeoutError, OSError):
            pass
        time.sleep(0.2)

    return False


def _show_error(message: str) -> None:
    if sys.platform == 'win32':
        ctypes.windll.user32.MessageBoxW(0, message, 'KK Scanner', 0x10)
    else:
        print(message, file=sys.stderr)


def main() -> int:
    root = _data_root()
    _configure_environment(root)

    port = _find_free_port()
    server = ScannerServer(port)
    server.start()

    if not _wait_until_ready(server):
        server.stop()
        details = f'\n\nDetail: {server.error}' if server.error else ''
        _show_error(
            'Server lokal KK Scanner gagal dijalankan. '
            'Silakan tutup aplikasi lalu coba kembali.' + details
        )
        return 1

    webview.settings['ALLOW_DOWNLOADS'] = True
    webview.settings['OPEN_EXTERNAL_LINKS_IN_BROWSER'] = True

    webview.create_window(
        'KK Scanner',
        f'http://{HOST}:{port}/',
        width=1366,
        height=820,
        min_size=(1024, 650),
        resizable=True,
        text_select=True,
        background_color='#F7F8FA',
    )

    try:
        webview.start(
            debug=False,
            private_mode=False,
            storage_path=str(root / 'webview'),
        )
    finally:
        server.stop()
        server.join(timeout=10)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
