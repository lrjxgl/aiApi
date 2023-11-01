import time
import requests
from urllib import request
from io import BytesIO
import base64
import os
import platform
import taskcheck
#model
import cv2
from moviepy.editor import *
#接口
queueKey="aiapi_unionvideo_create"
serviceId="10000002"
serviceToken="0e34e7713bb5721bd34dd2bc886f1788";
apiurl = "http://aiapi.deituicms.com/module.php?m=apitest_unionvideo&serviceId="+serviceId+"&serviceToken="+serviceToken+"&queueKey="+queueKey
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
        url = apiurl + '&a=get'
        response = requests.get(url, timeout=30)
         
        res = response.json()
        print(res)
        if res["error"] == 1:
            print("还没任务")
            time.sleep(3)

        else:
            
            task = res["data"]
            a=1
            if  a==1:
                videoList =task["videoList"]
                video_files=[]
                audioList=task["audioList"]
                audioClips=[]
                i=0
                for v in videoList:
                    file="./static/unionvideo"+str(i)+".mp4"
                    request.urlretrieve( v,file)
                    video_files.append(VideoFileClip(file))
                    i=i+1
                i=0
                for v in audioList:
                    file="static/unionvideo"+str(i)+".mp3"
                    request.urlretrieve( v,file)
                    audioClips.append(AudioFileClip(file))
                    i=i+1
                mp4url = './static/unionvideo.mp4'
                mp4url2 = './static/unionvideo_audio.mp4'
                # 创建一个视频读取器对象
                
                final_clip = concatenate_videoclips(video_files)
                # 保存合并后的视频文件
                final_clip.write_videofile(mp4url) 
                # 合成语音
                video_clip = VideoFileClip(mp4url)
                concatenated_audio = concatenate_audioclips(audioClips)
                final_clip = video_clip.set_audio(concatenated_audio)
                final_clip.write_videofile(mp4url2) 
 
                
                ##发布回复
                 
                rdata = task
                with open(mp4url2,'rb') as f:
                    con=f.read()
                    rdata["base64"]=base64.b64encode(con).decode('utf-8')
                            
                
                url = apiurl+'&a=finish'
                
                response = requests.post(url, data=rdata)

                print("生成成功")
            else:    
                print("视频合成出错了")
            # print(res)

    except requests.exceptions.RequestException as e:
        print(e)
        time.sleep(1)
