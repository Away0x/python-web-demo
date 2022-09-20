# Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi "uvicorn[standard]"

uvicorn main:app --reload
```