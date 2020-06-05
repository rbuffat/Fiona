
include "gdal.pxi"

from fiona._err cimport  exc_wrap_pointer
from fiona.compat import strencode
from fiona._shim cimport gdal_open_vector
from fiona.env import require_gdal_version
import logging

# This import is required otherwise GDALGetDriverByName returns NULL for GDAL 1.x
from fiona._shim cimport *


log = logging.getLogger(__name__)


@require_gdal_version('2.0')
def _get_metadata_item(driver, metadata_item):
    """Query metadata items

    Parameters
    ----------
    driver : str
        Driver to query
    metadata_item : str
        Metadata item to query

    Returns
    -------
    str
        XML of metadata item or empty string

    """
    cdef char* metadata_c = NULL
    cdef void *cogr_driver

    metadata = ""
    cogr_driver = exc_wrap_pointer(GDALGetDriverByName(driver.encode("utf-8")))
    metadata_c = GDALGetMetadataItem(cogr_driver, strencode(metadata_item), NULL)
    if metadata_c != NULL:
        metadata = metadata_c
    return metadata


def _get_metadata_item_domains(driver, metadata_item):
    """Query metadata items
    TODO: not sure when a domain is required

    Parameters
    ----------
    driver : str
        Driver to query
    metadata_item : str
        Metadata item to query

    Returns
    -------
    list
        Each list item contains a (domain name, metadata xml) tuple

    """
    cdef char *driver_c
    cdef char *result_c
    cdef void* cogr_driver = NULL
    cdef char** pszDomains
    cdef char * metadata_c
    cdef int n


    driver_b = driver.encode()
    driver_c = driver_b
    cogr_driver = exc_wrap_pointer(GDALGetDriverByName(driver_c))

    pszDomains = GDALGetMetadataDomainList(cogr_driver)
    n = CSLCount(pszDomains)

    data = []
    for i in range(n):
        domain = CSLGetField(pszDomains, i)
        metadata = ""
        metadata_c = GDALGetMetadataItem(cogr_driver, metadata_item.encode(), CSLGetField(pszDomains, i))
        if metadata_c != NULL:
            metadata = metadata_c
            metadata = metadata.decode('utf-8')
        data.append((domain, metadata))

    return data
