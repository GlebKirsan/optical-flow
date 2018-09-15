import os


def get_frame_num_from_filename(filename: str) -> int:

    """
    Получает номер кадра из названия файла.

    :param filename: Имя файла, в котором есть номер кадра.
    :return: Число, номер кадра из названия.

    """
    return int(filename.split('.')[4])


def get_file_prefix(name: str) -> str:

    """
    Например - xxx.yyy.1234.left.avi.

    :param name: Название файла из которого нужно получить префикс.
    :return: Префикс файла вида xxx.yyy.1234.left

    """
    end_of_prefix = 4
    return '.'.join(name.split('.')[:end_of_prefix])


def build_excepting_dirs(directory) -> dict:
    """
    Сохранение путей до имеющихся директорий и создание недостающих.

    :param directory: Директория с папками inp, mar.
    :return: Словарь с путями до папок.

    """
    files = os.listdir(directory)

    path_to = {
        file_name: os.path.join(directory, file_name) for file_name in files
        if os.path.isdir(os.path.join(directory, file_name))
    }

    for i in ['opt', 'jsn', 'png', 'viz', 'logs']:

        if i not in path_to:
            new_dir = os.path.join(directory, i)
            os.mkdir(new_dir)
            path_to[i] = new_dir

    path_to['parent'] = os.getcwd()
    return path_to


def make_path_from_name(file_name: str, path_to):
    """
    Функция строит директорию для данного файла в другой папке.

    :param file_name: series.season.episode.{left,right}.*
    :param path_to: series/folder
    :return: series/folder/series.season/series.season.episode.{left,right}.*

    """
    sub_folder = get_file_prefix(file_name)
    file_name = file_name.split('.')
    folder = '.'.join(file_name[:2])
    return os.path.join(path_to, folder, sub_folder)
