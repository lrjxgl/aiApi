import time
import requests
from io import BytesIO
import base64
import os
import platform
import json
import wss

#模型开始
from paddlenlp.transformers import AutoTokenizer, AutoModelForCausalLM
tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b-int4",use_fast=True)
model = AutoModelForCausalLM.from_pretrained("THUDM/chatglm-6b-int4", dtype="float16")
def prepare_query_for_chat(query: str, history = None):
    if history is None:
        return query
    else:
        prompt = ""
        for i, (old_query, response) in enumerate(history):
            prompt += "[Round {}]\n问：{}\n答：{}\n".format(i, old_query, response)
        prompt += "[Round {}]\n问：{}\n答：".format(len(history), query)
    return prompt
def model_chat(query:str,history=None):
    prompt=prepare_query_for_chat(query, history) 
    input_features = tokenizer(prompt, return_tensors="pd")
    outputs = model.generate(**input_features, max_new_token=4096,max_length=2048)
    answer=tokenizer.batch_decode(outputs[0])  
    return answer
#模型结束
queueKey="aiapi_text2text_create"
serviceId="10000002"
serviceToken="0e34e7713bb5721bd34dd2bc886f1788";
apiurl = "http://aiapi.deituicms.com/module.php?m=aiapi_text2text&serviceId="+serviceId+"&serviceToken="+serviceToken+"&queueKey="+queueKey
os_name = platform.system()
clear_command = 'cls' if os_name == 'Windows' else 'clear'
#载入模型

while True:
    try:
        url = apiurl + '&a=get'
        print(url)
        response = requests.get(url, timeout=2)
         
        res = response.json()
        print(res)
        if res["error"] == 1:
            print("还没任务")
            #model_chat("你是谁呢",None)
            time.sleep(3)


        else:
            task = res["data"]
            a=1
            if a==1 :
                #paddle.seed(5232132133)
                query = task["prompt"]
                history=task["history"] 
                content =model_chat(query,history)
                history.append((query,content))
                title=""
                if "create_title" in task and task["create_title"]==1:
                    prompt2="帮我给这篇文章取一个标题，只要提供一个标题就行,不要出现引号或者双引号"
                    title = model_chat(prompt2,history)
                description=""
                if "create_description" in task and task["create_description"]==True:
                    prompt2="帮我给这篇文章做一个100字以内的介绍。"
                    description = model_chat(prompt2,history)
                ##发布回复
                url = apiurl+'&a=finish'
                rdata = task
                rdata["content"] = content
                rdata["title"]= title
                rdata["description"]=description
                print(content)
                #ws发送
                '''
                if 'stream' in task and task["stream"]==1:
                    ws=wss.wsInit()
                    wsData={
                            "type":"say",
                            "taskAction":"text2text-task",
                            "content":content,
                            "wsclient_to":task["wsclient_to"],
                            "uTask":task["uTask"],
                            "taskid":task["taskid"]
                    }
                    wss.wsSend(ws,json.dumps(wsData))
                        
                    ws.close()
                '''
                response = requests.post(url, data=rdata)
                print("生成成功")
                #time.sleep(10)
            # print(res)
            
            # print(res)

    except requests.exceptions.RequestException as e:
        print(e)
        time.sleep(1)
