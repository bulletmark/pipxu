# Author: Mark Blakeney, Feb 2024.
'Common module containing shared functions'
from __future__ import annotations

import shlex
import subprocess
import sys
from typing import Optional, Sequence

def run(cmd: Sequence[str], *, capture: bool = False,
        quiet: bool = False, ignore_error=False) -> Optional[str]:
    'Run given command'
    # Lazy evaluation of cmdstr
    cmdstr = None

    if capture:
        stdout = subprocess.PIPE
    else:
        stdout = None
        if not quiet:
            if not cmdstr:
                cmdstr = shlex.join(cmd)
            print(f'>>> Running {cmdstr}')
    try:
        res = subprocess.run(cmd, stdout=stdout, text=True)
    except Exception as e:
        if not ignore_error:
            if not cmdstr:
                cmdstr = shlex.join(cmd)
            print(f'{cmdstr} failed: {e}', file=sys.stderr)
        return None

    if res.returncode != 0:
        return None

    return (res.stdout and res.stdout.strip()) if capture else 'ok'
