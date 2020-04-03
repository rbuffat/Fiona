import glob
import os
import logging
import contextlib
import platform
import sys

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

# With Python >= 3.8 on Windows directories in PATH are not automatically
# searched for DLL dependencies and must be added manually with
# os.add_dll_directory.
# see https://github.com/Toblerity/Fiona/issues/851

dll_directory = None


def directory_contains_gdal_dll(path):
    """ Checks if a directory contains a gdal dll """
    return len(glob.glob(os.path.join(path, "gdal*.dll"))) > 0


def search_gdal_dll_directory():
    """ Search for gdal dlls

        Checks if a */*gdal*/* directory is present in PATH
        and contains a gdal*.dll file.
        If none is found, GDAL_HOME is used if available.
    """

    _dll_directory = None

    # Parse PATH for gdal/bin
    for path in os.getenv('PATH', '').split(os.pathsep):

        if "gdal" in path.lower() and directory_contains_gdal_dll(path):
            _dll_directory = path
            break

    # Use GDAL_HOME if present
    if _dll_directory is None:

        gdal_home = os.getenv('GDAL_HOME', None)

        if gdal_home is not None and os.path.exists(gdal_home):

            if directory_contains_gdal_dll(gdal_home):
                _dll_directory = gdal_home
            elif directory_contains_gdal_dll(os.path.join(gdal_home, "bin")):
                _dll_directory = os.path.join(gdal_home, "bin")

        elif gdal_home is not None and not os.path.exists(gdal_home):
            log.warning("GDAL_HOME directory ({}) does not exist.".format(gdal_home))

    if _dll_directory is None:
        log.warning("No dll directory found.")

    return _dll_directory


if platform.system() == 'Windows' and (3, 8) <= sys.version_info:
    dll_directory = search_gdal_dll_directory()


@contextlib.contextmanager
def add_gdal_dll_directory():

    cm = os.add_dll_directory(dll_directory) if dll_directory is not None else contextlib.nullcontext()

    try:

        yield cm

    finally:

        if dll_directory is not None:
            cm.close()
