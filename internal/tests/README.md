# Test

Run tests using the project venv and pytest:

```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install pytest pytest-cov -q

# Run tests with coverage
PYTHONPATH=skills/kwdb-intelligent-inspection/scripts:internal/tests/kwdb-intelligent-inspection/scripts \
  python -m pytest \
  internal/tests/kwdb-intelligent-inspection/scripts/test_get_kwdb_statements.py \
  internal/tests/kwdb-intelligent-inspection/scripts/test_get_kwdb_ts_metrics.py \
  --cov=skills/kwdb-intelligent-inspection/scripts \
  --cov-report=term-missing -v
```