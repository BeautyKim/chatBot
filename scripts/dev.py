import socket
import subprocess
import sys
import os

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('0.0.0.0', port)) == 0

def find_available_port(start_port=8080, max_attempts=10):
    for port in range(start_port, start_port + max_attempts):
        if not is_port_in_use(port):
            return port
    return None

def start_server():
    port = find_available_port()
    if port is None:
        print("❌ 가용한 포트를 찾을 수 없습니다.")
        sys.exit(1)
    
    print(f"🚀 {port} 포트가 비어있어 서버를 실행합니다...")
    
    # .venv 내의 uvicorn 경로 확인
    venv_uvicorn = os.path.join(".venv", "bin", "uvicorn")
    cmd = [
        venv_uvicorn if os.path.exists(venv_uvicorn) else "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", str(port),
        "--reload"
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 서버를 종료합니다.")
        sys.exit(0)

if __name__ == "__main__":
    start_server()
