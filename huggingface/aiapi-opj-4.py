import requests
import time
from diffusers import StableDiffusionPipeline
import torch
import base64
from io import BytesIO
import os
import platform
import taskcheck
import serviceConf
os_name = platform.system()
clear_command = 'cls' if os_name == 'Windows' else 'clear'
#接口
queueKey="aiapi_text2img_create"
serviceId=serviceConf.serviceId
serviceToken=serviceConf.serviceToken
apiurl =serviceConf.apiHost+"/module.php?m=aiapi_text2img&serviceId="+serviceId+"&serviceToken="+serviceToken+"&queueKey="+queueKey

root="G:/model/"
model_id = root+"openjourney-v4"
pipe = StableDiffusionPipeline.from_pretrained(
    model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda")
while True:
    try:
        url = apiurl + '&a=get'
        response = requests.get(url, timeout=2)
        res = response.json()
        if res["error"] == 1:
            print("还没任务")
            time.sleep(3)
            os.system(clear_command)

        else:
            task = res["data"]
            prompt = task["prompt_en"]
            prompt=prompt[:60]
            prompt += ",mdjrny-v4 style"
            image = pipe(prompt).images[0]
            # base64
            output_buffer = BytesIO()
            image.save(output_buffer, format='PNG')
            byte_data = output_buffer.getvalue()
            image64 = base64.b64encode(byte_data)
            url = apiurl+'&a=finish'
            rdata = task
            rdata["image64"] = image64
            t = time.time()
            image.save("./static/%s.png" % t)
            response = requests.post(url, data=rdata)
            print("生成成功")
            time.sleep(30)
            os.system(clear_command)
            # print(res)

    except requests.exceptions.RequestException as e:
        print(e)
        time.sleep(1)
