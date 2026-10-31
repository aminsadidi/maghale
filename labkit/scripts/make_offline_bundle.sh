#!/bin/bash
# make_offline_bundle.sh - builds offline/maghale_lab_offline.zip: everything the lab kit needs on a Windows PC without
# internet (portable Python 3.11 + numpy, MNPBEM17, the BEM job files, the lab kit). Run on any Linux machine with internet.
set -euo pipefail
REPO=$(cd "$(dirname "$0")/../.." && pwd)
W=$(mktemp -d); B=$W/maghale_lab
mkdir -p $B/labkit/vendor/python $B/isi/bem
curl -sSLo $W/py.zip https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip
python3 -m pip download numpy==1.26.4 --platform win_amd64 --python-version 3.11 --only-binary=:all: --no-deps -d $W -q
git clone -q --depth 1 https://github.com/Nikolaos-Matthaiakakis/MNPBEM.git $W/mnpbem
unzip -q $W/py.zip -d $B/labkit/vendor/python
unzip -q $W/numpy-1.26.4-cp311-cp311-win_amd64.whl -d $B/labkit/vendor/python
rm -rf $W/mnpbem/.git; mv $W/mnpbem $B/labkit/vendor/MNPBEM
(cd $REPO/labkit && tar cf - --exclude=output --exclude=vendor --exclude='results_*.zip' --exclude=__pycache__ .) | (cd $B/labkit && tar xf -)
cp -r $REPO/isi/bem/extra $B/isi/bem/
printf '@echo off\r\ncall "%%~dp0labkit\\START.bat" %%*\r\n' > $B/START.bat
mkdir -p $REPO/offline; rm -f $REPO/offline/maghale_lab_offline.zip
(cd $W && zip -qr -9 $REPO/offline/maghale_lab_offline.zip maghale_lab)
rm -rf $W
ls -la $REPO/offline/maghale_lab_offline.zip
