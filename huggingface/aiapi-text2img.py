import requests
import time
from diffusers import StableDiffusionPipeline
import torch
import cv2
from PIL import Image
import base64
from io import BytesIO
import os
import platform
import taskcheck
import serviceConf
os_name = platform.system()
clear_command = 'cls' if os_name == 'Windows' else 'clear'
 
queueKey="aiapi_text2img_create"
serviceId=serviceConf.serviceId
serviceToken=serviceConf.serviceToken
apiurl =serviceConf.apiHost+"/module.php?m=aiapi_text2img&serviceId="+serviceId+"&serviceToken="+serviceToken+"&queueKey="+queueKey
root="G:/model/"
#model_id =root+ "andite/anything-v4.0"
model_id = root+"openjourney-v4"
pipe = StableDiffusionPipeline.from_pretrained(
    model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda")
while True:
    try:
        t=taskcheck.canTask()
        if t==False:
            print('执行其它任务');
            time.sleep(1)
            continue
        taskcheck.addTask()    
        apiTime=serviceConf.apiTime();
        apiAccess=serviceConf.serviceAccess(serviceConf.serviceToken,apiTime)
        url = apiurl + '&a=get&apiTime='+apiTime+"&apiAccess="+apiAccess
        
        response = requests.get(url, timeout=30)
        res = response.json()
        if res["error"] == 1:
            taskcheck.removeTask();
            print("还没任务")
            
            time.sleep(3)
            os.system(clear_command)

        else:
            
            task = res["data"]            
            prompt = task["prompt_en"]
           
            #output = pipe({'text': prompt})
            #image = output['output_imgs'][0]
            width=task["width"]
            height=task["height"]
            num_inference_steps=task["num_inference_steps"]
            inputText={
                'text':prompt,
                'width':width,
                'height':height,
                'num_inference_steps': num_inference_steps,
                'Sampler': 'DPM++ 2M Karras',
                'guidance_scale': 7,
                'negative_prompt':'Fuzzy'
            }
            image = pipe(
                prompt,
                num_inference_steps=num_inference_steps,
                width=width,
                height=height,
                guidance_scale=7.5,
                negative_prompt=''
            ).images[0]
            
            t = time.time()
            imgurl="./static/text2img.png"
            #cv2.imwrite(f, image)
            image.save(imgurl)
            
             
            apiTime=serviceConf.apiTime();
            apiAccess=serviceConf.serviceAccess(serviceConf.serviceToken,apiTime)
            url = apiurl + '&a=finish&apiTime='+apiTime+"&apiAccess="+apiAccess
            rdata = task
            with open(imgurl,'rb') as f:
                    con=f.read()
                    rdata["image64"]=base64.b64encode(con).decode('utf-8')
            
            taskcheck.removeTask();
            response = requests.post(url, data=rdata)
            print("生成成功")
            time.sleep(3)
            os.system(clear_command)
            # print(res)

    except requests.exceptions.RequestException as e:
        print(e)
        taskcheck.removeTask();
        time.sleep(5)
