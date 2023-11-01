import time
import requests
from io import BytesIO
import base64
import os
import platform
#模型开始
import paddle
#from ppdiffusers import StableDiffusionPipeline
from ppdiffusers import StableDiffusionXLPipeline
#pipe = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-2",paddle_dtype=paddle.float16) 
pipe = StableDiffusionXLPipeline.from_pretrained(
     "stabilityai/stable-diffusion-xl-base-1.0",
     paddle_dtype=paddle.float16,
     variant="fp16"
)
#模型结束
queueKey="aiapi_text2img_create"
serviceId="10000002"
serviceToken="0e34e7713bb5721bd34dd2bc886f1788";
apiurl = "http://aiapi.deituicms.com/module.php?m=aiapi_text2img&serviceId="+serviceId+"&serviceToken="+serviceToken+"&queueKey="+queueKey
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
            prompt=task["prompt_en"]
            a=1
            if a==1 :
                num_inference_steps=task["num_inference_steps"]
                image = pipe(prompt, guidance_scale=7.5, width=1024, height=1024,num_inference_steps=num_inference_steps).images[0]
                image.save("static/text2img.png")
                ##发布回复
                url = apiurl+'&a=finish'
                rdata = task
                with open("static/text2img.png",'rb') as f:
                    con=f.read()
                    rdata["image64"]=base64.b64encode(con).decode('utf-8')
                response = requests.post(url, data=rdata)
                print("生成成功")
                #time.sleep(10)
            # print(res)
            
            # print(res)

    except requests.exceptions.RequestException as e:
        print(e)
        time.sleep(1)
