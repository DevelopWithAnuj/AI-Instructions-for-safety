"""Guardrail 4: never delete files, folders or data."""
import re
from common import block

RULES = [
    (r"(?<![\w.-])(rm|rmdir|unlink|shred|trash|trash-put|rimraf|truncate)(?![\w-])",
     "delete command (rm, rmdir, unlink, shred, trash, rimraf, truncate)"),
    (r"(?<!\w)--?delete\b", "delete flag (for example find -delete, rsync --delete)"),
    (r"(?<![\w-])prune(?![\w-])", "prune command"),
    (r"(?:\bos\.(?:remove|unlink|rmdir|removedirs)|\bshutil\.rmtree|\brmtree"
     r"|\.unlink\s*\(|\bfs\.(?:rm|rmSync|unlink|unlinkSync|rmdir|rmdirSync))",
     "delete call inside a script"),
    (r"Remove-Item", "PowerShell delete"),
    (r"\bmv\s+[^;|&]*\s/dev/null", "moving a file to /dev/null"),
]
COMPILED = [(re.compile(p, re.I), why) for p, why in RULES]


def check(ctx):
    cmd = ctx["command"]
    if not cmd:
        return
    for rx, why in COMPILED:
        if rx.search(cmd):
            block("deleting is not allowed: " + why + ". Ask the user to do it.")
