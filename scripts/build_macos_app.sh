#!/usr/bin/env bash
set -euo pipefail
python -m pip install --upgrade pip
pip install py2app

cat > setup_py2app.py <<'PY'
from setuptools import setup

APP = ['src/c2t/__main__.py']
OPTIONS = {'argv_emulation': True, 'packages': ['c2t']}
setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
PY

python setup_py2app.py py2app || true
mkdir -p dist/macos
if [ -d "dist/c2t.app" ]; then
  mv dist/c2t.app dist/macos/
fi
echo "macOS app (if built) in dist/macos"
