# Author: Mark Blakeney, Feb 2024.
'Common module containing shared functions'
from __future__ import annotations

import subprocess
import sys
from typing import Optional

def run(cmd: str, *, capture: bool = False, quiet: bool = False,
        shell=True, ignore_error=False) -> Optional[str]:
    'Run given command string'
    if capture:
        stdout = subprocess.PIPE
    else:
        stdout = None
        if not quiet:
            print(f'>>> Running {cmd}')
    try:
        res = subprocess.run(cmd if shell else cmd.split(), shell=shell,
                             stdout=stdout, universal_newlines=True)
    except Exception as e:
        if not ignore_error:
            print(f'{cmd} failed: {e}', file=sys.stderr)
        return None

    if res.returncode != 0:
        return None

    return (res.stdout and res.stdout.strip()) if capture else 'ok'
