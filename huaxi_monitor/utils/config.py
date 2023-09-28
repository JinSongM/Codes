import os


def mkdir(fil_path):
    if not os.path.exists(os.path.dirname(fil_path)):
        os.makedirs(os.path.dirname(fil_path))


def file_exits(file_path):
    return os.path.exists(file_path)


def makedir(file_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
