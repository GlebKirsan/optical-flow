import os
import cv2
import numpy as np
from queue import PriorityQueue

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


def Farneback(video_file: str, save_file_dir: str, queued_frames: PriorityQueue) -> None:
    """
    Расчёт оптического потока методом Farneback.

    :param video_file: Путь до видео, из которого будут извлекаться кадры.
    :param save_file_dir: Папка, куда будут сохраняться изображения.
    :param queued_frames: Очередь с кадрами, которые нужно обработать.

    """
    cap = cv2.VideoCapture(video_file)

    ret, pr_frame = cap.read()

    frame_to_write = queued_frames.get_nowait()
    for i in range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))):
        ret, nx_frame = cap.read()

        # Условие, на надобность обработки кадра
        if i == frame_to_write:
            pr_frame = cv2.cvtColor(pr_frame, cv2.COLOR_BGR2GRAY)
            nx_frame = cv2.cvtColor(nx_frame, cv2.COLOR_BGR2GRAY)

            flow = cv2.calcOpticalFlowFarneback(pr_frame,
                                                nx_frame,
                                                None, 0.5, 3, 15, 3, 5, 1.2, 0)
            hsv = draw_hsv(flow)
            cv2.imwrite(save_file_dir + f".{str(i).zfill(6)}.Far.png",
                        hsv)

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

        # Создаём путь до нужного видео, получаем map всех кадров,
        # для которых нужно посчитать поток, и сохраняем их в очередь
        # с приоритетом и формируем директорию для сохраняемых картинок
        file_prefix = get_file_prefix(files[0])
        save_file_dir = preparation(file_prefix, path_to['opt'])

        video_file = make_path_from_name(file_prefix, video_folder) + '.avi'
        frames_map = map(get_frame_num_from_filename, files)

        queued_frames = PriorityQueue()
        [queued_frames.put(i) for i in frames_map]

        Farneback(video_file,
                  os.path.join(save_file_dir, file_prefix),
                  queued_frames)
