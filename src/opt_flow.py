import os
import cv2
import numpy as np
from time import time

from src.common import make_path_from_name, get_frame_num_from_filename, get_file_prefix
from .get_frame import extract_frame


def preparation(file_prefix: str, path_to_opt_folder: dict) -> str:
    """
    Функция подготавливает директории, куда будут сохраняться обработанные
    кадры.

    :param file_prefix: Строка вида xxx.yyy.zzz.ppp.
    :param path_to_opt_folder: Путь до папки, где будут оптические потоки.
    :return: Путь, куда будут сохраняться кадры.

    """
    save_file_dir = make_path_from_name(file_prefix, path_to_opt_folder)
    os.makedirs(save_file_dir, exist_ok=True)
    return save_file_dir


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


def Farneback(video_file: str, save_file_dir: str, frames_list: map) -> None:
    """
    Расчёт оптического потока методом Farneback.

    :param video_file: Путь до видео, из которого будут извлекаться кадры.
    :param save_file_dir: Папка, куда будут сохраняться изображения.
    :param frames_list: map с кадрами, которые нужно обработать.

    """
    cap = cv2.VideoCapture(video_file)

    for frame_num in frames_list:
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
                save_file_dir + f".{str(frame_num).zfill(6)}.Far.png"
            ),
            hsv
        )


def check_png(path_to: dict):
    """
    Проверка наличия png файлов-кадров, для которых будет посчитан
    поток.
    """
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
            # Не спустились до файлов
            continue

        # Создаём путь до нужного видео, получаем список всех кадров,
        # для которых нужно посчитать поток, и формируем директорию
        # для сохраняемых картинок
        file_prefix = get_file_prefix(files[0])
        save_file_dir = preparation(file_prefix, path_to['opt'])
        video_file = make_path_from_name(file_prefix, video_folder) + '.avi'
        frames_list = map(get_frame_num_from_filename, files)
        
        Farneback(video_file, save_file_dir, frames_list)
