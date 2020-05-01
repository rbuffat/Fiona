"""
See also test_rfc3339.py for datetime parser tests.
"""

import fiona
import pytest
import tempfile
import shutil
import os
from fiona.errors import DriverSupportError
from .conftest import requires_gpkg, get_temp_filename
from fiona.env import GDALVersion
import datetime


gdal_version = GDALVersion.runtime()
GDAL_MAJOR_VER = gdal_version.major

GEOMETRY_TYPE = "Point"
GEOMETRY_EXAMPLE = {"type": "Point", "coordinates": [1, 2]}

DATE_EXAMPLE = "2018-03-25"
PY_DATE_EXAMPLE = datetime.datetime.strptime(DATE_EXAMPLE, "%Y-%m-%d").date()


DATETIME_EXAMPLE = "2018-03-25T22:49:05"
PY_DATETIME_EXAMPLE = datetime.datetime.strptime(DATETIME_EXAMPLE, "%Y-%m-%dT%H:%M:%S")
DATETIME_EXAMPLE_MILLISECONDS = "2018-03-25T22:49:05.123000"
PY_DATETIME_EXAMPLE_MILLISECONDS = datetime.datetime.strptime(DATETIME_EXAMPLE_MILLISECONDS, "%Y-%m-%dT%H:%M:%S.%f")

TIME_EXAMPLE = "22:49:05"
PY_TIME_EXAMPLE = datetime.datetime.strptime(TIME_EXAMPLE, "%H:%M:%S").time()
TIME_EXAMPLE_MILLISECONDS = "22:49:05.123000"
PY_TIME_EXAMPLE_MILLISECONDS = datetime.datetime.strptime(TIME_EXAMPLE_MILLISECONDS, "%H:%M:%S.%f").time()


class TestDateFieldSupport:
    def write_data(self, driver):
        filename = get_temp_filename(driver)
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
            {
                "geometry": GEOMETRY_EXAMPLE,
                "properties": {
                    "date": PY_DATE_EXAMPLE,
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
        assert features[2]["properties"]["date"] == DATE_EXAMPLE

    @requires_gpkg
    def test_gpkg(self):
        driver = "GPKG"
        schema, features = self.write_data(driver)

        assert schema["properties"]["date"] == "date"
        assert features[0]["properties"]["date"] == DATE_EXAMPLE
        assert features[1]["properties"]["date"] is None
        assert features[2]["properties"]["date"] == DATE_EXAMPLE

    def test_geojson(self):
        # GDAL 1: date field silently converted to string
        # GDAL 1: date string format uses / instead of -
        driver = "GeoJSON"
        schema, features = self.write_data(driver)

        if GDAL_MAJOR_VER >= 2:
            assert schema["properties"]["date"] == "date"
            assert features[0]["properties"]["date"] == DATE_EXAMPLE
            assert features[2]["properties"]["date"] == DATE_EXAMPLE
        else:
            assert schema["properties"]["date"] == "str"
            assert features[0]["properties"]["date"] == "2018/03/25"
            assert features[2]["properties"]["date"] == "2018/03/25"
        assert features[1]["properties"]["date"] is None

    def test_mapinfo(self):
        driver = "MapInfo File"
        schema, features = self.write_data(driver)

        assert schema["properties"]["date"] == "date"
        assert features[0]["properties"]["date"] == DATE_EXAMPLE
        assert features[1]["properties"]["date"] is None
        assert features[2]["properties"]["date"] == DATE_EXAMPLE


class TestDatetimeFieldSupport:
    def write_data(self, driver):
        filename = get_temp_filename(driver)
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
                    "datetime": DATETIME_EXAMPLE_MILLISECONDS,
                }
            },
            {
                "geometry": GEOMETRY_EXAMPLE,
                "properties": {
                    "datetime": None,
                }
            },
            {
                "geometry": GEOMETRY_EXAMPLE,
                "properties": {
                    "datetime": PY_DATETIME_EXAMPLE_MILLISECONDS,
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
            assert features[0]["properties"]["datetime"] == DATETIME_EXAMPLE_MILLISECONDS
            assert features[1]["properties"]["datetime"] is None
            assert features[2]["properties"]["datetime"] == DATETIME_EXAMPLE_MILLISECONDS
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
            assert features[0]["properties"]["datetime"] == DATETIME_EXAMPLE_MILLISECONDS
            assert features[2]["properties"]["datetime"] == DATETIME_EXAMPLE_MILLISECONDS
        else:
            assert schema["properties"]["datetime"] == "str"
            assert features[0]["properties"]["datetime"] == "2018/03/25 22:49:05.22"
            assert features[2]["properties"]["datetime"] == "2018/03/25 22:49:05.22"
        assert features[1]["properties"]["datetime"] is None

    def test_mapinfo(self):
        driver = "MapInfo File"
        schema, features = self.write_data(driver)

        assert schema["properties"]["datetime"] == "datetime"
        assert features[0]["properties"]["datetime"] == DATETIME_EXAMPLE_MILLISECONDS
        assert features[1]["properties"]["datetime"] is None
        assert features[2]["properties"]["datetime"] == DATETIME_EXAMPLE_MILLISECONDS


class TestTimeFieldSupport:
    def write_data(self, driver):
        filename = get_temp_filename(driver)
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
                    "time": TIME_EXAMPLE_MILLISECONDS,
                }
            },
            {
                "geometry": GEOMETRY_EXAMPLE,
                "properties": {
                    "time": None,
                }
            },
            {
                "geometry": GEOMETRY_EXAMPLE,
                "properties": {
                    "time": PY_TIME_EXAMPLE_MILLISECONDS,
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

        with pytest.raises(DriverSupportError):
            schema, features = self.write_data(driver)

        # if GDAL_MAJOR_VER >= 2:
        #     assert schema["properties"]["time"] == "str"
        #     assert features[0]["properties"]["time"] == TIME_EXAMPLE_MILLISECONDS
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
        assert features[0]["properties"]["time"] == TIME_EXAMPLE_MILLISECONDS
        assert features[1]["properties"]["time"] is None
        assert features[2]["properties"]["time"] == TIME_EXAMPLE_MILLISECONDS

    def test_mapinfo(self):
        # GDAL 2: null time is converted to 00:00:00 (regression?)
        driver = "MapInfo File"
        schema, features = self.write_data(driver)

        assert schema["properties"]["time"] == "time"
        assert features[0]["properties"]["time"] == TIME_EXAMPLE_MILLISECONDS
        if GDAL_MAJOR_VER >= 2:
            assert features[1]["properties"]["time"] == "00:00:00"
        else:
            assert features[1]["properties"]["time"] is None
        assert features[2]["properties"]["time"] == TIME_EXAMPLE_MILLISECONDS