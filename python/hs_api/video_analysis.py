import cv2
import traceback
from hs_api.logger import logger
# Ref: https://docs.opencv.org/4.1.2/dc/dc3/tutorial_py_matcher.html
def find_timestamp(video_file, ref_im_file):
    '''
    Find Timestamp by ref image file in video_file
    '''
    video_capture = cv2.VideoCapture(video_file)
    ref_im = cv2.imread(ref_im_file, cv2.IMREAD_GRAYSCALE)
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    method = cv2.TM_CCORR_NORMED
    frame_index = 0

    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(ref_im, None)
    logger.info('out')
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    logger.info('out')
    match_list = []
    im_threshold = 12
    while True:
        ret, frame = video_capture.read()
        if not video_capture.isOpened():
            break
        frame_index += 1
        if not ret:
            break
        try:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            kp2, des2 = orb.detectAndCompute(gray_frame, None)
            
            matches = bf.match(des1, des2)
            matches = sorted(matches, key = lambda x:x.distance)
            logger.info('timestamp:', frame_index/fps)
            
            logger.info(matches[0].distance)
            logger.info(kp2[matches[0].trainIdx].pt)
            match_list.append(matches[0].distance)
            if im_threshold > matches[0].distance:
                return frame_index/fps
        except:
            logger.info(traceback.print_exc())

            match_list.append(1000000000000000000)
        
