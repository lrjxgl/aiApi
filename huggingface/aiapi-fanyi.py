import time
import requests
from io import BytesIO
import base64
import os
import taskcheck
import serviceConf
import platform
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

tokenizer_zh2en = AutoTokenizer.from_pretrained("G:/model/Helsinki-NLP/opus-mt-zh-en")
model_zh2en = AutoModelForSeq2SeqLM.from_pretrained("G:/model/Helsinki-NLP/opus-mt-zh-en")
tokenizer_en2zh = AutoTokenizer.from_pretrained("G:/model/Helsinki-NLP/opus-mt-en-zh")
model_en2zh = AutoModelForSeq2SeqLM.from_pretrained("G:/model/Helsinki-NLP/opus-mt-en-zh")

def zh2en(text):
    tokenized_text = tokenizer_zh2en([text], return_tensors='pt')
    translation = model_zh2en.generate(**tokenized_text, max_new_tokens=1024)
    return tokenizer_zh2en.batch_decode(translation, skip_special_tokens=True)[0]
def en2zh(text):
    tokenized_text = tokenizer_en2zh([text], return_tensors='pt')
    translation = model_en2zh.generate(**tokenized_text, max_new_tokens=1024)
    return tokenizer_en2zh.batch_decode(translation, skip_special_tokens=True)[0]
#接口
queueKey="aiapi_fanyi_create"
serviceId=serviceConf.serviceId
serviceToken=serviceConf.serviceToken
apiurl =serviceConf.apiHost+"/module.php?m=aiapi_fanyi&serviceId="+serviceId+"&serviceToken="+serviceToken+"&queueKey="+queueKey
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
            content=""
            if task["action"]=="zh2en":
                content = zh2en(task["prompt"])
                
            elif task["action"]=="en2zh":
                content = en2zh(task["prompt"])
            ##发布回复
            print(content)
            taskcheck.removeTask()
            url = apiurl+'&a=finish'
            rdata = task
            rdata["content"] = content
            
            response = requests.post(url, data=rdata)
            print("生成成功")

            # print(res)

    except requests.exceptions.RequestException as e:
        print(e)
        taskcheck.removeTask()
        time.sleep(5)
