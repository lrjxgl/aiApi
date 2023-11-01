import websocket
from websocket import create_connection
import json
def wsInit():
    ws = create_connection("wss://wss.deituicms.com:8282")
    wsData={
            "type":"login",
            "k":"aiapi"
    }
    ws.send(json.dumps(wsData))
    return ws
def wsSend(ws,data):
    try:
        ws.send(data)
        print(data)
        print("发送成功")
        return True
    except websocket._exceptions.WebSocketConnectionClosedException:
        print("发送失败")
        return False
def wsClose(ws):
    ws.close()