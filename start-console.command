#!/usr/bin/env bash
set -euo pipefail

cd "$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VERSION="$(cat VERSION 2>/dev/null || echo dev)"
printf '破甲next · macOS 装载台 v%s\n' "$VERSION"
chmod +x pojia-console.sh wb-macos.py wb-guard.sh inject-workbuddy-identity.py 2>/dev/null || true
exec ./pojia-console.sh menu
