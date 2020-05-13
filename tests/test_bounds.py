import pytest
import fiona
from fiona.errors import DriverError
from .conftest import driver_extensions
from fiona.env import GDALVersion

from fiona.drvsupport import supported_drivers, driver_mode_mingdal

gdal_version = GDALVersion.runtime()

def test_bounds_point():
    g = {'type': 'Point', 'coordinates': [10, 10]}
    assert fiona.bounds(g) == (10, 10, 10, 10)


def test_bounds_line():
    g = {'type': 'LineString', 'coordinates': [[0, 0], [10, 10]]}
    assert fiona.bounds(g) == (0, 0, 10, 10)


def test_bounds_polygon():
    g = {'type': 'Polygon', 'coordinates': [[[0, 0], [10, 10], [10, 0]]]}
    assert fiona.bounds(g) == (0, 0, 10, 10)


def test_bounds_z():
    g = {'type': 'Point', 'coordinates': [10, 10, 10]}
    assert fiona.bounds(g) == (10, 10, 10, 10)


@pytest.mark.parametrize('driver', [driver for driver, raw in supported_drivers.items() if 'w' in raw and (
        driver not in driver_mode_mingdal['w'] or gdal_version >= GDALVersion(*driver_mode_mingdal['w'][driver][:2]))
                                    and driver not in {'CSV', 'GPX', 'GPSTrackMaker', 'DXF', 'DGN', 'MapInfo File'}])
def test_bounds(tmpdir, driver):
    """Test if bounds are correctly calculated after writing
    """

    if driver == 'BNA' and GDALVersion.runtime() < GDALVersion(2, 0):
        # BNA driver segfaults with gdal 1.11
        return

    extension = driver_extensions.get(driver, "bar")
    path = str(tmpdir.join('foo.{}'.format(extension)))

    with fiona.open(path, 'w',
                    driver=driver,
                    schema={'geometry': 'Point',
                            'properties': [('title', 'str')]}) as c:

        c.writerecords([{'geometry': {'type': 'Point', 'coordinates': (1.0, 10.0)},
                         'properties': {'title': 'One'}}])

        try:
            bounds = c.bounds
            assert bounds == (1.0, 10.0, 1.0, 10.0)
        except Exception as e:
            assert isinstance(e, DriverError)

        c.writerecords([{'geometry': {'type': 'Point', 'coordinates': (2.0, 20.0)},
                         'properties': {'title': 'Two'}}])

        try:
            bounds = c.bounds
            assert bounds == (1.0, 10.0, 2.0, 20.0)
        except Exception as e:
            assert isinstance(e, DriverError)
