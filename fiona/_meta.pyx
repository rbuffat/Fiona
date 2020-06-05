# cython: c_string_type=unicode, c_string_encoding=utf8
from __future__ import absolute_import

include "gdal.pxi"

from fiona._err cimport  exc_wrap_pointer
from fiona.compat import strencode
from fiona._shim cimport gdal_open_vector
from fiona.env import ensure_env

import datetime
import json
import locale
import logging
import os
import warnings
import math
import uuid
from collections import namedtuple

from six import integer_types, string_types, text_type

from fiona._shim cimport *

from fiona._geometry cimport (
    GeomBuilder, OGRGeomBuilder, geometry_type_code,
    normalize_geometry_type_code, base_geometry_type_code)
from fiona._err cimport exc_wrap_int, exc_wrap_pointer, exc_wrap_vsilfile, get_last_error_msg

import fiona
from fiona._env import GDALVersion, get_gdal_version_num
from fiona._err import cpl_errs, FionaNullPointerError, CPLE_BaseError, CPLE_OpenFailedError
from fiona._geometry import GEOMETRY_TYPES
from fiona import compat
from fiona.errors import (
    DriverError, DriverIOError, SchemaError, CRSError, FionaValueError,
    TransactionError, GeometryTypeValidationError, DatasetDeleteError,
    FionaDeprecationWarning)
from fiona.compat import OrderedDict, strencode
from fiona.rfc3339 import parse_date, parse_datetime, parse_time
from fiona.rfc3339 import FionaDateType, FionaDateTimeType, FionaTimeType
from fiona.schema import FIELD_TYPES, FIELD_TYPES_MAP, normalize_field_type
from fiona.path import vsi_path
from fiona._shim cimport is_field_null, osr_get_name, osr_set_traditional_axis_mapping_strategy

from libc.stdlib cimport malloc, free
from libc.string cimport strcmp
from cpython cimport PyBytes_FromStringAndSize, PyBytes_AsString


cdef extern from "ogr_api.h" nogil:

    ctypedef void * OGRLayerH
    ctypedef void * OGRDataSourceH
    ctypedef void * OGRSFDriverH
    ctypedef void * OGRFieldDefnH
    ctypedef void * OGRFeatureDefnH
    ctypedef void * OGRFeatureH
    ctypedef void * OGRGeometryH


log = logging.getLogger(__name__)


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
    cdef char* metadata_c
    cdef void *cogr_driver

    print("before 2: {}".format(GDALGetDriverCount()))
    print(driver, type(driver))
    cogr_driver = exc_wrap_pointer(GDALGetDriverByName(driver.encode("utf-8")))
    print("success2: {}".format(GDALGetDriverCount()))

    metadata = ""
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
