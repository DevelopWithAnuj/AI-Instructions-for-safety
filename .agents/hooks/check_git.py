"""Guardrail 2: git is read-only. Only status, diff, log, show, branch (list) are allowed.
Everything else, and every gh/hub/glab call, is blocked. The user runs the rest."""
import os
import re
import shlex
from common import block, segments

GIT_CMD = re.compile(r"(?<![\w.-])(git|gh|hub|glab|git-lfs)(?![\w-])", re.I)
GIT_API = re.compile(r"api\.github\.com|gitlab\.com/api|api\.bitbucket\.org", re.I)
GIT_MCP = re.compile(r"github|gitlab|bitbucket", re.I)

ALLOWED = ("status", "diff", "log", "show", "branch")
BRANCH_OK = {"-a", "--all", "-r", "--remotes", "-v", "-vv", "--verbose", "--list",
             "--show-current"}
BAD_ARGS = ("--output", "-O", "--ext-diff", "--textconv", "--exec-path",
            "--upload-pack", "--receive-pack", "--git-dir", "--work-tree")


def check_text(text):
    """For script contents: any git or GitHub use is blocked."""
    if GIT_CMD.search(text) or GIT_API.search(text):
        block("this script uses git or GitHub. The user runs those.")


def _check_segment(seg):
    if not GIT_CMD.search(seg):
        return
    if re.search(r"[<>]", seg):
        block("git with redirects is not allowed.")
    try:
        tokens = shlex.split(seg)
    except ValueError:
        block("could not read this git command safely.")
    while tokens and re.match(r"^\w+=", tokens[0]):
        tokens.pop(0)
    if not tokens:
        block("could not read this git command safely.")
    name = os.path.basename(tokens[0]).lower()
    if name.endswith(".exe"):
        name = name[:-4]
    if name != "git":
        block("only plain read-only git is allowed. gh, hub, glab and git inside other "
              "commands are blocked.")
    rest = tokens[1:]
    if not rest:
        block("plain 'git' is not allowed. Allowed: status, diff, log, show, branch (list).")
    sub = rest[0]
    if sub not in ALLOWED:
        block("git " + sub + " is not allowed. Allowed: status, diff, log, show, "
              "branch (list). The user runs the rest.")
    args = rest[1:]
    for a in args:
        if a.startswith(BAD_ARGS):
            block("git option " + a + " can write files or run programs.")
    if sub == "branch":
        for a in args:
            if a not in BRANCH_OK:
                block("git branch is list-only. Creating, renaming or deleting is blocked.")


def check(ctx):
    cmd = ctx["command"]
    if cmd:
        if GIT_API.search(cmd):
            block("calling GitHub, GitLab or Bitbucket APIs is not allowed.")
        for seg in segments(cmd):
            _check_segment(seg)
    if ctx["is_mcp"] and GIT_MCP.search(ctx["tool"]):
        block("git hosting tools (GitHub, GitLab, Bitbucket) are not allowed.")
