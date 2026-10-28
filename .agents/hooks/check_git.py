"""Guardrail 2: no git or GitHub commands. The user runs them."""
import re
from common import block

GIT_CMD = re.compile(r"(?<![\w.-])(git|gh|hub|glab|git-lfs)(?![\w-])", re.I)
GIT_API = re.compile(r"api\.github\.com|gitlab\.com/api|api\.bitbucket\.org", re.I)
GIT_MCP = re.compile(r"github|gitlab|bitbucket", re.I)


def check(ctx):
    cmd = ctx["command"]
    if cmd:
        if GIT_CMD.search(cmd):
            block("git and GitHub commands are not allowed. The user runs them.")
        if GIT_API.search(cmd):
            block("calling GitHub, GitLab or Bitbucket APIs is not allowed.")
    tool = ctx["tool"]
    if tool.lower().startswith("mcp") and GIT_MCP.search(tool):
        block("git hosting tools (GitHub, GitLab, Bitbucket) are not allowed.")
