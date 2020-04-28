"""Note well: collection slicing is deprecated!
"""

import logging
import sys

import pytest
from fiona.env import GDALVersion
import fiona
from fiona.errors import FionaDeprecationWarning
from .conftest import get_temp_filename
from fiona.drvsupport import supported_drivers, driver_mode_mingdal


def test_collection_get(path_coutwildrnp_shp):
    with fiona.open(path_coutwildrnp_shp) as src:
        result = src[5]
        assert result['id'] == '5'


def test_collection_slice(path_coutwildrnp_shp):
    with pytest.warns(FionaDeprecationWarning), fiona.open(path_coutwildrnp_shp) as src:
        results = src[:5]
        assert isinstance(results, list)
        assert len(results) == 5
        assert results[4]['id'] == '4'


def test_collection_iterator_slice(path_coutwildrnp_shp):
    with fiona.open(path_coutwildrnp_shp) as src:
        results = list(src.items(5))
        assert len(results) == 5
        k, v = results[4]
        assert k == 4
        assert v['id'] == '4'


def test_collection_iterator_next(path_coutwildrnp_shp):
    with fiona.open(path_coutwildrnp_shp) as src:
        k, v = next(src.items(5, None))
        assert k == 5
        assert v['id'] == '5'


@pytest.mark.parametrize('driver', [driver for driver, raw in supported_drivers.items() if 'w' in raw
                                    and driver not in {'DGN', 'MapInfo File', 'GPSTrackMaker', 'GPX', 'BNA', 'DXF',
                                                       'GML'}])
@pytest.mark.parametrize("args", [(0, 5, None),
                                  (1, 5, None),
                                  (-5, None, None),
                                  (-5, -1, None),
                                  (0, None, None),
                                  (5, None, None),
                                  (0, 5, 2),
                                  (1, 5, 2),
                                  (-5, None, 2),
                                  (-5, -1, 2),
                                  (0, None, 2),
                                  (5, None, 2),
                                  (5, None, -1),
                                  (5, None, -2),
                                  (5, None, None),
                                  (4, None, -2),
                                  (-1, -5, -1),
                                  (-5, None, -1)])
def test_collection_iterator_items_slice(tmpdir, driver, args):
    """ Test if c.filter(start, stop) returns the correct features.
    """

    start, stop, step = args

    min_id = 0
    max_id = 9

    schema = {'geometry': 'Point', 'properties': [('position', 'int')]}
    path = str(tmpdir.join(get_temp_filename(driver)))

    # We only test driver with write capabilities
    if driver in driver_mode_mingdal['w'] and GDALVersion.runtime() < GDALVersion(
            *driver_mode_mingdal['w'][driver][:2]):
        return

    records = [{'geometry': {'type': 'Point', 'coordinates': (0.0, float(i))}, 'properties': {'position': i}} for i in
               range(min_id, max_id + 1)]

    # Create test file to append to
    with fiona.open(path, 'w',
                    driver=driver,
                    schema=schema) as c:
        c.writerecords(records)

    positions = list(range(min_id, max_id + 1))[start:stop:step]

    if ((start and start < 0) or (stop and stop < 0)) and driver in {'GMT'}:
        with pytest.raises(IndexError):
            with fiona.open(path, 'r') as c:
                pass
    else:
        with fiona.open(path, 'r') as c:
            items = list(c.items(start, stop, step))
            assert len(items) == len(positions)
            record_positions = [int(item[1]['properties']['position']) for item in items]
            assert len(positions) == len(record_positions)
            for expected_position, record_position in zip(positions, record_positions):
                assert expected_position == record_position


def test_collection_iterator_keys_next(path_coutwildrnp_shp):
    with fiona.open(path_coutwildrnp_shp) as src:
        k = next(src.keys(5, None))
        assert k == 5
