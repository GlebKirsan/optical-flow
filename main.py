import argparse
import os

from src.common import build_excepting_dirs
from src.parse_xml import create_json_with_frame_data
from src.get_frame import extract_frame
from src.opt_flow import calc_opt_flow


def _main(**kwargs):
    path_to = build_excepting_dirs(kwargs['dir'])
    if kwargs['jsn']:
        create_json_with_frame_data(path_to)
    if kwargs['png']:
        extract_frame(path_to)
    if kwargs['opt']:
        calc_opt_flow(path_to)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("directory",
                            help='Directory with folders inp, mar',
                            metavar='path_to_directory')

    keys = arg_parser.add_argument_group('keys')
    keys.add_argument('--json', '-j',
                      help='Extract non-empty frames from '
                           'directory/mar/.../.../*.xml '
                           'to directory/jsn/.../.../*.json',
                      action='store_true')
    keys.add_argument('--png', '-p',
                      help='Extract non-empty frames from videos to png files',
                      action='store_true')
    keys.add_argument('--optic', '-o',
                      help='Calculate optical flow for existing frames in png',
                      action='store_true')

    args = arg_parser.parse_args()
    if os.path.isdir(args.directory):
        _main(dir=args.directory,
              jsn=args.json,
              png=args.png,
              opt=args.optic)
    else:
        raise NotADirectoryError(f"{args.directory} не является директорией!")
