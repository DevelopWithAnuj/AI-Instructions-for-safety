"""Phase 1: close the common ways to hide a blocked command."""
import re
from common import block

INTERP = (r"(?:python[\d.]*|py|node|nodejs|deno|bun|perl|ruby|php|lua|bash|sh|zsh|dash"
          r"|ksh|fish|pwsh|powershell)")

RULES = [
    (INTERP + r"(?![\w-])[^;|&\n]*?\s-[a-zA-Z]*[ceEpr](?=\s|$|['\"])",
     "inline code (python -c, sh -c, node -e) is not allowed"),
    (r"\s--(eval|command|exec)\b", "inline code (--eval, --command) is not allowed"),
    (r"(?<![\w.-])eval(?![\w-])", "eval is not allowed"),
    (r"\$\(|`", "command substitution ($(...) or backticks) is not allowed"),
    (r"base64\s+(-d|--decode)|\bxxd\s+-r|openssl\s+enc\s+-d",
     "decoding hidden commands is not allowed"),
    (INTERP + r"(?![\w-])[^;|&\n]*<<", "feeding a script through a heredoc is not allowed"),
    (INTERP + r"(?![\w-])\s+-(?=\s|$)", "running a script from stdin is not allowed"),
    (r"\|\s*(?:sudo\s+)?" + INTERP + r"(?![\w-])",
     "piping into a shell or interpreter is not allowed"),
    (r"(?<![\w.-])(xargs|parallel)(?![\w-])", "xargs and parallel can run hidden commands"),
    (r"(?<![\w-])-(exec|execdir|ok|okdir)(?![\w-])", "find -exec can run hidden commands"),
    (r"(?<![\w.-])ln(?![\w-])", "links (ln) can escape the project folder"),
]
COMPILED = [(re.compile(p, re.I), why) for p, why in RULES]


def check(ctx):
    cmd = ctx["command"]
    if not cmd:
        return
    for rx, why in COMPILED:
        if rx.search(cmd):
            block(why + ". Run the plain command, or ask the user.")
