import os
import cv2
import numpy as np
from time import time   

from src.common import make_path_from_name, get_frame_num_from_filename
from .get_frame import extract_frame


def preparation(video_file):
    video_file_name = os.path.split(video_file)[1]
    video_file_name_wo_ext = os.path.splitext(video_file_name)[0]
    save_file_dir = os.path.splitext(video_file)[0].replace('inp', 'opt')

    os.makedirs(save_file_dir, exist_ok=True)

    return save_file_dir, video_file_name_wo_ext


def draw_hsv(flow):
    h, w = flow.shape[:2]
    fx, fy = flow[:, :, 0], flow[:, :, 1]
    ang = np.arctan2(fy, fx) + np.pi
    v = np.sqrt(fx*fx + fy*fy)
    hsv = np.zeros((h, w, 3), np.uint8)
    hsv[..., 0] = ang * (180/np.pi / 2)
    hsv[..., 1] = 255
    hsv[..., 2] = np.minimum(v*4, 255)
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return bgr


def Farneback(video_file, frame_num):
    cap = cv2.VideoCapture(video_file)

    save_file_dir, video_file_name_wo_ext = preparation(video_file)

    cap.set(1, frame_num - 1)
    ret, frame1 = cap.read()
    pr_frame = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)

    ret, frame2 = cap.read()
    nx_frame = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    flow = cv2.calcOpticalFlowFarneback(pr_frame,
                                        nx_frame,
                                        None, 0.5, 3, 15, 3, 5, 1.2, 0)
    hsv = draw_hsv(flow)
    cv2.imwrite(
        os.path.join(
            save_file_dir,
            video_file_name_wo_ext + f".{str(frame_num).zfill(6)}.Far.png"
        ),
        hsv
    )


def check_png(path_to):
    walk = os.walk(path_to['png'])
    _, subdir, files = next(walk)
    if not subdir and not files:
        print("png файлы отсутствуют, будут созданы автоматически")
        extract_frame(path_to)
        print("png файлы созданы")


def calc_opt_flow(path_to):
    check_png(path_to)
    png_folder = path_to['png']
    video_folder = path_to['inp']

    for par_dir, subdir, files in os.walk(png_folder):
        if subdir:
            continue
        for image in files:
            video_file_path = os.path.join(video_folder,
                                           make_path_from_name(image, path_to['inp']) + '.avi')
            frame_num = get_frame_num_from_filename(image)
            prev_frames = frame_num
            Farneback(video_file_path, prev_frames)
