"""Phase 4: the outside world is closed. Only the user can open it.

Unlock: the user creates an empty file  .agents/ALLOW_NET  by hand.
Lock again: the user removes that file.
Agents must never create, edit or mention that file in a command.
Git and database blocks stay on even when unlocked."""
import re
from common import ROOT, block

FLAG = ROOT / ".agents" / "ALLOW_NET"
NET_TOOLS = {"webfetch", "websearch", "artifact"}

NET_CMD = re.compile(
    r"(?<![\w.-])(curl|wget|ssh|scp|sftp|ftp|telnet|nc|ncat|netcat|socat|rsync|aria2c)(?![\w-])",
    re.I)
PKG = re.compile(
    r"(?<![\w.-])(npm|pnpm|yarn|bun|pip|pip3|pipx|uv|poetry|cargo|go|gem|brew|apt|apt-get"
    r"|dnf|yum|composer|nuget|dotnet)(?![\w-])\s+(?:[^;|&\n]*?\s)?"
    r"(install|i|add|ci|update|upgrade|get|require|restore)(?=\s|$)",
    re.I)
RUNNERS = re.compile(
    r"(?<![\w.-])(npx|bunx)(?![\w-])|\b(pnpm\s+dlx|yarn\s+dlx|npm\s+exec)\b", re.I)


def net_unlocked():
    try:
        return FLAG.is_file()
    except Exception:
        return False


def check(ctx):
    for p in ctx["paths"]:
        if "ALLOW_NET" in p:
            block("only the user can create or change .agents/ALLOW_NET.")
    cmd = ctx["command"]
    if "ALLOW_NET" in cmd:
        block("only the user can create or change .agents/ALLOW_NET.")
    if net_unlocked():
        return
    tool = ctx["tool"].lower()
    if tool in NET_TOOLS:
        block(ctx["tool"] + " is closed. The user can unlock network with .agents/ALLOW_NET.")
    if ctx["is_mcp"]:
        block("MCP tools are closed. The user can unlock them with .agents/ALLOW_NET.")
    if cmd:
        if NET_CMD.search(cmd):
            block("network commands (curl, wget, ssh and similar) are closed. "
                  "The user can unlock with .agents/ALLOW_NET.")
        if PKG.search(cmd) or RUNNERS.search(cmd):
            block("package installs and runners need the network. "
                  "The user can unlock with .agents/ALLOW_NET.")
