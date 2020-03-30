import pytest

from .conftest import windows_only
import os


@windows_only
def test_import_gdalhome(monkeypatch):
    """
    Test if fiona import works using GDAL_HOME only
    """

    assert 'GDAL_HOME' in os.environ
    assert os.path.exists(os.environ['GDAL_HOME'])

    # Clean gdal paths from PATH
    paths = []

    for path in os.getenv('PATH', '').split(os.pathsep):
        if 'gdal' not in path.lower():
            paths.append(path)

    monkeypatch.setenv("PATH", os.pathsep.join(paths))
    for path in os.getenv('PATH', '').split(os.pathsep):
        assert "path" not in path.lower()

    import fiona.ogrext

    assert True

