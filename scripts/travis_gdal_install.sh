#!/bin/sh
set -ex
GDALDIR="$HOME/gdalbuild"
GDALINST="$HOME/gdalinstall"

GDALOPTS="--prefix=$GDALINST/gdal-$GDALVERSION --with-ogr \
            --with-geos \
            --with-expat \
            --without-libtool \
            --with-libz=internal \
            --with-libtiff=internal \
            --with-geotiff=internal \
            --without-gif \
            --without-pg \
            --without-grass \
            --without-libgrass \
            --without-cfitsio \
            --without-pcraster \
            --without-netcdf \
            --without-png \
            --with-jpeg=internal \
            --without-gif \
            --without-ogdi \
            --without-fme \
            --without-hdf4 \
            --without-hdf5 \
            --without-jasper \
            --without-ecw \
            --without-kakadu \
            --without-mrsid \
            --without-jp2mrsid \
            --without-bsb \
            --without-grib \
            --without-mysql \
            --without-ingres \
            --without-xerces \
            --without-odbc \
            --without-curl \
            --without-sqlite3 \
            --without-dwgdirect \
            --without-idb \
            --without-sde \
            --without-perl \
            --without-php \
            --without-ruby \
            --without-python"

# Create build dir if not exists
if [ ! -d "$GDALDIR" ]; then
  mkdir $GDALDIR;
fi

if [ ! -d "$GDALINST" ]; then
  mkdir $GDALINST;
fi

ls -l $GDALINST

# download and compile gdal version
if [ ! -d $GDALINST/gdal-$GDALVERSION ]; then
  cd $GDALDIR
  if [ "$GDALVERSION" = "1.9.2" ]; then
    wget http://download.osgeo.org/gdal/gdal-1.9.2.tar.gz
  else
    wget http://download.osgeo.org/gdal/$GDALVERSION/gdal-$GDALVERSION.tar.gz
  fi
  tar -xzvf gdal-$GDALVERSION.tar.gz
  cd gdal-$GDALVERSION
  ./configure $GDALOPTS
  make -j 2
  make install
fi

# change back to travis build dir
cd $TRAVIS_BUILD_DIR
