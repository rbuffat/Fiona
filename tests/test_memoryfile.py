"""Tests of MemoryFile and ZippedMemoryFile"""

from io import BytesIO
import pytest
import uuid
import fiona
from fiona.io import MemoryFile, ZipMemoryFile
from fiona.drvsupport import supported_drivers, driver_mode_mingdal
from fiona.env import GDALVersion

gdal_version = GDALVersion.runtime()


@pytest.fixture(scope='session')
def profile_first_coutwildrnp_shp(path_coutwildrnp_shp):
    with fiona.open(path_coutwildrnp_shp) as col:
        return col.profile, next(iter(col))


def test_memoryfile(path_coutwildrnp_json):
    """In-memory GeoJSON file can be read"""
    with open(path_coutwildrnp_json, 'rb') as f:
        data = f.read()
    with MemoryFile(data) as memfile:
        with memfile.open() as collection:
            assert len(collection) == 67


def test_zip_memoryfile(bytes_coutwildrnp_zip):
    """In-memory zipped Shapefile can be read"""
    with ZipMemoryFile(bytes_coutwildrnp_zip) as memfile:
        with memfile.open('coutwildrnp.shp') as collection:
            assert len(collection) == 67


def test_write_memoryfile(profile_first_coutwildrnp_shp):
    """In-memory Shapefile can be written"""
    profile, first = profile_first_coutwildrnp_shp
    profile['driver'] = 'GeoJSON'
    with MemoryFile() as memfile:
        with memfile.open(**profile) as col:
            col.write(first)
        memfile.seek(0)
        data = memfile.read()

    with MemoryFile(data) as memfile:
        with memfile.open() as col:
            assert len(col) == 1


@pytest.mark.parametrize('driver', [driver for driver in ['GeoJSON', 'GPKG', 'ESRI Shapefile'] if (
        'a' in supported_drivers[driver] and driver not in driver_mode_mingdal['a'] or
        gdal_version >= GDALVersion(*driver_mode_mingdal['w'][driver][:2]))])
def test_append_memoryfile(driver):
    """In-memory Shapefile can be appended"""
    schema = {'geometry': 'Point', 'properties': [('position', 'int')]}
    records1 = [{'geometry': {'type': 'Point', 'coordinates': (0.0, float(i))}, 'properties': {'position': i}} for i in
                range(0, 5)]
    records2 = [{'geometry': {'type': 'Point', 'coordinates': (0.0, float(i))}, 'properties': {'position': i}} for i in
                range(5, 10)]
    positions = list(range(0, 10))

    filename = None
    # TODO ESRI Shapefile needs extension, otherwise MemoryFile.exists() is always False
    if driver == 'ESRI Shapefile':
        filename = "inmemory.shp"

    with MemoryFile(filename=filename) as memfile:
        with memfile.open(driver=driver, schema=schema) as c:
            c.writerecords(records1)
        with memfile.open(driver=driver, schema=schema, mode='a') as c:
            c.writerecords(records2)
        with memfile.open(driver=driver) as c:
            items = list(c)
            assert len(items) == len(positions)
            for val_in, val_out in zip(positions, items):
                assert val_in == int(val_out['properties']['position'])


def test_memoryfile_bytesio(path_coutwildrnp_json):
    """In-memory GeoJSON file can be read"""
    with open(path_coutwildrnp_json, 'rb') as f:
        data = f.read()

    with fiona.open(BytesIO(data)) as collection:
        assert len(collection) == 67


def test_memoryfile_fileobj(path_coutwildrnp_json):
    """In-memory GeoJSON file can be read"""
    with open(path_coutwildrnp_json, 'rb') as f:

        with fiona.open(f) as collection:
            assert len(collection) == 67


def test_memoryfilebase_write():
    """Test MemoryFileBase.write """

    schema = {'geometry': 'Point', 'properties': [('position', 'int')]}
    records = [{'geometry': {'type': 'Point', 'coordinates': (0.0, float(i))}, 'properties': {'position': i}} for i in
               range(5)]

    with MemoryFile() as memfile:

        with BytesIO() as fout:
            with fiona.open(fout,
                            'w',
                            driver="GeoJSON",
                            schema=schema) as c:
                c.writerecords(records)
            fout.seek(0)
            data = fout.read()

        assert memfile.tell() == 0
        memfile.write(data)

        with memfile.open(driver="GeoJSON",
                          schema=schema) as c:
            record_positions = [int(f['properties']['position']) for f in c]
            assert record_positions == list(range(5))
