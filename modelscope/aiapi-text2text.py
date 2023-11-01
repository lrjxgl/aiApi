import time
import requests
from io import BytesIO
import base64
import os
import taskcheck
import serviceConf
import platform
import wss
import json

 
'''
from modelscope import AutoTokenizer, AutoModelForCausalLM, snapshot_download

model_dir = snapshot_download("qwen/Qwen-7B-Chat-Int4", revision = 'v1.1.0' )

# Note: The default behavior now has injection attack prevention off.
tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)

model = AutoModelForCausalLM.from_pretrained(
    model_dir,
    device_map="auto",
    trust_remote_code=True
).eval()'''
#chatglm
from modelscope import AutoTokenizer, AutoModel
tokenizer = AutoTokenizer.from_pretrained("ZhipuAI/chatglm2-6b-int4", trust_remote_code=True)
model = AutoModel.from_pretrained("ZhipuAI/chatglm2-6b-int4", trust_remote_code=True).half().cuda()
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
        t=taskcheck.canTask()
        if t==False:
            print('执行其它任务');
            time.sleep(1)
            continue;
        taskcheck.addTask()    
        apiTime=serviceConf.apiTime();
        apiAccess=serviceConf.serviceAccess(serviceConf.serviceToken,apiTime)
        url = apiurl + '&a=get&apiTime='+apiTime+"&apiAccess="+apiAccess
        response = requests.get(url, timeout=30)
         
        res = response.json()
        print(res)
        if res["error"] == 1:
            taskcheck.removeTask();
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
                    ws=wss.wsInit()
                    for content, history in model.stream_chat(tokenizer, prompt, history):
                        wsData={
                            "type":"say",
                            "taskAction":"text2text-task",
                            "content":content,
                            "wsclient_to":task["wsclient_to"],
                            "taskid":task["taskid"]
                        }
                        wss.wsSend(ws,json.dumps(wsData))
                    ws.close()
                else:
                    content, history = model.chat(tokenizer, prompt, task["history"])
                #history.append((prompt,content))
                if "create_title" in task and task["create_title"]==1:
                    prompt2="给下面这篇文章取一个标题："+content                 
                    title, history = model.chat(tokenizer, prompt2, history=history)
                if "create_description" in task and task["create_description"]==1:
                    prompt="给下面这篇文章生成简介："+content
                    description,history= model.chat(tokenizer, prompt, history=history)
                ##发布回复
                
                apiTime=serviceConf.apiTime();
                apiAccess=serviceConf.serviceAccess(serviceConf.serviceToken,apiTime)
                url = apiurl + '&a=finish&apiTime='+apiTime+"&apiAccess="+apiAccess
                rdata = task
                rdata["content"] = content
                rdata["title"]= title
                rdata["description"]=description
                taskcheck.removeTask();
                response = requests.post(url, data=rdata)
                print("生成成功")

            # print(res)

    except requests.exceptions.RequestException as e:
        print(e)
        taskcheck.removeTask();
        time.sleep(5)
