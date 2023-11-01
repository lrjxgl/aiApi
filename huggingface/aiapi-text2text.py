import time
import requests
from io import BytesIO
import base64
import os
import platform
import taskcheck
import serviceConf
import wss
import json
ws=wss.wsinit()

from transformers import AutoTokenizer, AutoModel
tokenizer = AutoTokenizer.from_pretrained(r"G:\model\THUDM\chatglm-6b-int4", trust_remote_code=True)
model = AutoModel.from_pretrained(r"G:\model\THUDM\chatglm-6b-int4", trust_remote_code=True).half().cuda()
model = model.eval() 
#接口
queueKey="aiapi_text2text_create"
serviceId=serviceConf.serviceId
serviceToken=serviceConf.serviceToken
apiurl =serviceConf.apiHost+"/module.php?m=aiapi_text2text&serviceId="+serviceId+"&serviceToken="+serviceToken+"&queueKey="+queueKey
os_name = platform.system()
clear_command = 'cls' if os_name == 'Windows' else 'clear'
#载入模型

while True:
    try:
        url = apiurl + '&a=get'
        response = requests.get(url, timeout=2)
         
        res = response.json()
        print(res)
        if res["error"] == 1:
            print("还没任务")
            time.sleep(3)

        else:
            task = res["data"]
            a=1
            if a==1:
                history=task["history"]
                prompt = task["prompt"]
                inputs = {'text':prompt, 'history': []}
                title=''
                description=''
                content=''
                #result = pipe(inputs)
                
                if 'stream' in task and task["stream"]==1:
                    for content, history in model.stream_chat(tokenizer, prompt, history):
                        wsData={
                            "type":"text2text-task",
                            "content":content,
                            "wsclient_to":task["wsclient_to"]
                        }
                        ws.send(json.dumps(wsData))
                else:
                    content, history = model.chat(tokenizer, prompt, task["history"])
                #history.append((prompt,content))
                if 'title' in task:
                    prompt2="给下面这篇文章取一个标题："+content                 
                    title, history = model.chat(tokenizer, prompt2, history=history)
                if 'description' in task:
                    prompt="给下面这篇文章生成简介："+content
                    description,history= model.chat(tokenizer, prompt, history=history)
                ##发布回复
                url = apiurl+'&a=finish'
                rdata = task
                rdata["content"] = content
                rdata["title"]= title
                rdata["description"]=description
                taskcheck.removeTask();
                response = requests.post(url, data=rdata)
            
                #time.sleep(10)
            # print(res)

    except requests.exceptions.RequestException as e:
        print(e)
        time.sleep(1)
