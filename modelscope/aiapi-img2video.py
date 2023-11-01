import time
import requests
from io import BytesIO
import base64
import os
import platform
import taskcheck
import serviceConf
#model
from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
pipe = pipeline("image-to-video", 'damo/Image-to-Video')

#接口
queueKey="aiapi_img2video_create"
serviceId=serviceConf.serviceId
serviceToken=serviceConf.serviceToken
apiurl =serviceConf.apiHost+"/module.php?m=aiapi_img2video&serviceId="+serviceId+"&serviceToken="+serviceToken+"&queueKey="+queueKey
os_name = platform.system()
clear_command = 'cls' if os_name == 'Windows' else 'clear'
#载入模型

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
        print(res)
        if res["error"] == 1:
            print("还没任务")
            taskcheck.removeTask();
            time.sleep(5)

        else:
            
            task = res["data"]
            a=1
            if  a==1:
                print("开始视频任务")
                imgurl=task["imgurl"]
                mp4url = pipe(imgurl, output_video='./static/img2video/output.mp4')[OutputKeys.OUTPUT_VIDEO]
                
                rdata = task
                with open(mp4url,'rb') as f:
                    con=f.read()
                    rdata["base64"]=base64.b64encode(con).decode('utf-8')
                            
                ##发布回复
                 apiTime=serviceConf.apiTime();
                apiAccess=serviceConf.serviceAccess(serviceConf.serviceToken,apiTime)
                url = apiurl + '&a=finish&apiTime='+apiTime+"&apiAccess="+apiAccess
                taskcheck.removeTask();
                print("视频生成成功，反馈finish")
                response = requests.post(url, data=rdata)

                print("视频任务完成")
            else:    
                taskcheck.removeTask();
            # print(res)

    except requests.exceptions.RequestException as e:
        print(e)
        taskcheck.removeTask();
        time.sleep(5)
