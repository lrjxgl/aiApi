import torch.cuda as cuda
import torch.cuda as cuda
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
 
queueKey="aiapi_imgcolor_create"
serviceId=serviceConf.serviceId
serviceToken=serviceConf.serviceToken
apiurl =serviceConf.apiHost+"/module.php?m=aiapi_imgcolor&serviceId="+serviceId+"&serviceToken="+serviceToken+"&queueKey="+queueKey
#pipe

pipe = pipeline(Tasks.image_colorization, model='damo/cv_ddcolor_image-colorization')
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
        res = response.json()
        if res["error"] == 1:
            print("还没任务")
            taskcheck.removeTask();
            time.sleep(3)
            os.system(clear_command)

        else:
            
            task = res["data"]                        
            imgurl=task["imgurl"]                   
            result = pipe(imgurl)
            taskcheck.removeTask();
            t = time.time()
            f="./static/%s.png" % t
            cv2.imwrite(f, result[OutputKeys.OUTPUT_IMG])
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
