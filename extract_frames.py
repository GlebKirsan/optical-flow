import xml.etree.ElementTree as ET
import argparse
import os
import json
import time
import get_frame


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


def get_prefix(name):
    end_of_prefix = 4
    return '.'.join(name.split('.')[:end_of_prefix])


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


def build_dirs(directory):
    path_to = {
        file_name: os.path.join(directory, file_name) for file_name in os.listdir(directory)
        if os.path.isdir(os.path.join(directory, file_name))
    }
    for i in ['opt', 'jsn', 'png']:
        if i not in path_to:
            new_dir = os.path.join(directory, i)
            os.mkdir(new_dir)
            path_to[i] = new_dir
    path_to['parent'] = directory
    return path_to


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


def get_frames_num(jsn_path, avi_list, avi_prefxs):
    avi_frame_list = {}
    int_string = lambda x: int(x.split('.')[4])

    for i, avi in enumerate(avi_prefxs):
        for par_dir, subdirs, files in os.walk(jsn_path):

            if avi in subdirs:
                jsn_list = os.listdir(os.path.join(par_dir, avi))

                for file_name in jsn_list:
                    if avi_list[i] not in avi_frame_list:
                        avi_frame_list[avi_list[i]] = []

                    avi_frame_list[avi_list[i]].append(int_string(file_name))

    return avi_frame_list


def extract_frame(path_to):
    for dirs in os.listdir(path_to['inp']):
        cur_dir = os.path.join(path_to['inp'], dirs)
        if not os.path.isdir(cur_dir):
            continue

        file_list = os.listdir(cur_dir)
        avi_list = list(filter(lambda file: file.endswith('.avi'), file_list))
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
        avi_frame_list = get_frames_num(path_to['jsn'], actual_avi_list, avi_prefxs)
        for video_file, frames in avi_frame_list.items():

            video_file_name = get_prefix(video_file)
            video_file = os.path.join(cur_dir, video_file)

            video_frames_dir = os.path.splitext(video_file.replace('inp', 'png'))[0]

            if not os.path.exists(video_frames_dir):
                os.makedirs(video_frames_dir)

            get_frame.get_frame(frames, os.path.join(video_frames_dir, video_file_name + '.{}'), video_file)


def _main(**kwargs):
    st = time.time()
    path_to = build_dirs(kwargs['dir'])
    if kwargs['jsn']:
        frame_info_to_json(path_to)
    if kwargs['png']:
        extract_frame(path_to)
    print(time.time() - st)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("directory",
                            help='Directory with folders inp, mar',
                            metavar='path_to_directory')

    keys = arg_parser.add_argument_group('keys')
    keys.add_argument('--json', '-j',
                      help='Extract non-empty frames from directory/mar/.../.../*.xml '
                           'to directory/jsn/.../.../xxx.yyy.yyy.{right, left}.{frame_number}.json',
                      action='store_true')
    keys.add_argument('--png', '-p',
                      help='Extract non-empty frames from videos to png files',
                      action='store_true')

    args = arg_parser.parse_args()
    if os.path.isdir(args.directory):
        _main(dir=args.directory,
              jsn=args.json,
              png=args.png)
    else:
        raise NotADirectoryError(f"{args.directory} не является директорией!")
