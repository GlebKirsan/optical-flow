import time
import argparse
import os
from mypackage import parse_xml, get_frame, helping, opt_flow


def _main(**kwargs):
    st = time.time()
    path_to = helping.build_dirs(kwargs['dir'])
    if kwargs['jsn']:
        parse_xml.frame_info_to_json(path_to)
    if kwargs['png']:
        get_frame.extract_frame(path_to)
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
