import time
import requests
from io import BytesIO
import base64
import os
import platform
import taskcheck
#model
from paddlespeech.cli.tts.infer import TTSExecutor
model = TTSExecutor()
#接口
queueKey="aiapi_tts_create"
serviceId="10000002"
serviceToken="0e34e7713bb5721bd34dd2bc886f1788";
apiurl = "http://aiapi.deituicms.com/module.php?m=aiapi_tts&serviceId="+serviceId+"&serviceToken="+serviceToken+"&queueKey="+queueKey
os_name = platform.system()
clear_command = 'cls' if os_name == 'Windows' else 'clear'
#载入模型

while True:
    try:
        t=taskcheck.canTask()
        if t==False:
            print('执行其它任务');
            time.sleep(1)
            continue;
        taskcheck.addTask()    
        url = apiurl + '&a=get'
        response = requests.get(url, timeout=5)
         
        res = response.json()
        print(res)
        if res["error"] == 1:
            taskcheck.removeTask();
            print("还没任务")
            time.sleep(3)

        else:
            
            task = res["data"]
            a=1;
            if task["action"]=='create_tts' or  a==1:
                mp3url="static/aiapi-tts.mp3"
                model(text=task["prompt"], output=mp3url)
                ##发布回复
                url = apiurl+'&a=finish'
                rdata = task
                with open(mp3url,'rb') as f:
                    con=f.read()
                    rdata["base64"]=base64.b64encode(con).decode('utf-8')
                taskcheck.removeTask();
                response = requests.post(url, data=rdata)

                print("生成成功")
            else:    
                taskcheck.removeTask();
            # print(res)

    except requests.exceptions.RequestException as e:
        print(e)
        time.sleep(1)
