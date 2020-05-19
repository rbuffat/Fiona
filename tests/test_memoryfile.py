"""Tests of MemoryFile and ZippedMemoryFile"""
from collections import OrderedDict
from io import BytesIO
import pytest
import fiona
from fiona.errors import FionaValueError
from fiona.io import MemoryFile, ZipMemoryFile
from fiona.drvsupport import supported_drivers, driver_mode_mingdal
from fiona.env import GDALVersion
from fiona.path import ARCHIVESCHEMES
from tests.conftest import driver_extensions
import pprint

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


def test_zip_memoryfile_listdir(bytes_coutwildrnp_zip):
    """In-memory zipped Shapefile can be read"""

    with ZipMemoryFile(bytes_coutwildrnp_zip) as memfile:
        assert set(memfile.listdir('/')) == {'coutwildrnp.shp', 'coutwildrnp.shx', 'coutwildrnp.dbf', 'coutwildrnp.prj'}


def test_tar_memoryfile_listdir(bytes_coutwildrnp_tar):
    """In-memory zipped Shapefile can be read"""

    with ZipMemoryFile(bytes_coutwildrnp_tar, ext='tar') as memfile:
        assert set(memfile.listdir('/testing')) == {'coutwildrnp.shp', 'coutwildrnp.shx', 'coutwildrnp.dbf', 'coutwildrnp.prj'}


@pytest.mark.parametrize('ext', ARCHIVESCHEMES.keys())
def test_zip_memoryfile_write(ext):
    schema = {'geometry': 'Point', 'properties': OrderedDict([('position', 'int')])}
    records1 = [{'geometry': {'type': 'Point', 'coordinates': (0.0, float(i))}, 'properties': {'position': i}} for i in
                range(0, 5)]
    records2 = [{'geometry': {'type': 'Point', 'coordinates': (0.0, float(i))}, 'properties': {'position': i}} for i in
                range(5, 10)]

    # \vsitar\ does not allow write mode
    if ARCHIVESCHEMES[ext] == 'tar':
        with pytest.raises(FionaValueError):
            with ZipMemoryFile(ext=ext) as memfile:
                with memfile.open(path="/test1.geojson", mode='w', driver='GeoJSON', schema=schema) as c:
                    c.writerecords(records1)
    else:
        with ZipMemoryFile(ext=ext) as memfile:
            with memfile.open(path="/test1.geojson", mode='w', driver='GeoJSON', schema=schema) as c:
                c.writerecords(records1)
            with memfile.open(path="/test2.geojson", mode='w', driver='GeoJSON', schema=schema) as c:
                c.writerecords(records2)

            with memfile.open(path="/test1.geojson", mode='r', driver='GeoJSON', schema=schema) as c:
                items = list(c)
                assert len(items) == len(range(0, 5))
                for val_in, val_out in zip(range(0, 5), items):
                    assert val_in == int(val_out['properties']['position'])

            with memfile.open(path="/test2.geojson", mode='r', driver='GeoJSON', schema=schema) as c:
                items = list(c)
                assert len(items) == len(range(5, 10))
                for val_in, val_out in zip(range(5, 10), items):
                    assert val_in == int(val_out['properties']['position'])


@pytest.mark.parametrize('ext', ARCHIVESCHEMES.keys())
def test_zip_memoryfile_write_directory(ext):
    schema = {'geometry': 'Point', 'properties': OrderedDict([('position', 'int')])}
    records1 = [{'geometry': {'type': 'Point', 'coordinates': (0.0, float(i))}, 'properties': {'position': i}} for i in
                range(0, 5)]
    records2 = [{'geometry': {'type': 'Point', 'coordinates': (0.0, float(i))}, 'properties': {'position': i}} for i in
                range(5, 10)]

    # \vsitar\ does not allow write mode
    if ARCHIVESCHEMES[ext] == 'tar':
        with pytest.raises(FionaValueError):
            with ZipMemoryFile(ext=ext) as memfile:
                with memfile.open(path="/dir1/test1.geojson", mode='w', driver='GeoJSON', schema=schema) as c:
                    c.writerecords(records1)
    else:
        with ZipMemoryFile(ext=ext) as memfile:
            with memfile.open(path="/dir1/test1.geojson", mode='w', driver='GeoJSON', schema=schema) as c:
                c.writerecords(records1)
            with memfile.open(path="/dir2/test2.geojson", mode='w', driver='GeoJSON', schema=schema) as c:
                c.writerecords(records2)

            with memfile.open(path="/dir1/test1.geojson", mode='r', driver='GeoJSON', schema=schema) as c:
                items = list(c)
                assert len(items) == len(range(0, 5))
                for val_in, val_out in zip(range(0, 5), items):
                    assert val_in == int(val_out['properties']['position'])

            with memfile.open(path="/dir2/test2.geojson", mode='r', driver='GeoJSON', schema=schema) as c:
                items = list(c)
                assert len(items) == len(range(5, 10))
                for val_in, val_out in zip(range(5, 10), items):
                    assert val_in == int(val_out['properties']['position'])


@pytest.mark.parametrize('ext', ARCHIVESCHEMES.keys())
def test_zip_memoryfile_append(ext):

    with pytest.raises(FionaValueError):
        schema = {'geometry': 'Point', 'properties': OrderedDict([('position', 'int')])}
        records1 = [{'geometry': {'type': 'Point', 'coordinates': (0.0, float(i))}, 'properties': {'position': i}} for i in
                    range(0, 5)]
        records2 = [{'geometry': {'type': 'Point', 'coordinates': (0.0, float(i))}, 'properties': {'position': i}} for i in
                    range(5, 10)]
        with ZipMemoryFile(ext=ext) as memfile:
            with memfile.open(path="/test1.geojson", mode='w', driver='GeoJSON', schema=schema) as c:
                c.writerecords(records1)

            with memfile.open(path="/test1.geojson", mode='a', driver='GeoJSON', schema=schema) as c:
                c.writerecords(records2)

            with memfile.open(path="/test1.geojson", mode='r', driver='GeoJSON', schema=schema) as c:
                items = list(c)
                assert len(items) == len(range(0, 10))
                for val_in, val_out in zip(range(0, 10), items):
                    assert val_in == int(val_out['properties']['position'])


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


@pytest.mark.parametrize('driver', [driver for driver, raw in supported_drivers.items() if 'a' in raw and (
                                            driver not in driver_mode_mingdal['a'] or
                                            gdal_version >= GDALVersion(*driver_mode_mingdal['a'][driver][:2]))
                                    and driver not in {'DGN'}])
def test_append_memoryfile(driver):
    """In-memory Shapefile can be appended"""

    special_schemas = {'CSV': {'geometry': None, 'properties': OrderedDict([('position', 'int')])}}
    schema = special_schemas.get(driver, {'geometry': 'Point', 'properties': OrderedDict([('position', 'int')])})

    range1 = list(range(0, 5))
    special_records1 = {'CSV': [{'geometry': None, 'properties': {'position': i}} for i in range1]}
    records1 = special_records1.get(driver, [
        {'geometry': {'type': 'Point', 'coordinates': (0.0, float(i))}, 'properties': {'position': i}} for i in
        range1])

    range2 = list(range(5, 10))
    special_records2 = {'CSV': [{'geometry': None, 'properties': {'position': i}} for i in range2]}
    records2 = special_records2.get(driver, [
        {'geometry': {'type': 'Point', 'coordinates': (0.0, float(i))}, 'properties': {'position': i}} for i in
        range2])

    positions = range1 + range2

    if (driver == 'GPKG' and gdal_version < GDALVersion(2, 0) or
            driver in {'PCIDSK', 'MapInfo File'}):
        # Test fails with sqlite3_open(/vsimem/...) failed: out of memory for gdal 1.x
        with pytest.raises(FionaValueError):
            with MemoryFile(ext=driver_extensions.get(driver, '')) as memfile:
                with memfile.open(driver=driver, schema=schema) as c:
                    c.writerecords(records1)
                with memfile.open(driver=driver, schema=schema, mode='a') as c:
                    c.writerecords(records2)
    else:
        #  Shapfile needs file extensions so that exists() returns True
        #  GPKG requires extensions for gdal 2.0, otherwise sqlite driver is used
        with MemoryFile(ext=driver_extensions.get(driver, '')) as memfile:
            with memfile.open(driver=driver, schema=schema) as c:
                c.writerecords(records1)
            with memfile.open(driver=driver, schema=schema, mode='a') as c:
                c.writerecords(records2)
            with memfile.open(driver=driver) as c:
                items = list(c)
                pprint.pprint(items)
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
