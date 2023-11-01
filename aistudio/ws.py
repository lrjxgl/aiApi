import json
import wss
ws=wss.wsInit()
wsData={
        "type":"say",
        "taskAction":"text2text-task",
        "content":"hello",
        "wsclient_to":"hello",
        "taskid":1
}
wss.wsSend(ws,json.dumps(wsData))
    
ws.close()