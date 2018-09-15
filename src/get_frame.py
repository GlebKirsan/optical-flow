import cv2
import os
import logging

from src.common import get_file_prefix
from src.common import make_path_from_name
from src.common import get_frame_num_from_filename
from .parse_xml import create_json_with_frame_data


def check(avi_list: list, jsn_list: list) -> list:
    """
    :param avi_list: Список avi файлов в директории.
    :param jsn_list: Список json файлов в соотвествующей директории.
    :return: Список avi файлов, для которых есть разметка.

    """
    res_avi_list = []
    jsn_list = set(map(get_file_prefix, jsn_list))
    avi_list_pref = map(get_file_prefix, avi_list)

    for i, avi in enumerate(avi_list_pref):

        # Проверка на наличие разметки для видео
        if avi in jsn_list:
            res_avi_list.append(avi_list[i])

    return res_avi_list


def get_frames_in_video_dict(jsn_path, avi_list) -> dict:
    """
    Функция возвращает словарь, в котором ключ - название видео,
    значение - список с размеченными кадрами для этого видео.
    """
    avi_frame_list = {}
    for avi in avi_list:

        needed_json_files = make_path_from_name(avi, path_to=jsn_path)
        files = os.listdir(needed_json_files)
        files = list(map(get_frame_num_from_filename, files))
        avi_frame_list[avi] = files

    return avi_frame_list


def check_json_files(path_to):
    """
    Функция создаёт json файлы с разметкой, если они отсутствуют.
    """
    jsn_folders = os.listdir(path_to['jsn'])
    if not jsn_folders:
        logging.info("jsn файлы отсутствуют, будут созданы автоматически")
        create_json_with_frame_data(path_to)
        logging.info("jsn файлы созданы")


def extract_frame(path_to: dict):
    """
    :param path_to: Словарь с путями до ключевых директорий.
    """
    check_json_files(path_to)

    for directory in os.listdir(path_to['inp']):
        cur_dir = os.path.join(path_to['inp'], directory)

        # Выбираем только файлы с расширением avi
        videos_list = list(filter(lambda file_name: file_name.endswith('.avi'),
                                  os.listdir(cur_dir)))

        os.chdir(path_to['jsn'])

        jsn_list = []
        jsn_folders = os.listdir(os.curdir)
        for folder in jsn_folders:

            if folder == directory:
                jsn_list = os.listdir(folder)

                break

        # Формирование списка видео, для которых есть разметка
        actual_avi_list = check(videos_list, jsn_list)

        os.chdir(path_to['parent'])

        # Проверка на наличие разметки для видеофайлов текущей директории
        if not actual_avi_list:
            print(directory)
            continue

        avi_frame_list = get_frames_in_video_dict(path_to['jsn'],
                                                  actual_avi_list)

        for video_file, frames in avi_frame_list.items():

            video_file_name = get_file_prefix(video_file)
            video_file_path = make_path_from_name(video_file_name,
                                                  path_to=path_to['png'])

            video_file = os.path.join(cur_dir, video_file)

            os.makedirs(video_file_path, exist_ok=True)

            save_frames_from_video(frames,
                                   os.path.join(
                                       video_file_path,
                                       video_file_name + '.{}'),
                                   video_file)


def save_frames_from_video(frame_num_list: list, save_file: str, video_path: str):
    """
    :param frame_num_list: Список кадров для видео-файла.
    :param save_file: f-строка с местом для номера кадра.
    :param video_path: Видео, из которого извлекаются кадры.

    """
    cap = cv2.VideoCapture(video_path)

    for frame_num in frame_num_list:
        cap.set(1, frame_num)
        ret, frame = cap.read()
        file_name = save_file.format(str(frame_num).zfill(6)) + '.png'
        logging.info(f"Сохранется файл {file_name}")
        cv2.imwrite(file_name, frame)
    cap.release()
