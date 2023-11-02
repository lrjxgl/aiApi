import requests
import time
from diffusers import AutoencoderKL, StableDiffusionXLControlNetPipeline, ControlNetModel, UniPCMultistepScheduler
from controlnet_aux import OpenposeDetector 
from diffusers.utils import load_image
from PIL import Image
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
queueKey="aiapi_ctrl2img_create"
serviceId=serviceConf.serviceId
serviceToken=serviceConf.serviceToken
apiurl =serviceConf.apiHost+"/module.php?m=aiapi_ctrl2img&serviceId="+serviceId+"&serviceToken="+serviceToken+"&queueKey="+queueKey
#openpose = OpenposeDetector.from_pretrained("lllyasviel/ControlNet")
controlnet = ControlNetModel.from_pretrained("/mnt/workspace/sdxl-control/", torch_dtype=torch.float16)
pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
     '/mnt/workspace/.cache/modelscope/AI-ModelScope/stable-diffusion-xl-base-1.0', controlnet=controlnet, torch_dtype=torch.float16
)
pipe.enable_model_cpu_offload()
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
            openpose_image = load_image(task["imgurl"])
            #openpose_image = openpose(img)
            #image = pipe(prompt).images[0]
            negative_prompt = "low quality, bad quality"
            images = pipe(
                prompt, 
                negative_prompt=negative_prompt,
                num_inference_steps=30,
                num_images_per_prompt=1,
                image=openpose_image.resize((1024, 1024))
            ).images
            image=images[0]
            # base64
            output_buffer = BytesIO()
            image.save(output_buffer, format='PNG')
            byte_data = output_buffer.getvalue()
            image64 = base64.b64encode(byte_data)
            url = apiurl+'&a=finish'
            rdata = task
            rdata["base64"] = image64
            t = time.time()
            image.save("./static/%s.png" % t)
            response = requests.post(url, data=rdata)
            print("生成成功")
             
            os.system(clear_command)
            # print(res)

    except requests.exceptions.RequestException as e:
        print(e)
        time.sleep(1)
