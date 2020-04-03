import glob
import os
import logging
from contextlib import contextmanager

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def directory_contains_gdal_dll(path):
    """ Checks if a directory contains a gdal dll """
    return len(glob.glob(os.path.join(path, "gdal*.dll"))) > 0


def search_gdal_dll_directory():
    """ Search for gdal dlls

        Checks if a */*gdal*/* directory is present in PATH
        and contains a gdal*.dll file.
        If none is found, GDAL_HOME is used if available.
    """

    dll_directory = None

    # Parse PATH for gdal/bin
    for path in os.getenv('PATH', '').split(os.pathsep):

        if "gdal" in path.lower() and directory_contains_gdal_dll(path):
            dll_directory = path
            break

    # Use GDAL_HOME if present
    if dll_directory is None:

        gdal_home = os.getenv('GDAL_HOME', None)

        if gdal_home is not None and os.path.exists(gdal_home):

            if directory_contains_gdal_dll(gdal_home):
                dll_directory = gdal_home
            elif directory_contains_gdal_dll(os.path.join(gdal_home, "bin")):
                dll_directory = os.path.join(gdal_home, "bin")

        elif gdal_home is not None and not os.path.exists(gdal_home):
            log.warning("GDAL_HOME directory ({}) does not exist.".format(gdal_home))

    dll_directory = None
    return dll_directory


dll_directory = search_gdal_dll_directory()


@contextmanager
def add_gdal_dll_directory():

    if dll_directory is None:
        log.warning("No DLL direcotry was added")

    f = os.add_dll_directory(dll_directory)
    yield f
    f.close()
