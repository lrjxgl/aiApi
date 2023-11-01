import requests
import base64
import re
import json 
import time
from moviepy.editor import *
from urllib import request
from io import BytesIO
import os
import platform
import taskcheck
import serviceConf
import datetime
import hashlib
def getApp():
    data={};
    data["appId"]=10000000;
    data["appToken"]="asdasdasdasdasdasd"
    data["siteToken"]="qweqweqweds"
    data["apiurl"]="http://aiapi.deituicms.com/"
    return data
def text2movie(prompt,taskid=0):
    App=getApp()
    
    url=App["apiurl"]+"/module.php?m=aiapi_text2text&a=create"
    data={
        "taskid":taskid,
        "prompt":prompt,
        "appId":App["appId"],
        "appToken":App["appToken"],
        "notify_url":"/module.php?m=apitest_text2text&a=notify",
        "action":"text2text",
        "aimodel":"",
        "history":[]
        
    }
    
    response=requests.post(url,data=data)
    res = response.json()
    
    taskid=res["data"]["taskid"]
    
    #taskid=177
    ###
    while True:
        apiTime=serviceConf.apiTime();
        apiAccess=serviceConf.serviceAccess(App["appToken"],apiTime)
        url=App["apiurl"]+"/module.php?m=aiapi_text2text&a=check"
        data={
            "appId":App["appId"],
            "apiTime":apiTime,
            "apiAccess":apiAccess,
            "taskid":taskid
        }
        print("检测结果"+ str(taskid))
        print(data)
        response=requests.post(url,data=data)
       
        res = response.json()
        
        #print(res)
        if res["error"]==0:
            print("生成成功")
            content=res["data"]["content"]
            pattern2 = re.compile(r'旁白[^：]*：(.*)', re.I)
            arr2 = pattern2.findall(content)
            pattern = r"画面[^：]*：(.*?)旁白："
            arr = re.findall(pattern, content, re.I | re.S)
         

            # 检查两个匹配结果的长度是否相同，如果不同或者为0，返回错误信息
            if len(arr) != len(arr2) or len(arr) == 0:
                print(json.dumps({"error": 1, "message": "text2text生成错误"}))
                #text2movie(prompt,taskid)
                break
            # 生成画面
            print("生成画面")
            imgList=[]
            imgTaskids=[];
            #demo
            for i in range(len(arr)):
                #语音1秒6个字 一个图片4秒
                m=round(len(arr2[i])/22)
                for j in range(m):
                    imgTaskid=text2img(arr[i])
                    imgTaskids.append(imgTaskid)
                    #imgList.append(imgurl)
            
            #imgTaskids=[313, 314, 315, 316, 317, 318, 319, 320]
            print(imgTaskids)
            
        

            # 生成旁白
            print("生成旁白")
            ttsTaskids=[]
            audioList=[]
            
            for p in arr2:
                ttsTaskid=tts(p)
                ttsTaskids.append(ttsTaskid)
            
            #ttsTaskids=[201,203,204] 
            print(ttsTaskids)
            imgList=text2img_check(imgTaskids)
            print(imgList)
            audioList=tts_check(ttsTaskids)
            print(audioList)
             
            # img2video
            print("生成视频")
            videoList=[]
            videoIds=[]
            for img in imgList:
                videoid=img2video(img)
                videoIds.append(videoid)
            #videoIds=[157, 158, 159]
            print(videoIds)    
            videoList=img2video_check(videoIds)
            print(videoList)
            # 合并视频音频
            mp4url= unionvideo(videoList,audioList)  
            print("视频合成成功")  
            return mp4url
        else:
            time.sleep(1)
            
def text2img(prompt):
    App=getApp()
    url=App["apiurl"]+"/module.php?m=aiapi_text2img&a=create"
    apiTime=serviceConf.apiTime();
    apiAccess=serviceConf.serviceAccess(App["appToken"],apiTime)
    data={
        "prompt":prompt,
        "width":1024,
        "height":1024,
        "num_inference_steps":30,
        "appId":App["appId"],
        "apiTime":apiTime,
        "apiAccess":apiAccess,
        "notify_url":"/module.php?m=apitest_text2img&a=notify",
        "action":"text2img",
        "history":[]
        
    }
    
    response=requests.post(url,data=data)
    print(response.text)
    res = response.json()
    
    taskid=res["data"]["taskid"]
    return taskid
    

def text2img_check(taskids):
    App=getApp()
    
    while True:
        url=App["apiurl"]+"/module.php?m=aiapi_text2img&a=check"
        apiTime=serviceConf.apiTime();
        apiAccess=serviceConf.serviceAccess(App["appToken"],apiTime)
        data={
            "appId":App["appId"],
            "appToken":App["appToken"], 
            "taskids":",".join(str(i) for i in taskids)
        }
         
        response=requests.post(url,data=data)
        
        res = response.json()
        print(res)
        if res["error"]==0:
            
            imgList=res["data"]["imgList"]
            print("imgList生成成功")
            return imgList
        else:
            time.sleep(3)
            
def tts(prompt):
    App=getApp()
    url=App["apiurl"]+"/module.php?m=aiapi_tts&a=create"
    apiTime=serviceConf.apiTime();
    apiAccess=serviceConf.serviceAccess(App["appToken"],apiTime)
    data={
        "prompt":prompt,
        "appId":App["appId"],
        "apiTime":apiTime,
        "apiAccess":apiAccess,
        "notify_url":"/module.php?m=apitest_tts&a=notify",
        "action":"tts",
        "history":[]
        
    }
    
    response=requests.post(url,data=data)
    print(response.text)
    res = response.json()
    
    taskid=res["data"]["taskid"]
    return taskid               
def tts_check(taskids):
    App=getApp()
    while True:
        url=App["apiurl"]+"/module.php?m=aiapi_tts&a=check"
        apiTime=serviceConf.apiTime();
        apiAccess=serviceConf.serviceAccess(App["appToken"],apiTime)
        data={
            "appId":App["appId"],
            "apiTime":apiTime,
            "apiAccess":apiAccess, 
            "taskids":",".join(str(i) for i in taskids)
        }
         
        response=requests.post(url,data=data)
       
        res = response.json()
        print(res)
        if res["error"]==0:
            
            mp3List=res["data"]["mp3List"]
            print("ttsList生成成功")
            return mp3List
        else:
            time.sleep(3)    

def img2video(imgurl):
    App=getApp()
    url=App["apiurl"]+"/module.php?m=aiapi_img2video&a=create"
    apiTime=serviceConf.apiTime();
    apiAccess=serviceConf.serviceAccess(App["appToken"],apiTime)
    data={
        "prompt":"",
        "oimgurl":imgurl,
        "mp4url":"",
        "appId":App["appId"],
        "apiTime":apiTime,
        "apiAccess":apiAccess,
        "notify_url":"/module.php?m=apitest_img2video&a=notify",
        "action":"tts",
        "history":[]
        
    }
    
    response=requests.post(url,data=data)
    print(response.text)
    res = response.json()
    
    taskid=res["data"]["taskid"]
    return taskid
def img2video_check(taskids):
    App=getApp()
    while True:
        url=App["apiurl"]+"/module.php?m=aiapi_img2video&a=check"
        apiTime=serviceConf.apiTime();
        apiAccess=serviceConf.serviceAccess(App["appToken"],apiTime)
        data={
            "appId":App["appId"],
            "apiTime":apiTime,
            "apiAccess":apiAccess,
            "taskids":",".join(str(i) for i in taskids)
        }
         
        try:

            response=requests.post(url,data=data)
        
            res = response.json()
            print(res)
            if res["error"]==0:
                
                mp4List=res["data"]["mp4List"]
                print("ttsList生成成功")
                return mp4List
            else:
                time.sleep(3) 
        except requests.exceptions.RequestException as e:
           return img2video_check(taskids)
            
            
def unionvideo(videoList,audioList):
    print(videoList)
    print(audioList)

    video_files=[]
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
    print(mp4url2)
    return mp4url2

"""
text2movie("帮我写一个有关科幻题材的短视频脚本，含3个场景，每个场景有一个详细的画面和旁白。")   
#text2img("一个黑暗的宇宙空间，一艘巨大的太空船模型，模型上有一个神秘的标志。")
#tts("一个黑暗的宇宙空间，一艘巨大的太空船模型，模型上有一个神秘的标志。")
#img2video("http://aiapi.deituicms.com/attach/2023/09/16/11051096.png.small.jpg")
'''
videoList=["http://aiapi.deituicms.com//attach/2023/09/15/835.mp4",
			"http://aiapi.deituicms.com//attach/2023/09/15/834.mp4",
			"http://aiapi.deituicms.com//attach/2023/09/15/833.mp4"
]
audioList=[
       "http://aiapi.deituicms.com//attach/2023/09/15/822.mp3",
			"http://aiapi.deituicms.com//attach/2023/09/15/823.mp3",
			"http://aiapi.deituicms.com//attach/2023/09/15/826.mp3"
]
unionvideo(videoList,audioList)
"""
#接口
queueKey="aiapi_text2movie_create"
serviceId="10000002"
serviceToken="0e34e7713bb5721bd34dd2bc886f1788"
apiurl = "http://aiapi.deituicms.com/module.php?m=aiapi_text2movie&serviceId="+serviceId+"&serviceToken="+serviceToken+"&queueKey="+queueKey
os_name = platform.system()
clear_command = 'cls' if os_name == 'Windows' else 'clear'

while True:
    try:
         
        url = apiurl + '&a=get'
        print(url)
        response = requests.get(url, timeout=30)
         
        res = response.json()
        print(res)
        if res["error"] == 1:
            print("还没任务")
            time.sleep(5)

        else:
             
            task = res["data"]
            a=1
            if  a==1:
                prompt=task["prompt"]
                mp4url=text2movie(prompt)
                rdata = task
                with open(mp4url,'rb') as f:
                    con=f.read()
                    rdata["base64"]=base64.b64encode(con).decode('utf-8')
                         
                ##发布回复
                url = apiurl+'&a=finish'
                
                response = requests.post(url, data=rdata)

                print("生成成功")
            else:    
                print("等待")
            # print(res)

    except requests.exceptions.RequestException as e:
        print(e)
        
        time.sleep(1)
 
