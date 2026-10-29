import uvicorn
from .config import HTTP_HOST, HTTP_PORT

def main():
    print(f"[ESP32] Starting Web Server on http://{HTTP_HOST}:{HTTP_PORT}")
    uvicorn.run("virtual_esp32.server:app", host=HTTP_HOST, port=HTTP_PORT, reload=False)

if __name__ == "__main__":
    main()
