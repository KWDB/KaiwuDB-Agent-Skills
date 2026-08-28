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

clawhub skill publish skills/kwdb-intelligent-inspection \
  --slug kwdb-intelligent-inspection \
  --name "KWDB Intelligent Inspection" \
  --version "$version" \
  --tags latest,kwdb,ready \
  "${owner_args[@]}"

clawhub skill publish skills/kwdb-performance-review \
  --slug kwdb-performance-review \
  --name "KWDB Performance Review" \
  --version "$version" \
  --tags latest,kwdb,ready \
  "${owner_args[@]}"

clawhub skill publish skills/kwdb-troubleshooting \
  --slug kwdb-troubleshooting \
  --name "KWDB Troubleshooting" \
  --version "$version" \
  --tags latest,kwdb,ready \
  "${owner_args[@]}"

clawhub skill publish skills/kwdb-ts-anomaly-detection \
  --slug kwdb-ts-anomaly-detection \
  --name "KWDB Time-Series Anomaly Detection" \
  --version "$version" \
  --tags latest,kwdb,ready \
  "${owner_args[@]}"

clawhub skill publish skills/kwdb-build \
  --slug kwdb-build \
  --name "KWDB Build" \
  --version "$version" \
  --tags latest,kwdb,ready \
  "${owner_args[@]}"

clawhub skill publish skills/kwdb-schema-design \
  --slug kwdb-schema-design \
  --name "KWDB Schema Design" \
  --version "$version" \
  --tags latest,kwdb,ready \
  "${owner_args[@]}"

clawhub skill publish skills/kwdb-data-migration \
  --slug kwdb-data-migration \
  --name "KWDB Data Migration" \
  --version "$version" \
  --tags latest,kwdb,ready \
  "${owner_args[@]}"
