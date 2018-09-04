import os
import argparse
import logging
import time

from src.common import build_excepting_dirs
from src.parse_xml import create_json_with_frame_data
from src.get_frame import extract_frame
from src.opt_flow import calc_opt_flow

def parse_args():
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
                      help='Extract non-empty frames from videos to png files.',
                      action='store_true')
    keys.add_argument('--optic', '-o',
                      help='Calculate optical flow for existing frames in png.',
                      action='store_true')
    keys.add_argument('--verbose', '-v',
                      help='Enable verbosity.',
                      action='store_true')
    keys.add_argument('--vertical',
                      help='Concatenate optical flow and clear frame in one image.'
                           'vertically.',
                      action='store_true')

    return arg_parser.parse_args()


def _main(args):
    path_to = build_excepting_dirs(args.directory)
    verbose = args.verbose
    if verbose:
        today = time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime())
        log_file = os.path.join(path_to['logs'], f'{today}_logs.log')
        logging.basicConfig(level=logging.INFO,
                            filename=log_file,
                            filemode='w',
                            style='{',
                            format='{message}')
        logging.info(args)

    if args.json:
        create_json_with_frame_data(path_to)

    if args.png:
        extract_frame(path_to)

    if args.optic:
        calc_opt_flow(path_to, args.vertical)


if __name__ == "__main__":
    args = parse_args()
    if os.path.isdir(args.directory):
        _main(args)
    else:
        raise NotADirectoryError(f"{args.directory} не является директорией!")

