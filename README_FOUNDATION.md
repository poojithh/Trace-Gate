# TraceGate — Database Foundation

## Setup (Windows PowerShell)

```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

## Initialize the database

```powershell
python -c "from database.connection import initialize_database; initialize_database(); print('TraceGate database initialized')"
```

## Run tests

```powershell
python -m pytest -q
```

The default database path is `data/tracegate.db`. Uploaded documents will later be stored under `data/uploads/`.

Submission versions are immutable. Corrections must create a new version rather than overwrite an old snapshot.
