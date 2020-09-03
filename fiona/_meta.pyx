
include "gdal.pxi"

from fiona._err cimport exc_wrap_pointer
from fiona._shim cimport gdal_open_vector
from fiona._env import get_gdal_version_tuple
from fiona.errors import FionaValueError
import logging


log = logging.getLogger(__name__)


def _get_metadata_item(driver, metadata_item):
    """Query metadata items

    Parameters
    ----------
    driver : str
        Driver to query
    metadata_item : str or None
        Metadata item to query

    Returns
    -------
    str
        XML of metadata item or empty string

    """
    cdef char* metadata_c = NULL
    cdef void *cogr_driver

    if get_gdal_version_tuple() < (2, ):
        return None

    try:
        driver_b = driver.encode('utf-8')
    except UnicodeDecodeError:
        driver_b = driver

    cogr_driver = GDALGetDriverByName(driver_b)
    if cogr_driver == NULL:
        raise FionaValueError("Could not find driver '{}'".format(driver))
    
    metadata_c = GDALGetMetadataItem(cogr_driver, metadata_item.encode('utf-8'), NULL)

    metadata = None
    if metadata_c != NULL:
        metadata = metadata_c
        metadata = metadata.decode('utf-8')
        if len(metadata) == 0:
            metadata = None

    return metadata
