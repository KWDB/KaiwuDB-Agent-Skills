#!/usr/bin/env bash
set -euo pipefail

version="${1:-1.0.0}"
owner="${CLAWHUB_OWNER:-}"

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

owner_args=()
if [[ -n "$owner" ]]; then
  owner_args=(--owner "$owner")
fi

clawhub skill publish skills/kwdb-install-deploy \
  --slug kwdb-install-deploy \
  --name "KWDB Install Deploy" \
  --version "$version" \
  --tags latest,kwdb,ready \
  "${owner_args[@]}"

clawhub skill publish skills/kwdb-text2sql-aiot \
  --slug kwdb-text2sql-aiot \
  --name "KWDB Text2SQL AIoT" \
  --version "$version" \
  --tags latest,kwdb,ready \
  "${owner_args[@]}"
