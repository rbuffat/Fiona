"""
See also test_rfc3339.py for datetime parser tests.
"""
import os
import re
import shutil
import tempfile
from collections import OrderedDict

import fiona
import pytest

from fiona.errors import DriverSupportError
from fiona.rfc3339 import parse_time
from .conftest import get_temp_filename, requires_gpkg
from fiona.env import GDALVersion
import datetime
from fiona.drvsupport import (supported_drivers, driver_mode_mingdal, driver_converts_field_type_silently_to_str,
                              driver_supports_field, driver_converts_to_str, driver_supports_timezones,
                              drivers_not_supporting_milliseconds)
from fiona._env import calc_gdal_version_num, get_gdal_version_num

gdal_version = GDALVersion.runtime()

GDAL_MAJOR_VER = fiona.get_gdal_version_num() // 1000000

GEOMETRY_TYPE = "Point"
GEOMETRY_EXAMPLE = {"type": "Point", "coordinates": [1, 2]}

DRIVER_FILENAME = {
    "ESRI Shapefile": "test.shp",
    "GPKG": "test.gpkg",
    "GeoJSON": "test.geojson",
    "MapInfo File": "test.tab",
}

DATE_EXAMPLE = "2018-03-25"
DATETIME_EXAMPLE = "2018-03-25T22:49:05"
TIME_EXAMPLE = "22:49:05"


class TestDateFieldSupport:
    def write_data(self, driver):
        filename = DRIVER_FILENAME[driver]
        temp_dir = tempfile.mkdtemp()
        path = os.path.join(temp_dir, filename)
        schema = {
            "geometry": GEOMETRY_TYPE,
            "properties": {
                "date": "date",
            }
        }
        records = [
            {
                "geometry": GEOMETRY_EXAMPLE,
                "properties": {
                    "date": DATE_EXAMPLE,
                }
            },
            {
                "geometry": GEOMETRY_EXAMPLE,
                "properties": {
                    "date": None,
                }
            },
        ]
        with fiona.Env(), fiona.open(path, "w", driver=driver, schema=schema) as collection:
            collection.writerecords(records)

        with fiona.Env(), fiona.open(path, "r") as collection:
            schema = collection.schema
            features = list(collection)

        shutil.rmtree(temp_dir)

        return schema, features

    def test_shapefile(self):
        driver = "ESRI Shapefile"
        schema, features = self.write_data(driver)

        assert schema["properties"]["date"] == "date"
        assert features[0]["properties"]["date"] == DATE_EXAMPLE
        assert features[1]["properties"]["date"] is None

    @requires_gpkg
    def test_gpkg(self):
        driver = "GPKG"
        schema, features = self.write_data(driver)

        assert schema["properties"]["date"] == "date"
        assert features[0]["properties"]["date"] == DATE_EXAMPLE
        assert features[1]["properties"]["date"] is None

    def test_geojson(self):
        # GDAL 1: date field silently converted to string
        # GDAL 1: date string format uses / instead of -
        driver = "GeoJSON"
        schema, features = self.write_data(driver)

        if GDAL_MAJOR_VER >= 2:
            assert schema["properties"]["date"] == "date"
            assert features[0]["properties"]["date"] == DATE_EXAMPLE
        else:
            assert schema["properties"]["date"] == "str"
            assert features[0]["properties"]["date"] == "2018/03/25"
        assert features[1]["properties"]["date"] is None

    def test_mapinfo(self):
        driver = "MapInfo File"
        schema, features = self.write_data(driver)

        assert schema["properties"]["date"] == "date"
        assert features[0]["properties"]["date"] == DATE_EXAMPLE
        assert features[1]["properties"]["date"] is None


class TestDatetimeFieldSupport:
    def write_data(self, driver):
        filename = DRIVER_FILENAME[driver]
        temp_dir = tempfile.mkdtemp()
        path = os.path.join(temp_dir, filename)
        schema = {
            "geometry": GEOMETRY_TYPE,
            "properties": {
                "datetime": "datetime",
            }
        }
        records = [
            {
                "geometry": GEOMETRY_EXAMPLE,
                "properties": {
                    "datetime": DATETIME_EXAMPLE,
                }
            },
            {
                "geometry": GEOMETRY_EXAMPLE,
                "properties": {
                    "datetime": None,
                }
            },
        ]
        with fiona.Env(), fiona.open(path, "w", driver=driver, schema=schema) as collection:
            collection.writerecords(records)

        with fiona.Env(), fiona.open(path, "r") as collection:
            schema = collection.schema
            features = list(collection)

        shutil.rmtree(temp_dir)

        return schema, features

    def test_shapefile(self):
        # datetime is silently converted to date
        driver = "ESRI Shapefile"

        with pytest.raises(DriverSupportError):
            schema, features = self.write_data(driver)

        # assert schema["properties"]["datetime"] == "date"
        # assert features[0]["properties"]["datetime"] == "2018-03-25"
        # assert features[1]["properties"]["datetime"] is None

    @requires_gpkg
    def test_gpkg(self):
        # GDAL 1: datetime silently downgraded to date
        driver = "GPKG"

        if GDAL_MAJOR_VER >= 2:
            schema, features = self.write_data(driver)
            assert schema["properties"]["datetime"] == "datetime"
            assert features[0]["properties"]["datetime"] == '2018-03-25T22:49:05+00:00'
            assert features[1]["properties"]["datetime"] is None
        else:
            with pytest.raises(DriverSupportError):
                schema, features = self.write_data(driver)

    def test_geojson(self):
        # GDAL 1: datetime silently converted to string
        # GDAL 1: date string format uses / instead of -
        driver = "GeoJSON"
        schema, features = self.write_data(driver)

        if GDAL_MAJOR_VER >= 2:
            assert schema["properties"]["datetime"] == "datetime"
            assert features[0]["properties"]["datetime"] == DATETIME_EXAMPLE
        else:
            assert schema["properties"]["datetime"] == "str"
            assert features[0]["properties"]["datetime"] == "2018/03/25 22:49:05"
        assert features[1]["properties"]["datetime"] is None

    def test_mapinfo(self):
        driver = "MapInfo File"
        schema, features = self.write_data(driver)

        assert schema["properties"]["datetime"] == "datetime"
        assert features[0]["properties"]["datetime"] == DATETIME_EXAMPLE
        assert features[1]["properties"]["datetime"] is None


class TestTimeFieldSupport:
    def write_data(self, driver):
        filename = DRIVER_FILENAME[driver]
        temp_dir = tempfile.mkdtemp()
        path = os.path.join(temp_dir, filename)
        schema = {
            "geometry": GEOMETRY_TYPE,
            "properties": {
                "time": "time",
            }
        }
        records = [
            {
                "geometry": GEOMETRY_EXAMPLE,
                "properties": {
                    "time": TIME_EXAMPLE,
                }
            },
            {
                "geometry": GEOMETRY_EXAMPLE,
                "properties": {
                    "time": None,
                }
            },
        ]
        with fiona.Env(), fiona.open(path, "w", driver=driver, schema=schema) as collection:
            collection.writerecords(records)

        with fiona.Env(), fiona.open(path, "r") as collection:
            schema = collection.schema
            features = list(collection)

        shutil.rmtree(temp_dir)

        return schema, features

    def test_shapefile(self):
        # no support for time fields
        driver = "ESRI Shapefile"
        with pytest.raises(DriverSupportError):
            self.write_data(driver)

    @requires_gpkg
    def test_gpkg(self):
        # GDAL 2: time field is silently converted to string
        # GDAL 1: time field dropped completely
        driver = "GPKG"

        if GDAL_MAJOR_VER < 2:
            with pytest.raises(DriverSupportError):
                schema, features = self.write_data(driver)
        else:
            with pytest.warns(UserWarning) as record:
                schema, features = self.write_data(driver)
            assert len(record) == 1
            assert "silently converts" in record[0].message.args[0]

        # if GDAL_MAJOR_VER >= 2:
        #     assert schema["properties"]["time"] == "str"
        #     assert features[0]["properties"]["time"] == TIME_EXAMPLE
        #     assert features[1]["properties"]["time"] is None
        # else:
        #     assert "time" not in schema["properties"]

    def test_geojson(self):
        # GDAL 1: time field silently converted to string
        driver = "GeoJSON"
        schema, features = self.write_data(driver)

        if GDAL_MAJOR_VER >= 2:
            assert schema["properties"]["time"] == "time"
        else:
            assert schema["properties"]["time"] == "str"
        assert features[0]["properties"]["time"] == TIME_EXAMPLE
        assert features[1]["properties"]["time"] is None

    def test_mapinfo(self):
        # GDAL 2: null time is converted to 00:00:00 (regression?)
        driver = "MapInfo File"
        schema, features = self.write_data(driver)

        assert schema["properties"]["time"] == "time"
        assert features[0]["properties"]["time"] == TIME_EXAMPLE
        if GDAL_MAJOR_VER >= 2:
            assert features[1]["properties"]["time"] == "00:00:00"
        else:
            assert features[1]["properties"]["time"] is None


def get_schema(driver, field_type):
    if driver == 'GPX':
        return {'properties': OrderedDict([('ele', 'float'),
                                           ('time', field_type)]),
                'geometry': 'Point'}
    if driver == 'GPSTrackMaker':
        return {
            'properties': OrderedDict([('name', 'str'), ('comment', 'str'), ('icon', 'int'), ('time', field_type)]),
            'geometry': 'Point'}

    return {"geometry": "Point",
            "properties": {"datefield": field_type}}


def get_records(driver, values):
    if driver == 'GPX':
        return [{"geometry": {"type": "Point", "coordinates": [1, 2]},
                 "properties": {'ele': 0, "time": val}} for val in values]
    if driver == 'GPSTrackMaker':
        return [{"geometry": {"type": "Point", "coordinates": [1, 2]},
                 "properties": OrderedDict([('name', ''), ('comment', ''), ('icon', 48), ('time', val)])} for
                val in values]

    return [{"geometry": {"type": "Point", "coordinates": [1, 2]},
             "properties": {"datefield": val}} for val in values]


def get_schema_field(driver, schema):
    if driver in {'GPX', 'GPSTrackMaker'}:
        return schema["properties"]["time"]
    return schema["properties"]["datefield"]


def get_field(driver, f):
    if driver in {'GPX', 'GPSTrackMaker'}:
        return f["properties"]["time"]
    return f['properties']['datefield']


class TZ(datetime.tzinfo):

    def __init__(self, minutes):
        self.minutes = minutes

    def utcoffset(self, dt):
        return datetime.timedelta(minutes=self.minutes)


def convert_to_naive_utc(d):
    if isinstance(d, datetime.datetime):
        d_utc = datetime.datetime(d.year,
                                  d.month,
                                  d.day,
                                  d.hour,
                                  d.minute,
                                  d.second,
                                  d.microsecond)
        if d.utcoffset() is not None:
            d_utc += d.utcoffset()
        return d_utc
    else:
        d_utc = datetime.datetime(
            1900,
            1,
            1,
            d.hour,
            d.minute,
            d.second,
            d.microsecond)
        if d.utcoffset() is not None:
            d_utc += d.utcoffset()
        return d_utc.time()


def compare_datetimes(d1, d2):
    d1 = convert_to_naive_utc(d1)
    d2 = convert_to_naive_utc(d2)
    return d1 == d2


def validate_time(test_value, d, driver, strict=True):
    if strict:
        if d is None:
            if driver == 'MapInfo File' and (
                    calc_gdal_version_num(2, 0, 0) <= get_gdal_version_num() < calc_gdal_version_num(3, 1, 1)):
                return test_value == '00:00:00'
            else:
                return test_value is None
        else:
            if driver in drivers_not_supporting_milliseconds:
                return test_value == d.replace(microsecond=0, tzinfo=None).isoformat()
            else:
                return test_value == d.replace(microsecond=int(d.microsecond / 1000) * 1000,
                                               tzinfo=None).isoformat()
    else:
        if d is None:
            if test_value is None:
                return True
            if test_value == '':
                return True
            return False

        else:
            if (str(d.hour) in test_value and
                    str(d.minute) in test_value and
                    str(d.second) in test_value):
                return True
            elif (str(d.hour) in test_value and
                  str(d.minute) in test_value and
                  str(d.second) in test_value and
                  str(d.microsecond) in test_value):
                return True
            elif (str(d.hour) in test_value and
                  str(d.minute) in test_value and
                  str(d.second) in test_value and
                  str(int(d.microsecond / 1000)) in test_value):
                return True

    return False


def validate_datetime(test_value, d, driver, strict=True):

    print("validate_datetime", test_value, d, driver, strict)

    if strict:
        if d is None:
            return test_value is None
        else:
            if d.utcoffset() is not None and driver and driver_supports_timezones(driver, 'datetime'):
                return compare_datetimes(datetime.datetime.strptime(test_value, "%Y-%m-%dT%H:%M:%S.%fZ"), d)
            elif driver == 'GPKG':
                return test_value == d.replace(microsecond=int(d.microsecond / 1000) * 1000,
                                               tzinfo=TZ(0)).isoformat()
            else:
                if driver in drivers_not_supporting_milliseconds:
                    return test_value == d.replace(microsecond=0, tzinfo=None).isoformat()
                else:
                    return test_value == d.replace(microsecond=int(d.microsecond / 1000) * 1000,
                                                   tzinfo=None).isoformat()
    else:
        if d is None:
            if test_value is None:
                return True
            if test_value == '':
                return True
            return False

        else:
            if (str(d.year) in test_value and
                    str(d.month) in test_value and
                    str(d.day) in test_value and
                    str(d.hour) in test_value and
                    str(d.minute) in test_value and
                    str(d.second) in test_value):
                return True
            elif (str(d.year) in test_value and
                  str(d.month) in test_value and
                  str(d.day) in test_value and
                  str(d.hour) in test_value and
                  str(d.minute) in test_value and
                  str(d.second) in test_value and
                  str(d.microsecond) in test_value):
                return True
            elif (str(d.year) in test_value and
                  str(d.month) in test_value and
                  str(d.day) in test_value and
                  str(d.hour) in test_value and
                  str(d.minute) in test_value and
                  str(d.second) in test_value and
                  str(int(d.microsecond / 1000)) in test_value):
                return True
    return False


def validate_date(test_value, d, driver, strict=True):

    if strict:
        if d is None:
            return test_value is None
        else:
            return test_value == d.isoformat()
    else:
        if d is None:
            if test_value is None:
                return True
            if test_value == '':
                return True
            return False

        else:
            if (str(d.year) in test_value and
                    str(d.month) in test_value and
                    str(d.day) in test_value):
                return True

    return False


def validate(test_value, d, field_type, driver, strict=True):
    if field_type == 'time':
        return validate_time(test_value, d, driver, strict=strict)
    elif field_type == 'datetime':
        return validate_datetime(test_value, d, driver, strict=strict)
    elif field_type == 'date':
        return validate_date(test_value, d, driver, strict=strict)
    return False


def generate_testdata(field_type, driver):
    """ Generate test cases for test_datefield

    Each test case has the format [(in_value1, out_value1), (in_value2, out_value2), ...]
    """

    # Test data for 'date' data type
    if field_type == 'date':
        return [("2018-03-25", datetime.date(2018, 3, 25)),
                (datetime.date(2018, 3, 25), datetime.date(2018, 3, 25)),
                (None, None)]

    # Test data for 'datetime' data type
    if field_type == 'datetime':
        return [("2018-03-25T22:49:05", datetime.datetime(2018, 3, 25, 22, 49, 5)),
                (datetime.datetime(2018, 3, 25, 22, 49, 5), datetime.datetime(2018, 3, 25, 22, 49, 5)),
                ("2018-03-25T22:49:05.23", datetime.datetime(2018, 3, 25, 22, 49, 5, 230000)),
                (datetime.datetime(2018, 3, 25, 22, 49, 5, 230000), datetime.datetime(2018, 3, 25, 22, 49, 5, 230000)),
                ("2018-03-25T22:49:05.123456", datetime.datetime(2018, 3, 25, 22, 49, 5, 123000)),
                (datetime.datetime(2018, 3, 25, 22, 49, 5, 123456), datetime.datetime(2018, 3, 25, 22, 49, 5, 123000)),
                ("2018-03-25T22:49:05+01:30", datetime.datetime(2018, 3, 25, 22, 49, 5, tzinfo=TZ(90))),
                ("2018-03-25T22:49:05-01:30", datetime.datetime(2018, 3, 25, 22, 49, 5, tzinfo=TZ(-90))),
                (None, None)]

    # Test data for 'time' data type
    elif field_type == 'time':
        return [("22:49:05", datetime.time(22, 49, 5)),
                (datetime.time(22, 49, 5), datetime.time(22, 49, 5)),
                ("22:49:05.23", datetime.time(22, 49, 5, 230000)),
                (datetime.time(22, 49, 5, 230000), datetime.time(22, 49, 5, 230000)),
                ("22:49:05.123456", datetime.time(22, 49, 5, 123456)),
                (datetime.time(22, 49, 5, 123456), datetime.time(22, 49, 5, 123456)),
                (None, None)]


@pytest.mark.parametrize("driver", [driver for driver, raw in supported_drivers.items() if 'w' in raw
                                    and (driver not in driver_mode_mingdal['w'] or
                                         gdal_version >= GDALVersion(*driver_mode_mingdal['w'][driver][:2]))])
@pytest.mark.parametrize("field_type", ['time', 'datetime', 'date'])
def test_datefield(tmpdir, driver, field_type):
    """
    Test handling of date, time, datetime types for write capable drivers
    """

    strict_validation = not driver_converts_field_type_silently_to_str(driver, field_type)

    schema = get_schema(driver, field_type)
    path = str(tmpdir.join(get_temp_filename(driver)))
    # Some driver do not support date, datetime or time
    if not driver_supports_field(driver, field_type):
        with pytest.raises(DriverSupportError):
            with fiona.open(path, 'w',
                            driver=driver,
                            schema=schema) as c:
                pass

    else:
        values_in, values_out = zip(*generate_testdata(field_type, driver))
        records = get_records(driver, values_in)

        # Some driver silently convert date / datetime / time to str
        if driver_converts_field_type_silently_to_str(driver, field_type):
            with pytest.warns(UserWarning) as record:
                with fiona.open(path, 'w',
                                driver=driver,
                                schema=schema) as c:
                    c.writerecords(records)
                assert len(record) == 1
                assert "silently converts" in record[0].message.args[0]

            with fiona.open(path, 'r') as c:
                assert get_schema_field(driver, c.schema) == 'str'
                items = [get_field(driver, f) for f in c]
                assert len(items) == len(values_in)
                for val_in, val_out in zip(items, values_out):
                    assert validate(val_in, val_out, field_type, driver, strict=strict_validation), \
                        "{} does not match {}".format(val_in, val_out.isoformat())

        else:
            with fiona.open(path, 'w',
                            driver=driver,
                            schema=schema) as c:
                c.writerecords(records)

            with fiona.open(path, 'r') as c:
                assert get_schema_field(driver, c.schema) == field_type
                items = [get_field(driver, f) for f in c]
                assert len(items) == len(values_in)
                for val_in, val_out in zip(items, values_out):
                    assert validate(val_in, val_out, field_type, driver, strict=strict_validation), \
                        "{} does not match {}".format(val_in, val_out.isoformat())


@pytest.mark.parametrize("driver", [driver for driver, raw in supported_drivers.items() if 'w' in raw
                                    and (driver not in driver_mode_mingdal['w'] or
                                         gdal_version >= GDALVersion(*driver_mode_mingdal['w'][driver][:2]))])
@pytest.mark.parametrize("field_type", ['date', 'datetime', 'time'])
def test_datetime_field_type_marked_not_supported_is_not_supported(tmpdir, driver, field_type, monkeypatch):
    """ Test if a date/datetime/time field type marked as not not supported is really not supported

    Warning: Success of this test does not necessary mean that a field is not supported. E.g. errors can occour due to
    special schema requirements of drivers. This test only covers the standard case.

    """

    if driver == "BNA" and gdal_version < GDALVersion(2, 0):
        # BNA driver segfaults with gdal 1.11
        return

    # If the driver supports the field we have nothing to do here
    if driver_supports_field(driver, field_type):
        return

    monkeypatch.delitem(fiona.drvsupport.driver_field_type_unsupported[field_type], driver)

    schema = get_schema(driver, field_type)
    path = str(tmpdir.join(get_temp_filename(driver)))
    values_in, values_out = zip(*generate_testdata(field_type, driver))
    records = get_records(driver, values_in)

    is_good = True
    try:
        with fiona.open(path, 'w',
                        driver=driver,
                        schema=schema) as c:
            c.writerecords(records)

        with fiona.open(path, 'r') as c:
            if not get_schema_field(driver, c.schema) == field_type:
                is_good = False
            items = [get_field(driver, f) for f in c]
            for val_in, val_out in zip(items, values_out):
                if not val_in == val_out:
                    is_good = False
    except:
        is_good = False
    assert not is_good


def generate_tostr_testcases():
    """ Flatten driver_converts_to_str to a list of (field_type, driver) tuples"""
    cases = []
    for field_type in driver_converts_to_str:
        for driver in driver_converts_to_str[field_type]:
            driver_supported = driver in supported_drivers
            driver_can_write = (driver not in driver_mode_mingdal['w'] or
                                gdal_version >= GDALVersion(*driver_mode_mingdal['w'][driver][:2]))
            field_supported = driver_supports_field(driver, field_type)
            converts_to_str = driver_converts_field_type_silently_to_str(driver, field_type)
            if driver_supported and driver_can_write and converts_to_str and field_supported:
                cases.append((field_type, driver))
    return cases


@pytest.mark.parametrize("field_type,driver", generate_tostr_testcases())
def test_driver_marked_as_silently_converts_to_str_converts_silently_to_str(tmpdir, driver, field_type, monkeypatch):
    """ Test if a driver and field_type is marked in fiona.drvsupport.driver_converts_to_str to convert to str really
      silently converts to str

      If this test fails, it should be considered to replace the respective None value in
      fiona.drvsupport.driver_converts_to_str with a GDALVersion(major, minor) value.
      """

    monkeypatch.delitem(fiona.drvsupport.driver_converts_to_str[field_type], driver)

    schema = get_schema(driver, field_type)
    path = str(tmpdir.join(get_temp_filename(driver)))
    values_in, values_out = zip(*generate_testdata(field_type, driver))
    records = get_records(driver, values_in)

    with fiona.open(path, 'w',
                    driver=driver,
                    schema=schema) as c:
        c.writerecords(records)

    with fiona.open(path, 'r') as c:
        assert get_schema_field(driver, c.schema) == 'str'
