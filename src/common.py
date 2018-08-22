import os


def get_frame_num_from_filename(filename: str) -> int:

    """
    Получает номер кадра из названия файла
    :param filename: xxx.yyy.1234.left.000125.ext
    :return: 125

    """
    return int(filename.split('.')[4])


def get_file_prefix(name: str) -> str:

    """
    :param name: Название файла из которого нужно получить префикс.
    Например - xxx.yyy.1234.left.avi
    :return: Префикс файла вида xxx.yyy.1234.left

    """
    end_of_prefix = 4
    return '.'.join(name.split('.')[:end_of_prefix])


def build_excepting_dirs(directory) -> dict:
    """
    Сохранение путей до имеющихся директорий и создание недостающих
    :param directory: Директория с папками inp, mar
    :return: Словарь с путями до папок

    """
    files = os.listdir(directory)

    path_to = {
        file_name: os.path.join(directory, file_name) for file_name in files
        if os.path.isdir(os.path.join(directory, file_name))
    }

    for i in ['opt', 'jsn', 'png']:

        if i not in path_to:
            new_dir = os.path.join(directory, i)
            os.mkdir(new_dir)
            path_to[i] = new_dir

    path_to['parent'] = os.getcwd()
    return path_to


def make_path_from_name(file_name: str, path_to):
    """
    :param file_name: series.season.episode.{left,right}.*
    :param path_to: series/folder
    :return: series/folder/series.season/series.season.episode.{left,right}.*
    """
    file_name = file_name.split('.')
    folder = '.'.join(file_name[:2])
    sub_folder = '.'.join(file_name[:4])
    return os.path.join(path_to, folder, sub_folder)
