
import fiona
import logging
import os.path
import shutil
import sys
import tempfile
import unittest


logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


class SQLReadingTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sql_read(self):
        with fiona.open(path='docs/data/test_uk.shp',
                        mode='r',
                        sql="SELECT * FROM test_uk") as c:
            self.assertEquals(len(list(c.items())), 48)

        with fiona.open(path='docs/data/test_uk.shp',
                        mode='r',
                        sql="SELECT * FROM test_uk WHERE OGR_GEOM_AREA < 0.01") as c:
            self.assertEquals(len(list(c.items())), 21)


class SQLGeoJsonTest(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.path = os.path.join(self.tempdir, 'foo.json')
        with fiona.open(self.path, 'w',
                driver='GeoJSON',
                schema={'geometry': 'Unknown', 'properties': [('title', 'str')]}) as c:
            c.writerecords([{
                'geometry': {'type': 'Point', 'coordinates': [0.0, 0.0]},
                'properties': {'title': 'One'}}])
            c.writerecords([{
                'geometry': {'type': 'MultiPoint', 'coordinates': [[0.0, 0.0]]},
                'properties': {'title': 'Two'}}])

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_sql_json(self):
        with fiona.open(path=self.path,
                        mode='r',
                        sql="SELECT * FROM OGRGeoJSON WHERE title='TWO'") as c:
            self.assertEquals(len(list(c.items())), 1)

        with fiona.open(path=self.path,
                mode='r',
                sql="SELECT * FROM OGRGeoJSON") as c:
            self.assertEquals(len(list(c.items())), 2)


class SQLSlicingTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sql_slice(self):
        with fiona.open(path='docs/data/test_uk.shp',
                        mode='r',
                        sql="SELECT * FROM test_uk  WHERE OGR_GEOM_AREA < 0.01") as src:

            items = list(src.items(0, 5))
            self.assertEquals(len(items), 5)

            items = list(src.items(1, 5))
            self.assertEquals(len(items), 4)

            items = list(src.items(5, None, -1))
            self.assertEquals(len(items), 6)

            items = list(src.items(5, None, -2))
            self.assertEquals(len(items), 3)

            items = list(src.items(4, None, -2))
            self.assertEquals(len(items), 3)
