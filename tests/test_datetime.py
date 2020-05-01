"""
See also test_rfc3339.py for datetime parser tests.
"""

import fiona
import pytest

from fiona.errors import DriverSupportError
from .conftest import get_temp_filename
from fiona.env import GDALVersion
import datetime
from fiona.drvsupport import supported_drivers, driver_mode_mingdal

gdal_version = GDALVersion.runtime()


def generate_testdata(datatype, driver):
    """ Generate test cases for test_datefield

    Each testcase has the format [(in_value1, out_value1), (in_value2, out_value2), ...]
    """

    # Test data for 'date' data type
    if datatype == 'date' and (driver == 'CSV'):
        return [("2018-03-25", "2018/03/25"),
                (datetime.date(2018, 3, 25), "2018/03/25"),
                (None, '')]
    elif datatype == 'date' and ((driver == 'GeoJSON' and gdal_version.major < 2) or
                                 (driver == 'GMT' and gdal_version.major < 2)):
        return [("2018-03-25", "2018/03/25"),
                (datetime.date(2018, 3, 25), "2018/03/25"),
                (None, None)]
    if datatype == 'date' and driver == 'PCIDSK':

        if gdal_version < GDALVersion(2, 1):
            return [("2018-03-25", ''),
                    (datetime.date(2018, 3, 25), ''),
                    (None, '')]
        else:
            return [("2018-03-25", "2018/03/25 00:00:00"),
                    (datetime.date(2018, 3, 25), "2018/03/25 00:00:00"),
                    (None, '')]
    elif datatype == 'date':
        return [("2018-03-25", "2018-03-25"),
                (datetime.date(2018, 3, 25), "2018-03-25"),
                (None, None)]

    # Test data for 'datetime' data type
    if datatype == 'datetime' and driver in {'CSV', 'PCIDSK'}:
        if gdal_version.major < 2:
            return [("2018-03-25T22:49:05", "2018/03/25 22:49:05"),
                    (datetime.datetime(2018, 3, 25, 22, 49, 5), "2018/03/25 22:49:05"),
                    ("2018-03-25T22:49:05.22", "2018/03/25 22:49:05"),
                    (datetime.datetime(2018, 3, 25, 22, 49, 5, 220000), "2018/03/25 22:49:05"),
                    ("2018-03-25T22:49:05.123456", "2018/03/25 22:49:05"),
                    (datetime.datetime(2018, 3, 25, 22, 49, 5, 123456), "2018/03/25 22:49:05"),
                    (None, '')]
        else:
            return [("2018-03-25T22:49:05", "2018/03/25 22:49:05"),
                    (datetime.datetime(2018, 3, 25, 22, 49, 5), "2018/03/25 22:49:05"),
                    ("2018-03-25T22:49:05.22", "2018/03/25 22:49:05.220"),
                    (datetime.datetime(2018, 3, 25, 22, 49, 5, 220000), "2018/03/25 22:49:05.220"),
                    ("2018-03-25T22:49:05.123456", "2018/03/25 22:49:05.123"),
                    (datetime.datetime(2018, 3, 25, 22, 49, 5, 123456), "2018/03/25 22:49:05.123"),
                    (None, '')]
    if datatype == 'datetime' and driver == 'GeoJSON' and gdal_version.major < 2:
        return [("2018-03-25T22:49:05", "2018/03/25 22:49:05"),
                (datetime.datetime(2018, 3, 25, 22, 49, 5), "2018/03/25 22:49:05"),
                ("2018-03-25T22:49:05.22", "2018/03/25 22:49:05"),
                (datetime.datetime(2018, 3, 25, 22, 49, 5, 220000), "2018/03/25 22:49:05"),
                ("2018-03-25T22:49:05.123456", "2018/03/25 22:49:05"),
                (datetime.datetime(2018, 3, 25, 22, 49, 5, 123456), "2018/03/25 22:49:05"),
                (None, None)]
    elif datatype == 'datetime':
        if gdal_version.major < 2:
            return [("2018-03-25T22:49:05", "2018-03-25T22:49:05"),
                    (datetime.datetime(2018, 3, 25, 22, 49, 5), "2018-03-25T22:49:05"),
                    ("2018-03-25T22:49:05.22", "2018-03-25T22:49:05"),
                    (datetime.datetime(2018, 3, 25, 22, 49, 5, 220000), "2018-03-25T22:49:05"),
                    ("2018-03-25T22:49:05.123456", "2018-03-25T22:49:05"),
                    (datetime.datetime(2018, 3, 25, 22, 49, 5, 123456), "2018-03-25T22:49:05"),
                    (None, None)]
        else:
            return [("2018-03-25T22:49:05", "2018-03-25T22:49:05"),
                    (datetime.datetime(2018, 3, 25, 22, 49, 5), "2018-03-25T22:49:05"),
                    ("2018-03-25T22:49:05.22", "2018-03-25T22:49:05.220000"),
                    (datetime.datetime(2018, 3, 25, 22, 49, 5, 220000), "2018-03-25T22:49:05.220000"),
                    ("2018-03-25T22:49:05.123456", "2018-03-25T22:49:05.123000"),
                    (datetime.datetime(2018, 3, 25, 22, 49, 5, 123456), "2018-03-25T22:49:05.123000"),
                    (None, None)]

    # Test data for 'time' data type
    if datatype == 'time' and driver == 'PCIDSK':
        return [("22:49:05", '0000/00/00 22:49:05'),
                (datetime.time(22, 49, 5), '0000/00/00 22:49:05'),
                ("22:49:05.22", '0000/00/00 22:49:05.220'),
                (datetime.time(22, 49, 5, 220000), '0000/00/00 22:49:05.220'),
                ("22:49:05.123456", '0000/00/00 22:49:05.123'),
                (datetime.time(22, 49, 5, 123456), '0000/00/00 22:49:05.123'),
                (None, '')]
    elif datatype == 'time' and driver == 'MapInfo File':
        if gdal_version.major < 2:
            return [("22:49:05", "22:49:05"),
                    (datetime.time(22, 49, 5), "22:49:05"),
                    ("22:49:05.22", "22:49:05"),
                    (datetime.time(22, 49, 5, 220000), "22:49:05"),
                    ("22:49:05.123456", "22:49:05"),
                    (datetime.time(22, 49, 5, 123456), "22:49:05"),
                    (None, '00:00:00')]
        else:
            return [("22:49:05", "22:49:05"),
                    (datetime.time(22, 49, 5), "22:49:05"),
                    ("22:49:05.22", "22:49:05.220000"),
                    (datetime.time(22, 49, 5, 220000), "22:49:05.220000"),
                    ("22:49:05.123456", "22:49:05.123000"),
                    (datetime.time(22, 49, 5, 123456), "22:49:05.123000"),
                    (None, '00:00:00')]
    elif datatype == 'time' and driver == 'CSV':
        if gdal_version.major < 2:
            return [("22:49:05", "22:49:05"),
                    (datetime.time(22, 49, 5), "22:49:05"),
                    ("22:49:05.22", "22:49:05"),
                    (datetime.time(22, 49, 5, 220000), "22:49:05"),
                    ("22:49:05.123456", "22:49:05"),
                    (datetime.time(22, 49, 5, 123456), "22:49:05"),
                    (None, '')]
        else:
            return [("22:49:05", "22:49:05"),
                    (datetime.time(22, 49, 5), "22:49:05"),
                    ("22:49:05.22", "22:49:05.220"),
                    (datetime.time(22, 49, 5, 220000), "22:49:05.220"),
                    ("22:49:05.123456", "22:49:05.123"),
                    (datetime.time(22, 49, 5, 123456), "22:49:05.123"),
                    (None, '')]
    elif datatype == 'time' and driver in {'GeoJSON', 'GeoJSONSeq'}:
        if gdal_version.major < 2:
            return [("22:49:05", "22/49/05"),
                    (datetime.time(22, 49, 5), "22:49:05"),
                    ("22:49:05.22", "22/49/05.220000"),
                    (datetime.time(22, 49, 5, 220000), "22:49:05"),
                    ("22:49:05.123456", "22:49:05"),
                    (datetime.time(22, 49, 5, 123456), "22:49:05"),
                    (None, None)]
        else:
            return [("22:49:05", "22:49:05"),
                    (datetime.time(22, 49, 5), "22:49:05"),
                    ("22:49:05.22", "22:49:05.220000"),
                    (datetime.time(22, 49, 5, 220000), "22:49:05.220000"),
                    ("22:49:05.123456", "22:49:05.123000"),
                    (datetime.time(22, 49, 5, 123456), "22:49:05.123000"),
                    (None, None)]
    elif datatype == 'time':
        if gdal_version.major < 2:
            return [("22:49:05", "22:49:05"),
                    (datetime.time(22, 49, 5), "22:49:05"),
                    ("22:49:05.22", "22:49:05"),
                    (datetime.time(22, 49, 5, 220000), "22:49:05"),
                    ("22:49:05.123456", "22:49:05"),
                    (datetime.time(22, 49, 5, 123456), "22:49:05"),
                    (None, None)]
        else:
            return [("22:49:05", "22:49:05"),
                    (datetime.time(22, 49, 5), "22:49:05"),
                    ("22:49:05.22", "22:49:05.220"),
                    (datetime.time(22, 49, 5, 220000), "22:49:05.220"),
                    ("22:49:05.123456", "22:49:05.123000"),
                    (datetime.time(22, 49, 5, 123456), "22:49:05.123000"),
                    (None, None)]


@pytest.mark.parametrize("driver", [driver for driver, raw in supported_drivers.items() if 'w' in raw
                                    and (driver not in driver_mode_mingdal['w'] or
                                         gdal_version >= GDALVersion(*driver_mode_mingdal['w'][driver][:2]))
                                    and driver not in {'DGN', 'GPSTrackMaker', 'GPX', 'BNA', 'DXF', 'GML'}])
@pytest.mark.parametrize("data_type", ['date', 'datetime', 'time'])
def test_datefield(tmpdir, driver, data_type):

    schema = {
        "geometry": "Point",
        "properties": {
            "datefield": data_type,
        }
    }

    path = str(tmpdir.join(get_temp_filename(driver)))
    if ((driver == 'ESRI Shapefile' and data_type in {'datetime', 'time'}) or
            (driver == 'GPKG' and data_type == 'time') or
            (driver == 'GPKG' and gdal_version.major < 2)):
        with pytest.raises(DriverSupportError):
            with fiona.open(path, 'w',
                            driver=driver,
                            schema=schema) as c:
                pass

    else:
        values_in, values_out = zip(*generate_testdata(data_type, driver))

        records = [{
            "geometry": {"type": "Point", "coordinates": [1, 2]},
            "properties": {
                "datefield": val_in,
            }
        } for val_in in values_in]

        with fiona.open(path, 'w',
                        driver=driver,
                        schema=schema) as c:
            c.writerecords(records)

        with fiona.open(path, 'r') as c:

            # Some drivers convert data types to str
            if ((driver in {'CSV', 'PCIDSK'}) or
                    (driver == 'GeoJSON' and gdal_version.major < 2) or
                    (driver == 'GMT' and gdal_version.major < 2)):
                assert c.schema["properties"]["datefield"] == 'str'
            else:
                assert c.schema["properties"]["datefield"] == data_type

            items = [f['properties']['datefield'] for f in c]

            assert len(items) == len(values_in)
            for val_in, val_out in zip(items, values_out):
                print(val_in, val_out)
                assert val_in == val_out
