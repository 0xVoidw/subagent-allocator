#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 scripts/validate.py

mkdir -p dist
rm -f dist/subagent-allocator.skill

python3 - <<'PY'
from pathlib import Path
import zipfile

source = Path("skills") / "subagent-allocator"
output = Path("dist") / "subagent-allocator.skill"

with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(source.rglob("*")):
        if path.is_file():
            archive.write(path, path.relative_to("skills").as_posix())

print("打包完成：%s" % output.as_posix())
with zipfile.ZipFile(output) as archive:
    for name in archive.namelist():
        print("  %s" % name)
PY
