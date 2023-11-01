import requests
import time
from urllib import request
from modelscope.utils.constant import Tasks
from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.models import Model
#from modelscope.pipelines import pipeline
#from diffusers import StableDiffusionXLPipeline
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
queueKey="aiapi_sam_create"
serviceId=serviceConf.serviceId
serviceToken=serviceConf.serviceToken
apiurl =serviceConf.apiHost+"/module.php?m=aiapi_sam&serviceId="+serviceId+"&serviceToken="+serviceToken+"&queueKey="+queueKey
#pipe
model = 'damo/cv_fastsam_image-instance-segmentation_sa1b'
pipe = pipeline('fast-sam-task', model=model, model_revision='v1.0.5')
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
        if res["error"] == 1:
            print("还没任务")
            taskcheck.removeTask();
            time.sleep(3)
            os.system(clear_command)

        else:
            
            task = res["data"]                        
            imgurl=task["imgurl"]
            image_path = './sam_img/input.jpg'
            request.urlretrieve(imgurl, image_path)
            inputs = {
                 'img_path': image_path,  # 输入图像路径
                 'device': 'cuda',         # 使用‘cpu’或者‘cuda’
                 'retina_masks': True,    # 是否使用retina
                'imgsz': 1024,           # 输入图像分辨率
                'conf': 0.4,             # 置信度阈值
               'iou': 0.9               # iou阈值
            }
            prompt_process = pipe(inputs)
            ##分割一切
            if task["samType"]=='prompt' :
                ann = prompt_process.text_prompt(text=task["prompt_en"])
            else:
                ann = prompt_process.everything_prompt()
            t = time.time()
            f="./sam_img/%s.png" % t
            prompt_process.plot(annotations=ann, output_path=f)
            #image.save(f)
            # base64
            output_buffer = BytesIO()
            img = Image.open(f)
            img.save(output_buffer, format='PNG')
            byte_data = output_buffer.getvalue()
            image64 = base64.b64encode(byte_data)
            apiTime=serviceConf.apiTime();
            apiAccess=serviceConf.serviceAccess(serviceConf.serviceToken,apiTime)
            url = apiurl + '&a=finish&apiTime='+apiTime+"&apiAccess="+apiAccess
            rdata = task
            rdata["base64"] = image64
            taskcheck.removeTask();
            response = requests.post(url, data=rdata)
            print("生成成功")
            time.sleep(3)
            os.system(clear_command)
            # print(res)

    except requests.exceptions.RequestException as e:
        print(e)
        taskcheck.removeTask();
        time.sleep(1)
