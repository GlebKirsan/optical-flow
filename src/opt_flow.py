import os
import cv2
import logging
import numpy as np
from time import time
from queue import PriorityQueue

from src.common import make_path_from_name, get_frame_num_from_filename, get_file_prefix
from .get_frame import extract_frame


def preparation(file_prefix: str, path_to: dict) -> dict:
    """
    Функция подготавливает директории, куда будут сохраняться обработанные
    кадры.

    :param file_prefix: Строка вида xxx.yyy.zzz.ppp.
    :param path_to: Словарь с путями до папок.
    :return: Путь, куда будут сохраняться кадры.

    """
    save_file_dir = {'opt': make_path_from_name(file_prefix, path_to['opt']),
                     'viz': make_path_from_name(file_prefix, path_to['viz'])}
    os.makedirs(save_file_dir['opt'], exist_ok=True)
    os.makedirs(save_file_dir['viz'], exist_ok=True)

    return save_file_dir


def draw_hsv(flow, mask=None):
    h, w = flow.shape[:2]
    fx, fy = flow[:, :, 0], flow[:, :, 1]

    ang = np.arctan2(fy, fx) + np.pi
    v = np.sqrt(fx*fx + fy*fy)
    hsv = np.zeros((h, w, 3), np.uint8)

    hsv[:, :, 0] = ang * (90 / np.pi)
    hsv[:, :, 1] = 255
    hsv[:, :, 2] = np.minimum(v * 4, 255)

    hsv[mask] = 0
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return bgr


def Farneback(video_file: str, dir_for_opt: str, dir_for_viz: str,
              queued_frames: PriorityQueue, vertical: bool) -> None:
    """
    Расчёт оптического потока методом Farneback.

    :param video_file: Путь до видео, из которого будут извлекаться кадры.
    :param dir_for_opt: Папка, куда будут сохраняться изображения.
    :param dir_for_viz: Папка для хранения склеенных кадров с оптическим потоком для сравнения.
    :param queued_frames: Очередь с кадрами, которые нужно обработать.
    :param vertical: Если хранит True, то изображение с потоком и чистым кадром будет соединено вертикально.
    """
    cap = cv2.VideoCapture(video_file)

    ret, pr_frame = cap.read()

    kernel = np.ones((5, 5), np.uint8)
    frame_to_write = queued_frames.get()
    for i in range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))):
        ret, nx_frame = cap.read()
        # Условие, на надобность обработки кадра
        if i == frame_to_write:
            pr_frame = cv2.cvtColor(pr_frame, cv2.COLOR_BGR2GRAY)
            nx_frame_gray = cv2.cvtColor(nx_frame, cv2.COLOR_BGR2GRAY)

            flow = cv2.calcOpticalFlowFarneback(pr_frame,
                                                nx_frame_gray,
                                                None, 0.5, 5, 7, 5, 5, 1.2, 0)

            # Находим границы, делаем их толще и на базе этого создаём маску
            # в местах, где нет границ, чтобы потом занулить их в потоке
            mask = cv2.Canny(nx_frame, 200, 300)
            mask = cv2.dilate(mask, kernel, iterations=1) == 0

            hsv = draw_hsv(flow, mask)
            viz_image = (np.vstack if vertical else np.hstack)((nx_frame, hsv))

            frame_str = str(i).zfill(6)
            file_name = dir_for_opt + f".{frame_str}.Far.png"
            viz_file_name = dir_for_viz + f"{frame_str}.viz.png"

            cv2.imwrite(file_name, hsv)
            cv2.imwrite(viz_file_name, viz_image)

            logging.info(f"Сохранён файл {file_name}")
            logging.info(f"Сохранён файл {viz_file_name}")

            if not queued_frames.empty():
                frame_to_write = queued_frames.get()

        pr_frame = nx_frame


def check_png(path_to: dict):
    """
    Проверка наличия png файлов-кадров, для которых будет посчитан
    поток.
    """
    walk = os.walk(path_to['png'])
    _, subdir, files = next(walk)
    if not subdir and not files:
        logging.info("png файлы отсутствуют, будут созданы автоматически.")
        extract_frame(path_to)
        logging.info("png файлы созданы.")


def calc_opt_flow(path_to: dict, vertical: bool):
    check_png(path_to)

    png_folder = path_to['png']
    video_folder = path_to['inp']
    logging.info("Расчёт оптического потока.")
    for par_dir, subdir, files in os.walk(png_folder):
        if subdir:
            # Не спустились до файлов
            continue

        # Создаём путь до нужного видео, получаем map всех кадров,
        # для которых нужно посчитать поток, и сохраняем их в очередь
        # с приоритетом и формируем директорию для сохраняемых картинок
        file_prefix = get_file_prefix(files[0])
        save_file_dir = preparation(file_prefix, path_to)

        video_file = make_path_from_name(file_prefix, video_folder) + '.avi'
        frames_map = map(get_frame_num_from_filename, files)

        queued_frames = PriorityQueue()
        [queued_frames.put(i) for i in frames_map]
        t = time()

        dir_for_opt = os.path.join(save_file_dir['opt'], file_prefix)
        dir_for_viz = os.path.join(save_file_dir['viz'], file_prefix)

        Farneback(video_file,
                  dir_for_opt, dir_for_viz,
                  queued_frames,
                  vertical)

    logging.info("Расчёт выполнен.")
