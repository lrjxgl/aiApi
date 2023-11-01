import time
import requests
from io import BytesIO
import base64
import os
import platform
import taskcheck
from urllib import request
#model
from paddlespeech.cli.asr.infer import ASRExecutor

asr = ASRExecutor()

#接口
queueKey="aiapi_audio2text_create"
serviceId="10000002"
serviceToken="0e34e7713bb5721bd34dd2bc886f1788";
apiurl = "http://aiapi.deituicms.com/module.php?m=aiapi_audio2text&serviceId="+serviceId+"&serviceToken="+serviceToken+"&queueKey="+queueKey
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
            if  a==1:
                mp3url = task["mp3url"]
                audio="./static/audio2text.mp3"
                request.urlretrieve(mp3url, audio)
                content = asr(audio_file=audio, model='conformer_online_wenetspeech')
                
                ##发布回复
                url = apiurl+'&a=finish'
                rdata = task
                rdata["content"]=content
                taskcheck.removeTask();
                response = requests.post(url, data=rdata)

                print("生成成功")
            else:    
                taskcheck.removeTask();
            # print(res)

    except requests.exceptions.RequestException as e:
        print(e)
        time.sleep(1)
