import os
import cv2
import numpy as np
from .get_frame import get_frame_num
from .helping import get_path


def preparation(video_file):
    video_file_name = os.path.split(video_file)[1]
    video_file_name_wo_ext = os.path.splitext(video_file_name)[0]
    save_file_dir = os.path.splitext(video_file)[0].replace('inp', 'opt')

    if not os.path.exists(save_file_dir):
        os.makedirs(save_file_dir)

    return save_file_dir, video_file_name_wo_ext


def calc_opt_flow_LuK(video_file: str, frame_num: int) -> None:
    cap = cv2.VideoCapture(video_file)

    save_file_dir, video_file_name_wo_ext = preparation(video_file)

    feature_params = dict(maxCorners=100,
                          qualityLevel=0.3,
                          minDistance=7,
                          blockSize=7)

    lk_params = dict(winSize=(15, 15),
                     maxLevel=2,
                     criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    color = np.random.randint(0, 255, (100, 3))

    cap.set(1, frame_num)
    ret, old_frame = cap.read()
    old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
    p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)

    mask = np.zeros_like(old_frame)
    ret, frame = cap.read()

    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
    good_new = p1[st == 1]
    good_old = p0[st == 1]

    for j, (new, old) in enumerate(zip(good_new, good_old)):
        a, b = new.ravel()
        c, d = old.ravel()
        mask = cv2.line(mask, (a, b), (c, d), color[j].tolist(), 2)
        frame = cv2.circle(frame, (a, b), 5, color[j].tolist(), -1)
    img = cv2.add(frame, mask)

    cv2.imwrite(os.path.join(save_file_dir,
                             video_file_name_wo_ext + f".{str(frame_num + 1).zfill(6)}.LuK.png"), img)
    cap.release()


def calc_opt_flow_Farneback(video_file, frame_num):
    cap = cv2.VideoCapture(video_file)

    save_file_dir, video_file_name_wo_ext = preparation(video_file)

    cap.set(1, frame_num)
    ret, frame1 = cap.read()
    prvs = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
    hsv = np.zeros_like(frame1)
    hsv[...,1] = 255
    rang = 2
    for i in range(rang):
        ret, frame2 = cap.read()
        next = cv2.cvtColor(frame2,cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(prvs, next, None, 0.5, 5, 15, 5, 5, 1.2, 0)
        mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
        hsv[...,0] = ang*180/np.pi/2
        hsv[...,2] = cv2.normalize(mag,None,0,255,cv2.NORM_MINMAX)
        rgb = cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
        if i == rang - 1:
            cv2.imwrite(
                os.path.join(
                    save_file_dir,
                    video_file_name_wo_ext + f".{str(frame_num + rang).zfill(6)}.Far.png"),
                rgb)


def main(path_to):
    png_folder = path_to['png']
    video_folder = path_to['inp']
    for par_dir, subdir, files in os.walk(png_folder):
        if subdir:
            continue
        for image in files:
            video_file_path = os.path.join(video_folder, get_path(image) + '.avi')
            frame_num = get_frame_num(image)
            prev_frames = frame_num - 2
            calc_opt_flow_Farneback(video_file_path, prev_frames)
