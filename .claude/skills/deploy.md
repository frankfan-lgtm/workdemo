---
name: deploy
description: "Pre-deploy checks, generate setup script, commit & push. Use when user wants to deploy/publish the project."
user_invocable: true
---

# Deploy Skill

One-command deploy: validate, build setup script, commit, push.

## Workflow

### 1. Python 3.9 Compatibility Check

Scan all `.py` files for syntax that requires Python 3.10+:

- `X | Y` union type hints in function signatures and variable annotations (e.g., `-> dict | None`, `tools: list[dict] | None = None`)
- Fix: add `from __future__ import annotations` at top of each affected file, or use `Optional[X]` / `Union[X, Y]` from `typing`

Run this grep to find issues:
```bash
grep -rn '| None' --include='*.py' .
grep -rn ') -> .* | ' --include='*.py' .
```

For each affected file that does NOT already have `from __future__ import annotations`, add it right after the module docstring.

### 2. Import Validation

Run a quick import check to make sure the app loads:
```bash
python3 -c "from app import app; print('Import OK')"
```

If it fails, diagnose and fix the error. Common issues:
- Missing `from __future__ import annotations`
- `list[str]` / `dict[str, X]` in dataclass fields (needs `__future__` annotations or `List`/`Dict` from typing)
- Missing dependencies

### 3. Startup Smoke Test

Quick test that uvicorn can start:
```bash
timeout 5 python3 -c "import uvicorn; uvicorn.run('app:app', host='127.0.0.1', port=18765)" 2>&1 || true
```

Verify the output contains "Application startup complete". If not, debug and fix.

### 4. Regenerate create_project.sh

Run this Python script to regenerate the setup script with all current files:

```python
import base64, os

files_to_pack = [
    'app.py', 'requirements.txt', '.env.example', '.gitignore',
    'agent/__init__.py', 'agent/llm.py', 'agent/intent.py', 'agent/router.py',
    'agent/search/__init__.py', 'agent/search/community.py',
    'agent/search/doubao_web.py', 'agent/search/rag.py', 'agent/search/user_assets.py',
    'static/css/style.css', 'static/js/app.js', 'templates/index.html',
]

lines = ['#!/bin/bash', 'set -e', 'echo "Creating project files..."', '']
for fpath in files_to_pack:
    with open(fpath, 'rb') as f:
        content = base64.b64encode(f.read()).decode()
    dirpart = os.path.dirname(fpath)
    if dirpart:
        lines.append(f'mkdir -p "{dirpart}"')
    lines.append(f'echo "{content}" | base64 -d > "{fpath}"')
    lines.append('')
lines.append('echo "All files created successfully!"')
lines.append('echo "Run: python3 app.py"')

with open('create_project.sh', 'w') as f:
    f.write('\n'.join(lines))
```

If new Python/HTML/CSS/JS files were added to the project, include them in `files_to_pack`.
IMPORTANT: Never include `.env` in the pack (it contains secrets).

### 5. Commit & Push

- Stage all changed files
- Commit with message: `chore: deploy - regenerate setup script with latest changes`
- Push to the current branch

### 6. Output

Print a summary:
```
Deploy complete!
- Python 3.9 compat: OK (N files checked)
- Import check: OK
- Startup test: OK
- Setup script: regenerated
- Pushed to: <branch-name>

User can run on their Mac:
  cd ~/jimeng-search-agent
  curl -sL <raw-github-url>/create_project.sh | bash
  cat > .env << 'EOF'
  ARK_API_KEY=...
  ARK_BASE_URL=...
  ARK_MODEL=...
  EOF
  python3 app.py
```
