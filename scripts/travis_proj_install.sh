#!/bin/sh
set -e

# Create build dir if not exists
if [ ! -d "$PROJBUILD" ]; then
  mkdir $PROJBUILD;
fi

if [ ! -d "$PROJINST" ]; then
  mkdir $PROJINST;
fi

ls -l $PROJINST

echo "PROJ VERSION: $PROJVERSION"

DISTRIB_CODENAME=$(lsb_release -cs)
GDAL_ARCHIVE_NAME="gdal_${GDALVERSION}_proj_${PROJVERSION}_${DISTRIB_CODENAME}.tar.gz"
GDAL_ARCHIVE_URL="https://rbuffat.github.io/gdal_builder/$GDAL_ARCHIVE_NAME"

if [ "$GDALVERSION" = "master" ] && ( curl -o/dev/null -sfI "$GDAL_ARCHIVE_URL" ) && [ "$FORCE_GDAL_BUILD" != "yes" ]; then
    echo "Use previously built gdal $GDALVERSION"

else

    if [ ! -d "$PROJINST/gdal-$GDALVERSION/share/proj" ]; then
        cd $PROJBUILD
        wget -q https://download.osgeo.org/proj/proj-$PROJVERSION.tar.gz
        tar -xzf proj-$PROJVERSION.tar.gz
        cd proj-$PROJVERSION
        ./configure --prefix=$PROJINST/gdal-$GDALVERSION
        make -s -j 2
        make install
    fi
fi

# change back to travis build dir
cd $TRAVIS_BUILD_DIR
