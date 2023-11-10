import requests
import time
import cv2
from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
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

pipe = pipeline(
    Tasks.controllable_image_generation,
    
    model='dienstag/cv_controlnet_controllable-image-generation_nine-annotators')
while True:
    try:
        apiTime=serviceConf.apiTime();
        apiAccess=serviceConf.serviceAccess(serviceConf.serviceToken,apiTime)
        url = apiurl + '&a=get&apiTime='+apiTime+"&apiAccess="+apiAccess
        response = requests.get(url, timeout=2)
        res = response.json()
        if res["error"] == 1:
            print("还没任务")
            time.sleep(3)
            os.system(clear_command)

        else:
            task = res["data"]
            print(task)
            prompt = task["prompt_en"]
            prompt=prompt[:60]
            if 'control_type' in task:
                control_type=task['control_type']
            else:
                control_type='canny'

            input = {
                'image': task["imgurl"],
                'prompt': prompt,
                "strength": 1.0,
                "ddim_steps": 30,
                "guess_mode": False,
                "scale": 9.0,
                "num_samples": 1,
                "eta": 0.0,
                "a_prompt": "best quality, extremely detailed",
                "n_prompt": "longbody, lowres, bad anatomy, bad hands, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality"
            }
    
            negative_prompt = "low quality, bad quality"
          
            output = pipe(
                input,
                control_type=control_type
            )[OutputKeys.OUTPUT_IMG]
            _, w, _ = output.shape
            detected_map = output[:, 0: int(w / 2) + 1]
            result = output[:, int(w / 2) + 1: w]
            image= result[:, :, ::-1]
            cv2.imwrite("control-pose.png", result[:, :, ::-1])
            #cv2.imwrite("control-pose.png", output)
            rdata = task
            with open("control-pose.png",'rb') as f:
                    con=f.read()
                    rdata["base64"] =base64.b64encode(con).decode('utf-8')
            
            apiTime=serviceConf.apiTime();
            apiAccess=serviceConf.serviceAccess(serviceConf.serviceToken,apiTime)
            url = apiurl + '&a=finish&apiTime='+apiTime+"&apiAccess="+apiAccess
            response = requests.post(url, data=rdata)
            print("生成成功")
             
            os.system(clear_command)
            # print(res)

    except requests.exceptions.RequestException as e:
        print(e)
        time.sleep(1)
