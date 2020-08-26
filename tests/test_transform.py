"""Tests of the transform submodule"""

import math
import pytest
from fiona import transform


@pytest.mark.parametrize(
    "geom",
    [
        {"type": "Point", "coordinates": [0.0, 0.0, 1000.0]},
        {
            "type": "LineString",
            "coordinates": [[0.0, 0.0, 1000.0], [0.1, 0.1, -1000.0]],
        },
        {
            "type": "MultiPoint",
            "coordinates": [[0.0, 0.0, 1000.0], [0.1, 0.1, -1000.0]],
        },
        {
            "type": "Polygon",
            "coordinates": [
                [
                    [0.0, 0.0, 1000.0],
                    [0.1, 0.1, -1000.0],
                    [0.1, -0.1, math.pi],
                    [0.0, 0.0, 1000.0],
                ]
            ],
        },
        {
            "type": "MultiPolygon",
            "coordinates": [
                [
                    [
                        [0.0, 0.0, 1000.0],
                        [0.1, 0.1, -1000.0],
                        [0.1, -0.1, math.pi],
                        [0.0, 0.0, 1000.0],
                    ]
                ]
            ],
        },
    ],
)
def test_transform_geom_with_z(geom):
    """Transforming a geom with Z succeeds"""
    g2 = transform.transform_geom("epsg:4326", "epsg:3857", geom, precision=3)


@pytest.mark.parametrize("source_crs", ["epsg:4326",
                                        "EPSG:4326",
                                        "WGS84",
                                        {'init': 'epsg:4326'},
                                        {'proj': 'longlat', 'datum': 'WGS84', 'no_defs': True},
                                        "OGC:CRS84"])
def test_axis_ordering(source_crs):
    """ Test if transform uses traditional_axis_mapping """

    expected = (-8427998.647958742, 4587905.27136252)

    t1 = transform.transform(source_crs, "epsg:3857", [-75.71], [38.06])
    assert (t1[0][0], t1[1][0]) == pytest.approx(expected)

    geom = {"type": "Point", "coordinates": [-75.71, 38.06]}
    g1 = transform.transform_geom(source_crs, "epsg:3857", geom, precision=3)
    assert g1["coordinates"] == pytest.approx(expected)
