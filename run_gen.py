"""
Run gen-pydantic and gen-project with UTF-8 output on Windows.

Background
----------
Windows CMD uses the system code page (cp1252 / charmap) for stdout.
The LinkML generators embed Unicode characters (→, etc.) in their output
which cannot be encoded by cp1252.  This script bypasses the issue by:
  - calling the Pydantic generator via the Python API and writing the output
    file directly in UTF-8 mode
  - calling gen-project via subprocess with PYTHONIOENCODING=utf-8

On Linux/macOS the standard CLI commands work fine without this wrapper.

Usage
-----
    python run_gen.py

Or for gen-pydantic only on Windows cmd / PowerShell:
    set PYTHONIOENCODING=utf-8
    uv run gen-pydantic src/inkind_knowledge_repo/schema/inkind_knowledge_repo.yaml > ...
"""
import subprocess
import sys
import os
import traceback

env = {**os.environ, 'PYTHONIOENCODING': 'utf-8'}
schema = 'src/inkind_knowledge_repo/schema/inkind_knowledge_repo.yaml'

# ── gen-pydantic (Python API — avoids stdout encoding issues entirely) ────────
print("=== gen-pydantic ===")
try:
    from linkml.generators.pydanticgen import PydanticGenerator
    gen = PydanticGenerator(schema)
    output = gen.serialize()
    out_path = 'src/inkind_knowledge_repo/datamodel/inkind_knowledge_repo_pydantic.py'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)
    print(f"SUCCESS: {len(output):,} chars -> {out_path}")
except Exception as e:
    print("ERROR:", e)
    traceback.print_exc()

# ── gen-project (subprocess with PYTHONIOENCODING=utf-8) ─────────────────────
print()
print("=== gen-project ===")
gen_exe = os.path.join('.venv', 'Scripts', 'gen-project.exe')
if not os.path.exists(gen_exe):
    gen_exe = os.path.join('.venv', 'Scripts', 'gen-project')

result = subprocess.run(
    [gen_exe, '--config-file', 'config.yaml', '-d', 'project', schema],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='replace',
    env=env,
)
if result.returncode != 0:
    print(f"FAILED (return code {result.returncode})")
    print(result.stderr[:4000])
else:
    print("SUCCESS")
    # Filter out the known urllib3 version mismatch warning
    warnings = [
        line for line in result.stderr.splitlines()
        if line.strip()
        and 'RequestsDependency' not in line
        and 'warnings.warn' not in line
    ]
    if warnings:
        print("Warnings:\n" + '\n'.join(warnings[:20]))
