import xml.etree.ElementTree as ET
import os
import json
from .helping import get_prefix


def format_data(data):
    lines = data.split('\n')
    result = ""

    for line in lines:
        result += line.strip()

    return result


def get_data(FrameObjects):
    data = {}
    for _ in enumerate(FrameObjects):
        transport = {}
        payload = _[1]
        for i in payload:
            text = None

            if i.tag in ['vertices', 'rect']:
                text = format_data(i.text)

            transport[i.tag] = text or i.text
        data[_[0]] = transport
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
            subdir = os.path.split(directory)[1]
            continue

        xml_file = files[0]
        payload = parse_xml(os.path.join(directory, xml_file))
        if not payload:
            continue

        prefix = get_prefix(xml_file)
        new_dir = os.path.join(path_to['jsn'], subdir, prefix)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)

        for frame, data in payload.items():
            file_name = prefix + f'.{str(frame).zfill(6)}.json'
            with open(os.path.join(new_dir, file_name), 'w') as jsn_file:
                json.dump(data, jsn_file)


