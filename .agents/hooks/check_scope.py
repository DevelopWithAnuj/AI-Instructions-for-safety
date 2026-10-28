"""Guardrail 5: stay inside the project folder."""
import os
import re
from pathlib import Path
from common import ROOT, block

SAFE = {"/dev/null", "/dev/stdout", "/dev/stderr", "/dev/stdin"}
ABS = re.compile(r"(?<![\w:./-])(/[^\s'\"`;|&()<>]+)")
BARE_ROOT = re.compile(r"(?:^|\s)/(?=\s|$)")
DOTDOT = re.compile(r"(?:^|[\s='\"/])\.\.(?=/|\s|$|['\"])")
HOME = re.compile(r"(?:^|[\s='\"])~(?=/|\s|$|['\"])|\$\{?HOME\b")


def inside(p):
    try:
        r = Path(os.path.expanduser(p))
        if not r.is_absolute():
            r = ROOT / r
        r = r.resolve()
    except Exception:
        return False
    return r == ROOT or ROOT in r.parents


def check(ctx):
    for p in ctx["paths"]:
        if not inside(p):
            block("path is outside the project folder: " + p)
    cmd = ctx["command"]
    if not cmd:
        return
    if DOTDOT.search(cmd):
        block("command uses '..' to leave the folder. Use paths inside the project.")
    if HOME.search(cmd):
        block("command touches the home folder, which is outside the project.")
    if BARE_ROOT.search(cmd):
        block("command touches the system root folder.")
    for m in ABS.finditer(cmd):
        p = m.group(1)
        if p in SAFE:
            continue
        if not inside(p):
            block("command uses a path outside the project folder: " + p)
