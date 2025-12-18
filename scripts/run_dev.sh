
#!/usr/bin/env bash
set -e
export PYTHONPATH="$(pwd)/src"
source .venv/bin/activate
python -m ai_os.main
