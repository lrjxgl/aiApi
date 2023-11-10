import time
import requests
import taskcheck
import serviceConf
from io import BytesIO
import base64
import os
import platform
from modelscope import (
    snapshot_download, AutoModelForCausalLM, AutoTokenizer, GenerationConfig
)
from auto_gptq import AutoGPTQForCausalLM
model_dir="/mnt/workspace/.cache/modelscope/qwen/Qwen-VL-Chat-Int4"
#model_dir = snapshot_download(mdir, revision='v1.0.0')

import torch
torch.manual_seed(1234)

# Note: The default behavior now has injection attack prevention off.
tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)

# use cuda device
model = AutoModelForCausalLM.from_pretrained(model_dir, device_map="cuda", trust_remote_code=True,use_safetensors=True).eval()
#系统
queueKey="aiapi_img2text_create"
serviceId=serviceConf.serviceId
serviceToken=serviceConf.serviceToken
apiurl =serviceConf.apiHost+"/module.php?m=aiapi_img2text&serviceId="+serviceId+"&serviceToken="+serviceToken+"&queueKey="+queueKey
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
            print("还没任务")
            taskcheck.removeTask();
            time.sleep(3)

        else:
             
            task = res["data"]
            a=1
            if a==1 :
                history=task["history"] 
                prompt = task["prompt"]
                
                try: 
                    image_path=task["imgurl"] 
                except: 
                    image_path = ""

                # 处理
                query = tokenizer.from_list_format([
                    {'image': image_path},
                    {'text': prompt},
                ])
                response, history = model.chat(tokenizer, query=query, history=None)
               
                #全部生成完    
     
                apiTime=serviceConf.apiTime();
                apiAccess=serviceConf.serviceAccess(serviceConf.serviceToken,apiTime)
                url = apiurl + '&a=finish&apiTime='+apiTime+"&apiAccess="+apiAccess
                rdata = task
               
                rdata["content"] = response
                rdata["history"]= history
                taskcheck.removeTask();
                response = requests.post(url, data=rdata)
                print("生成成功") 
            else:
                taskcheck.removeTask();
        
                #time.sleep(10)
            # print(res)

    except requests.exceptions.RequestException as e:
        print(e)
        taskcheck.removeTask();
        time.sleep(5)
