import pytest

from fiona.collection import Collection, supported_drivers	from fiona.collection import Collection
from fiona.env import getenv	from fiona.drvsupport import supported_drivers, driver_mode_mingdal
from fiona.env import getenv, GDALVersion
from fiona.errors import FionaValueError, DriverError, FionaDeprecationWarning	from fiona.errors import FionaValueError, DriverError, FionaDeprecationWarning

from .conftest import WGS84PATTERN, driver_extensions, requires_gdal2
from .conftest import WGS84PATTERN	


#write_not_append_drivers = [driver for driver, raw in supported_drivers.items() if 'w' in raw and not 'a' in raw]

## Segfault with gdal 1.11, thus only enabling test with gdal2 and above
#@requires_gdal2
#@pytest.mark.parametrize('driver', write_not_append_drivers)
#def test_append_does_not_work(tmpdir, driver):
    #"""Test if driver supports append but it is not enabled
    
    #If this test fails, it should be considered to enable append for the respective driver in drvsupport.py. 
    
    #"""

    #backup_mode = supported_drivers[driver]

    #supported_drivers[driver] = 'raw'

    #extension = driver_extensions.get(driver, "bar")
    #path = str(tmpdir.join('foo.{}'.format(extension)))

    #with fiona.open(path, 'w',
                    #driver=driver,
                    #schema={'geometry': 'LineString',
                            #'properties': [('title', 'str')]}) as c:

        #c.writerecords([{'geometry': {'type': 'LineString', 'coordinates': [
                       #(1.0, 0.0), (0.0, 0.0)]}, 'properties': {'title': 'One'}}])

    #with pytest.raises(Exception):
        #with fiona.open(path, 'a',
                    #driver=driver) as c:
            #c.writerecords([{'geometry': {'type': 'LineString', 'coordinates': [
                        #(2.0, 0.0), (0.0, 0.0)]}, 'properties': {'title': 'Two'}}])

    #supported_drivers[driver] = backup_mode
