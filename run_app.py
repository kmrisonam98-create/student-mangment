import os
import sys
import time
import urllib.request
import webbrowser
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
API_HOST = "127.0.0.1"
API_PORT = 8000
STREAMLIT_PORT = 8501


def find_python():
    venv_python = ROOT / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def is_port_available(port: int):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("127.0.0.1", port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def wait_for_url(url: str, timeout: int = 30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2):
                return True
        except Exception:
            time.sleep(0.5)
    return False


def main():
    if not is_port_available(API_PORT) or not is_port_available(STREAMLIT_PORT):
        print(f"Port {API_PORT} or {STREAMLIT_PORT} is already in use. Stop the running app and try again.")
        return 1

    python_exe = find_python()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)

    api_proc = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "api:app", "--host", API_HOST, "--port", str(API_PORT)],
        cwd=str(ROOT),
        env=env,
    )

    api_ready = wait_for_url(f"http://{API_HOST}:{API_PORT}/docs")
    if not api_ready:
        print("FastAPI did not start successfully.")
        api_proc.terminate()
        return 1

    streamlit_proc = subprocess.Popen(
        [python_exe, "-m", "streamlit", "run", "app.py", "--server.address", API_HOST, "--server.port", str(STREAMLIT_PORT)],
        cwd=str(ROOT),
        env=env,
    )

    streamlit_ready = wait_for_url(f"http://{API_HOST}:{STREAMLIT_PORT}/")
    if not streamlit_ready:
        print("Streamlit did not start successfully.")
        api_proc.terminate()
        streamlit_proc.terminate()
        return 1

    print("\nProject is running successfully!")
    print(f"API Docs: http://{API_HOST}:{API_PORT}/docs")
    print(f"Student App: http://{API_HOST}:{STREAMLIT_PORT}")

    try:
        webbrowser.open(f"http://{API_HOST}:{STREAMLIT_PORT}")
    except Exception:
        pass

    try:
        while True:
            if api_proc.poll() is not None or streamlit_proc.poll() is not None:
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping project...")

    api_proc.terminate()
    streamlit_proc.terminate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
