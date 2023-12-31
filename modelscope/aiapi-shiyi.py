import requests
import time
from modelscope.utils.constant import Tasks
from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
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
 
queueKey="aiapi_shiyi_create"
serviceId=serviceConf.serviceId
serviceToken=serviceConf.serviceToken
apiurl =serviceConf.apiHost+"/module.php?m=aiapi_shiyi&serviceId="+serviceId+"&serviceToken="+serviceToken+"&queueKey="+queueKey
#pipe

model_id = 'damo/cv_daflow_virtual-try-on_base'
pipe = pipeline(task=Tasks.virtual_try_on, model=model_id)
while True:
    try:
        t=taskcheck.canTask()
        if t==False:
            print('执行其它任务');
            time.sleep(1)
            continue;
        taskcheck.addTask()    
        url = apiurl + '&a=get'
        response = requests.get(url, timeout=5)
        print(response.text)
        res = response.json()
        if res["error"] == 1:
            print("还没任务")
            taskcheck.removeTask();
            time.sleep(3)
            os.system(clear_command)

        else:
            
            task = res["data"]                        
               
            input_imgs = {
                  'masked_model': task["mt_img"],
                  'pose': task["pose_img"],
                  'cloth': task["cloth_img"]
            }            
            img = pipe(input_imgs)[OutputKeys.OUTPUT_IMG]
            taskcheck.removeTask();
             
            f="./static/shiyi.png"
            cv2.imwrite(f,  img[:, :, ::-1])
            with open(f,'rb') as f:
                con=f.read()
                image64=base64.b64encode(con).decode('utf-8')
             
            url = apiurl+'&a=finish'
            rdata = task
            rdata["base64"] = image64
            
            response = requests.post(url, data=rdata)
            print("生成成功")
            time.sleep(3)
            os.system(clear_command)
            # print(res)

    except requests.exceptions.RequestException as e:
        print(e)
        taskcheck.removeTask();
        time.sleep(1)
