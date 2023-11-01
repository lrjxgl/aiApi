import cv2
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from modelscope.outputs import OutputKeys

portrait_matting = pipeline(Tasks.portrait_matting,model='damo/cv_unet_image-matting')
result = portrait_matting('https://modelscope.oss-cn-beijing.aliyuncs.com/demo/image-matting/1.png')
cv2.imwrite('result.png', result[OutputKeys.OUTPUT_IMG])