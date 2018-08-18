import cv2
import os
from .helping import get_prefix


def check(avi_list, jsn_list):
    res_avi_pref = []
    res_avi_list = []
    avi_list_pref = map(get_prefix, avi_list)
    jsn_list = map(get_prefix, jsn_list)

    for i, avi in enumerate(avi_list_pref):
        if avi in jsn_list:
            res_avi_pref.append(avi)
            res_avi_list.append(avi_list[i])
    return res_avi_list, res_avi_pref


def get_frames_num_list(jsn_path, avi_list, avi_prefxs):
    avi_frame_list = {}

    for i, avi in enumerate(avi_prefxs):
        for par_dir, subdirs, files in os.walk(jsn_path):

            if avi in subdirs:
                jsn_list = os.listdir(os.path.join(par_dir, avi))

                for file_name in jsn_list:
                    if avi_list[i] not in avi_frame_list:
                        avi_frame_list[avi_list[i]] = []

                    avi_frame_list[avi_list[i]].append(get_frame_num(file_name))

    return avi_frame_list


def get_frame_num(filename: str):
    return int(filename.split('.')[4])


def extract_frame(path_to):
    for dirs in os.listdir(path_to['inp']):
        cur_dir = os.path.join(path_to['inp'], dirs)
        if not os.path.isdir(cur_dir):
            continue

        file_list = os.listdir(cur_dir)
        avi_list = list(filter(lambda file_name: file_name.endswith('.avi'), file_list))
        old_dir = os.getcwd()
        os.chdir(path_to['jsn'])
        jsn_list = []
        for folder in os.listdir(os.curdir):
            if folder == dirs:
                for file in os.listdir(folder):
                    jsn_list.append(file)
        actual_avi_list, avi_prefxs = check(avi_list, jsn_list)

        if not actual_avi_list:
            continue

        os.chdir(old_dir)
        avi_frame_list = get_frames_num_list(path_to['jsn'], actual_avi_list, avi_prefxs)
        for video_file, frames in avi_frame_list.items():

            video_file_name = get_prefix(video_file)
            video_file = os.path.join(cur_dir, video_file)

            video_frames_dir = os.path.splitext(video_file.replace('inp', 'png'))[0]

            if not os.path.exists(video_frames_dir):
                os.makedirs(video_frames_dir)

            get_frame(frames, os.path.join(video_frames_dir, video_file_name + '.{}'), video_file)


def get_frame(frame_num_list, save_file, video_path):
    cap = cv2.VideoCapture(video_path)
    for frame_num in frame_num_list:
        cap.set(1, frame_num)
        ret, frame = cap.read()
        cv2.imwrite(save_file.format(str(frame_num).zfill(6)) + '.png', frame)
