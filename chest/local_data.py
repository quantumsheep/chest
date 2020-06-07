import sys
import pathlib


def __get_datadir() -> pathlib.Path:
    home = pathlib.Path.home()

    if sys.platform == "win32":
        return home / "AppData/Roaming"
    elif sys.platform.startswith('linux'):
        return home / ".local/share"
    elif sys.platform == "darwin":
        return home / "Library/Application Support"


def appdir(path: str = '') -> pathlib.Path:
    if not path.startswith('/'):
        path = '/' + path

    dirpath = __get_datadir() / ("chest" + path)

    dirpath.mkdir(parents=True, exist_ok=True)

    return dirpath


def appfile(filename: str, path: str = '', create=True) -> pathlib.Path:
    if filename.startswith('/'):
        filename = filename[1::]

    filepath = appdir(path) / filename

    if create:
        filepath.touch(exist_ok=True)

    return filepath
