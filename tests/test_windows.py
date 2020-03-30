import pytest

from .conftest import windows_only, requires_python38
import os


@windows_only
@requires_python38
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

    new_PATH = os.pathsep.join(paths)
    monkeypatch.setenv("PATH", new_PATH)

    assert "gdal" not in os.getenv('PATH', '').lower()

    from importlib import invalidate_caches
    invalidate_caches()

    import fiona.ogrext

    assert "gdal" not in os.getenv('PATH', '').lower()

    assert True
