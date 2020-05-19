"""Classes capable of reading and writing collections
"""

from collections import OrderedDict
import logging

from fiona.ogrext import MemoryFileBase
from fiona.collection import Collection
from fiona.ogrext import _listdir

from fiona.drvsupport import memoryfile_supports_mode
from fiona.errors import FionaValueError, DriverError
from fiona.path import ARCHIVESCHEMES
from fiona.env import GDALVersion

log = logging.getLogger(__name__)
gdal_version = GDALVersion.runtime()


class MemoryFile(MemoryFileBase):
    """A BytesIO-like object, backed by an in-memory file.

    This allows formatted files to be read and written without I/O.

    A MemoryFile created with initial bytes becomes immutable. A
    MemoryFile created without initial bytes may be written to using
    either file-like or dataset interfaces.

    Examples
    --------

    """
    def __init__(self, file_or_bytes=None, filename=None, ext=''):
        super(MemoryFile, self).__init__(
            file_or_bytes=file_or_bytes, filename=filename, ext=ext)

    def open(self, mode=None, driver=None, schema=None, crs=None, encoding=None,
             layer=None, enabled_drivers=None, crs_wkt=None,
             **kwargs):
        """Open the file and return a Fiona collection object.

        If data has already been written, the file is opened in 'r'
        mode. Otherwise, the file is opened in 'w' mode.

        Parameters
        ----------
        Note well that there is no `path` parameter: a `MemoryFile`
        contains a single dataset and there is no need to specify a
        path.

        Other parameters are optional and have the same semantics as the
        parameters of `fiona.open()`.
        """
        vsi_path = self.name

        if self.closed:
            raise IOError("I/O operation on closed file.")

        if self.exists():
            if mode is None or mode == 'r':
                mode = 'r'
            else:
                mode = 'a'
        else:

            if schema:
                # Make an ordered dict of schema properties.
                this_schema = schema.copy()
                this_schema['properties'] = OrderedDict(schema['properties'])
            else:
                this_schema = None
            schema = this_schema

            mode = 'w'

        if not memoryfile_supports_mode(driver, mode):
            raise DriverError("{driver} driver does not support mode '{mode}'.".format(driver=driver,
                                                                                       mode=mode))

        return Collection(vsi_path, mode=mode, driver=driver, schema=schema, crs=crs,
                          encoding=encoding, layer=layer, enabled_drivers=enabled_drivers,
                          crs_wkt=crs_wkt, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()


class ZipMemoryFile(MemoryFile):
    """A read-only BytesIO-like object backed by an in-memory zip file.

    This allows a zip file containing formatted files to be read
    without I/O.
    """

    def __init__(self, file_or_bytes=None, ext='zip'):
        super(ZipMemoryFile, self).__init__(file_or_bytes, ext=ext)

        if ext in ARCHIVESCHEMES:
            self.vsi = '/vsi{}/'.format(ARCHIVESCHEMES[ext])
        else:
            raise FionaValueError("Extension {ext} is not one of the supported extensions ({extensions}).".format(
                ext=ext,
                extensions=', '.join(ARCHIVESCHEMES.keys())
            ))

    def open(self, path, mode=None, driver=None, schema=None, crs=None, encoding=None,
             layer=None, enabled_drivers=None, crs_wkt=None, **kwargs):
        """Open a dataset within the zipped stream.

        Parameters
        ----------
        path : str
            Path to a dataset in the zip file, relative to the root of the
            archive.

        Returns
        -------
        A Fiona collection object
        """
        vsi_path = '{vsi}{vsipath}/{path}'.format(vsi=self.vsi,
                                                  vsipath=self.name,
                                                  path=path.lstrip('/'))

        if mode is None:
            mode = 'r'

        if ((mode == 'w' and self.vsi == '/vsitar/') or
                (mode == 'a')):
            raise FionaValueError("GDAL Virtual File System {vsi} does not support mode '{mode}'.".format(vsi=self.vsi,
                                                                                                          mode=mode))

        # DGN: segfault with gdal 3.0.4
        # GPKG,DXF,ESRI Shapefile,GPX,MapInfo File,PCIDSK': Random access not supported for writable file in /vsizip
        # GMT: Random access not supported for /vsizip for gdal 1.x
        # GPSTrackMaker: VSIFSeekL() is not supported on writable Zip files
        if mode == 'w' and driver in {'DGN', 'GPKG', 'DXF', 'ESRI Shapefile', 'GPX', 'MapInfo File', 'PCIDSK',
                                      'GPSTrackMaker'}:
            raise FionaValueError("Driver {driver} does not support mode '{mode}' for ZipMemoryFile.".format(
                driver=driver, mode=mode))

        if self.closed:
            raise IOError("I/O operation on closed file.")

        return Collection(vsi_path, mode=mode, crs=crs, driver=driver, schema=schema, encoding=encoding,
                          layer=layer, enabled_drivers=enabled_drivers, crs_wkt=crs_wkt, **kwargs)

    def listdir(self, path='/'):
        """ List all files in a directory"""
        vsi_path = '{vsi}{vsipath}/{path}'.format(vsi=self.vsi,
                                                  vsipath=self.name,
                                                  path=path.lstrip('/'))
        return _listdir(vsi_path)
