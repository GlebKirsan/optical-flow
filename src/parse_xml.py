import os
import json
import xml.etree.ElementTree as ET
from .common import get_prefix, get_path


def format_data(data):
    lines = data.split('\n')
    result = ""

    for line in lines:
        result += line.strip()

    return result


def get_data(FrameObjects):
    data = {}
    for i, payload in enumerate(FrameObjects):
        transport = {}
        for info in payload:
            text = None

            if info.tag in ['vertices', 'rect']:
                text = format_data(info.text)

            transport[info.tag] = text or info.text
        data[i] = transport
    return data


def parse_xml(path_to_xml):
    tree = ET.parse(path_to_xml)
    root = tree.getroot()
    FrameDataArray = root[1]
    frames_data = {}

    for _ in FrameDataArray:
        FrameObjects = _[1]
        if not FrameObjects:
            continue

        frames_data[int(_[0].text)] = get_data(FrameObjects)

    return frames_data or None


def frame_info_to_json(path_to):
    for directory, subdirs, files in os.walk(path_to['mar']):
        if subdirs:
            continue

        xml_file = files[0]
        payload = parse_xml(os.path.join(directory, xml_file))

        if not payload:
            continue

        prefix = get_prefix(xml_file)
        subdir = get_path(xml_file)
        new_dir = os.path.join(path_to['jsn'], subdir)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)

        for frame, data in payload.items():
            file_name = prefix + f'.{str(frame).zfill(6)}.json'
            with open(os.path.join(new_dir, file_name), 'w') as jsn_file:
                json.dump(data, jsn_file)
