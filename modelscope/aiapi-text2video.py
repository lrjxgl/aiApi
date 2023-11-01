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
pipe = pipeline('text-to-video-synthesis', 'baiguan18/zeroscope_v2_xl')
#接口
queueKey="aiapi_text2video_create"
serviceId=serviceConf.serviceId
serviceToken=serviceConf.serviceToken
apiurl =serviceConf.apiHost+"/module.php?m=aiapi_text2video&serviceId="+serviceId+"&serviceToken="+serviceToken+"&queueKey="+queueKey
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
        url = apiurl + '&a=get'
        response = requests.get(url, timeout=30)
         
        res = response.json()
        print(res)
        if res["error"] == 1:
            print("还没任务")
            taskcheck.removeTask();
            time.sleep(3)

        else:
             
            task = res["data"]
            a=1;
            if task["action"]=='text2video' or  a==1:
                text = {
                        'text': task["prompt_en"],
                        'out_height': 576,
                        'out_width': 1024,
                }
                
                mp4url = pipe(text, output_video='./static/output.mp4')[OutputKeys.OUTPUT_VIDEO]
                rdata = task
                with open(mp4url,'rb') as f:
                    con=f.read()
                    rdata["base64"]=base64.b64encode(con).decode('utf-8')
                            
                ##发布回复
                url = apiurl+'&a=finish'
                taskcheck.removeTask();
                response = requests.post(url, data=rdata)

                print("生成成功")
            else:    
                taskcheck.removeTask();
            # print(res)

    except requests.exceptions.RequestException as e:
        print(e)
        taskcheck.removeTask();
        time.sleep(1)
