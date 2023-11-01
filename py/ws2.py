import websocket
import json
import threading
import time
def on_message(ws, message):
    print(f"Received: {message}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws):
    print("Connection closed")

def on_open(ws):
    print("Connection opened")
    wsData={
            "type":"login",
            "k":"hello"
        }
    ws.send(json.dumps(wsData))
    def run(*args):
        while True:
            time.sleep(5)
            try:
                ws.send("Hello, Server")
                print("ping");
            except WebSocketConnectionClosedException:
                break
    threading.Thread(target=run).start()
def isConnect(ws):
    try:
        ws.send("ping")
        return True
    except websocket._exceptions.WebSocketConnectionClosedException:
        
        time.sleep(1)
        return False
def wsinit():
    ws = websocket.WebSocketApp(
        "wss://wss.deituicms.com:8282",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.on_open = on_open
    return ws 