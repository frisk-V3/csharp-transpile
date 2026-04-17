#!/usr/bin/env bash
set -euo pipefail
PKG_NAME=${1:-csharp-transpile}
PKG_VERSION=${2:-0.1.0}

rm -rf pkgroot
mkdir -p pkgroot/usr/local/bin
mkdir -p pkgroot/usr/local/lib/python3.10/site-packages

python -m pip install --upgrade pip
python -m pip install --target pkgroot/usr/local/lib/python3.10/site-packages dist/wheels/*.whl

cat > pkgroot/usr/local/bin/c2t <<'PY'
#!/usr/bin/env python3
import sys
from c2t.__main__ import main
if __name__ == "__main__":
    main()
PY
chmod +x pkgroot/usr/local/bin/c2t

if ! command -v fpm >/dev/null 2>&1; then
  echo "fpm not found. Install with: sudo gem install --no-document fpm"
  exit 1
fi

fpm -s dir -t deb -n "${PKG_NAME}" -v "${PKG_VERSION}" --prefix=/ -C pkgroot usr/local/bin usr/local/lib || true
mkdir -p dist/deb
mv *.deb dist/deb/ || true
echo "Deb packages in dist/deb"
