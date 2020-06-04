import pytest
import fiona
import fiona.drvsupport
import fiona.meta
from fiona.drvsupport import supported_drivers


@pytest.mark.parametrize("driver", supported_drivers)
def test_print_driver_options(driver):
    # do not fail
    fiona.meta.print_driver_options(driver)


@pytest.mark.parametrize("driver", supported_drivers)
def test_extensions(driver):
    # do not fail
    fiona.meta.extensions(driver)


@pytest.mark.parametrize("driver", supported_drivers)
def test_supports_vsi(driver):
    # do not fail
    fiona.meta.supports_vsi(driver)

