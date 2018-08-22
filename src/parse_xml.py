import os
import json
import xml.etree.ElementTree as ET

from .common import get_file_prefix, make_path_from_name


def strip_data(data: str) -> str:
    """
    Избавление от лишних пробелов в данных
    :param data:
    :return: Строка без лишних пробелов

    """
    lines = data.split('\n')
    lines = map(str.strip, lines)
    result = ' '.join(lines)

    return result


def extract_data_from_frame_object(FrameObjects):
    """

    :param FrameObjects:
    :return:

    """
    data = {}

    for i, payload in enumerate(FrameObjects):
        transport = {}

        for info in payload:
            text = None

            if info.tag in ['vertices', 'rect']:
                text = strip_data(info.text)

            transport[info.tag] = text or info.text

        data[i] = transport

    return data


def get_data_from_xml_file(path_to_xml):
    """
    Извлекает данные о кадре, для которого есть разметка. Если данные
    отсутствуют возвращает None.
    :param path_to_xml: Путь до xml файла с разметкой кадров
    :return: dict or None

    """
    tree = ET.parse(path_to_xml)
    root = tree.getroot()
    FrameDataArray = root[1]
    frames_data = {}

    for _ in FrameDataArray:
        frame_num, frame_object = int(_[0].text), _[1]

        if not frame_object:
            continue

        frames_data[frame_num] = extract_data_from_frame_object(frame_object)

    return frames_data or None


def create_json_with_frame_data(path_to: dict) -> None:
    """
    Создание json файлов для каждого кадра, имеющего разметку в папке mar.
    :param path_to:
    :return:

    """
    for directory, sub_dirs, files in os.walk(path_to['mar']):

        # Если есть директории, то до файлов не спустились
        if sub_dirs:
            continue

        xml_file = files[0]
        payload = get_data_from_xml_file(os.path.join(directory, xml_file))

        if not payload:
            # В xml файле не было размеченных кадров
            continue

        prefix = get_file_prefix(xml_file)
        sub_dir = make_path_from_name(xml_file,
                                      path_to=path_to['jsn'])

        os.makedirs(sub_dir, exist_ok=True)

        for frame, data in payload.items():

            file_name = prefix + f'.{str(frame).zfill(6)}.json'

            with open(os.path.join(sub_dir, file_name), 'w') as jsn_file:
                json.dump(obj=data, fp=jsn_file, indent=4)
