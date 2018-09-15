import os
import cv2
import logging
import numpy as np
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


def draw_hsv(flow: np.ndarray, mask: np.ndarray):
    """
    Функция обработки потока.
    :param flow: Посчитанный поток.
    :param mask: Булевый numpy массив для устранения шума.
    :return:
    """
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


def process_image(frame: int, frame_to_cmp: np.ndarray, cur_frame: np.ndarray, dirs: dict, kernel: np.ndarray,
                  vizualize:bool, vertical: bool) -> None:
    """
    Функция обработки кадра.
    :param frame: Номер текущего кадра.
    :param frame_to_cmp: Кадр, с которым будет сравниваться текущий.
    :param cur_frame: Текущий кадр.
    :param dirs: Словарь с путями до соотвествующих текущему видео папок opt и viz.
    :param kernel: Ядро для морфологического расширения.
    :param vizualize: Разрешение на запись картинок с потокм и кадрами.
    :param vertical: Если хранит True и vizualize=True, то изображение с потоком и чистым кадром будет
    соединено вертикально.
    :return:
    """
    pr_frame = cv2.Canny(frame_to_cmp, 50, 300)
    nx_frame = cv2.Canny(cur_frame, 50, 300)

    flow = cv2.calcOpticalFlowFarneback(pr_frame,
                                        nx_frame,
                                        None, 0.5, 21, 21, 16, 7, 1.5, flags=1)

    # Находим границы, делаем их толще и на базе этого создаём маску
    # в местах, где нет границ, чтобы потом занулить их в потоке
    mask = cv2.dilate(nx_frame, kernel) == 0

    hsv = draw_hsv(flow, mask)

    frame_str = str(frame).zfill(6)
    file_name = dirs['opt'] + f".{frame_str}.Far.png"

    cv2.imwrite(file_name, hsv)

    logging.info(f"Сохранён файл {file_name}")

    if vizualize:
        viz_image = (np.vstack if vertical else np.hstack)((cur_frame, hsv))
        viz_file_name = dirs['viz'] + f".{frame_str}.viz.png"
        cv2.imwrite(viz_file_name, viz_image)
        logging.info(f"Сохранён файл {viz_file_name}")


def Farneback(video_file: str, dirs: dict, queued_frames: PriorityQueue,
              vizualize: bool,
              vertical: bool) -> None:
    """
    Расчёт оптического потока методом Farneback.

    :param video_file: Путь до видео, из которого будут извлекаться кадры.
    :param dirs: Словарь с путями до соотвествующих текущему видео папок opt и viz.
    :param queued_frames: Очередь с кадрами, которые нужно обработать.
    :param vizualize: Разрешение на запись картинок с потокм и кадрами.
    :param vertical: Если хранит True и vizualize=True, то изображение с потоком и чистым кадром будет
     соединено вертикально.
    """
    cap = cv2.VideoCapture(video_file)

    ret, pr_frame = cap.read()

    kernel = np.ones((2,2), dtype=np.uint8)
    frame_to_write = queued_frames.get()
    frame_to_cmp = pr_frame
    dist = 15
    for i in range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))):
        ret, cur_frame = cap.read()
        if frame_to_write - dist == i:
            frame_to_cmp = cur_frame

        # Условие, на надобность обработки кадра
        if i == frame_to_write:
            print(type(frame_to_cmp))
            process_image(i, frame_to_cmp, cur_frame, dirs, kernel, vizualize, vertical)

            if not queued_frames.empty():
                frame_to_write = queued_frames.get()


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


def calc_opt_flow(path_to: dict, vizualize=False, vertical=False):
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

        dir_for_opt = os.path.join(save_file_dir['opt'], file_prefix)
        dir_for_viz = os.path.join(save_file_dir['viz'], file_prefix)
        dirs = {
            'opt': dir_for_opt,
            'viz': dir_for_viz
        }

        Farneback(video_file,
                  dirs,
                  queued_frames,
                  vizualize,
                  vertical)

    logging.info("Расчёт выполнен.")
