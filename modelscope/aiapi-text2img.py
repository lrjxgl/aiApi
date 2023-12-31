import torch.cuda as cuda
import requests
import urllib.parse
import time
from modelscope.utils.constant import Tasks
#from modelscope.pipelines import pipeline
from diffusers import StableDiffusionXLPipeline
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
#pipe = pipeline(task=Tasks.text_to_image_synthesis, 
#                model='AI-ModelScope/stable-diffusion-xl-base-1.0',
#                use_safetensors=False,
#                model_revision='v1.0.0')

mdir="/mnt/workspace/.cache/modelscope/AI-ModelScope/stable-diffusion-xl-base-1.0"
pipe = StableDiffusionXLPipeline.from_pretrained(
    mdir, torch_dtype=torch.float16, variant="fp16", use_safetensors=True
)
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
            print("text2img还没任务")
            
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
            picnum=task["picnum"]
            inputText={
                'text':prompt,
                'width':width,
                'height':height,
                'num_inference_steps': num_inference_steps,
                'Sampler': 'DPM++ 2M Karras',
                'guidance_scale': 7,
                'negative_prompt':'Fuzzy'
            }
             
            imgList=[]
            for i in range(picnum):
                image = pipe(
                    prompt,
                    num_inference_steps=num_inference_steps,
                    width=width,
                    height=height,
                    guidance_scale=7.5,
                    negative_prompt='Fuzzy'
                ).images[0]
                #解除cuda占用
                cuda.empty_cache()
                t = time.time()
                imgurl="./static/text2img.png" 
                 
                image.save(imgurl)
                with open(imgurl,'rb') as f:
                    con=f.read()
                    imgList.append(base64.b64encode(con).decode('utf-8'))
                
            
            
            apiTime=serviceConf.apiTime();
            apiAccess=serviceConf.serviceAccess(serviceConf.serviceToken,apiTime)
            url = apiurl + '&a=finish&apiTime='+apiTime+"&apiAccess="+apiAccess
            rdata = task
            rdata["imgList"]=imgList
            
            taskcheck.removeTask()
            headers = {'Content-Type': 'application/json'} 
            response = requests.post(url,headers=headers,json=rdata )
            print("生成成功")
            print(response.text)
            
            time.sleep(3)
            os.system(clear_command)
            # print(res)

    except requests.exceptions.RequestException as e:
        print(e)
        taskcheck.removeTask();
        time.sleep(5)
