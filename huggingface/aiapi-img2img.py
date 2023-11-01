import requests
import time
from urllib import request
from PIL import Image
from diffusers.utils import load_image
from diffusers import StableDiffusionInpaintPipeline
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
queueKey="aiapi_img2img_create"
serviceId=serviceConf.serviceId
serviceToken=serviceConf.serviceToken
apiurl =serviceConf.apiHost+"/module.php?m=aiapi_img2img&serviceId="+serviceId+"&serviceToken="+serviceToken+"&queueKey="+queueKey

from PIL import Image
from diffusers.utils import load_image
from diffusers import StableDiffusionInpaintPipeline
pipe = StableDiffusionInpaintPipeline.from_pretrained(
    "G:/model/stabilityai/stable-diffusion-2-inpainting",
    torch_dtype=torch.float16,
)
pipe.to("cuda")
while True:
    try:
        url = apiurl + '&a=get'
        response = requests.get(url, timeout=2)
        print(response.text)
        res = response.json()
        if res["error"] == 1:
            print("还没任务")
            time.sleep(3)
            os.system(clear_command)

        else:
            task = res["data"]
            prompt = task["prompt_en"]
            prompt=prompt[:60]
            imgurl="./static/img2img-imgurl.png"
            request.urlretrieve(task["imgurl"], imgurl)
            im = Image.open(imgurl).resize((512,512))
            mask_img="./static/img2img-mask_img.png" 
            request.urlretrieve(task["mask_img"], mask_img)
            mask_im=Image.open(mask_img).resize((512,512))
            image = pipe(prompt=prompt, image=im, mask_image=mask_im).images[0]
             
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
            time.sleep(30)
            os.system(clear_command)
            # print(res)

    except requests.exceptions.RequestException as e:
        print(e)
        time.sleep(1)
