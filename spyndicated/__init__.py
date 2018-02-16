import os

__all__ = ['usr', 'run', 'tests', 'utils', 'rss', 'plugins', 'gui']


def get_config(filename):
    CONFIG_PATH = os.path.abspath(os.path.join(os.getcwd(), ".config"))
    filepath = os.path.join(CONFIG_PATH, filename)
    if os.path.isfile(filepath) or os.path.isdir(filepath):
        return filepath
    else:
        raise FileNotFoundError("CONFIG FILE ERROR! File/Subdirectory not found.")


def get_data(filename):
    DATA_PATH = os.path.abspath(os.path.join(os.getcwd(), '.data'))
    filepath = os.path.join(DATA_PATH, filename)
    if os.path.isfile(filepath) or os.path.isdir(filepath):
        return filepath
    else:
        with open(filepath, mode='w') as f:
            f.close()
        return filepath
