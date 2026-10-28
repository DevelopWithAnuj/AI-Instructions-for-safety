"""Guardrail 3: never touch the database directly, never delete data.
This is blocked always, even after the user approves."""
import re
from common import block

CLIENTS = re.compile(
    r"(?<![\w.-])(psql|pgcli|pg_dump|pg_restore|pg_dumpall|mysql|mysqlsh|mysqldump|mycli|mariadb"
    r"|sqlite3|litecli|sqlcmd|mongo|mongosh|redis-cli|cqlsh|clickhouse-client|cockroach|usql)(?![\w-])",
    re.I)
TOOLS = re.compile(
    r"prisma\s+(migrate|db|studio)|supabase\s+db|drizzle-kit|(?<![\w-])alembic(?![\w-])"
    r"|knex\s+(migrate|seed)|sequelize(-cli)?\s+db|typeorm\s+(migration|schema)|flask\s+db"
    r"|manage\.py\s+(migrate|flush|dbshell|sqlflush|loaddata|sqlmigrate)"
    r"|artisan\s+(migrate|db:)|(rails|rake)\s+db:|wrangler\s+d1|firebase\s+(firestore|database)"
    r"|(?<![\w-])(turso|neonctl|pscale|flyway|liquibase|dbmate|mikro-orm)(?![\w-])"
    r"|sqlx\s+(migrate|database)|atlas\s+(migrate|schema)",
    re.I)
SQL = re.compile(
    r"\b(drop|truncate)\s+(table|database|schema|index|view|column|user|role)\b"
    r"|\bdelete\s+from\b|\balter\s+table\b",
    re.I)
NOSQL = re.compile(
    r"\b(flushall|flushdb)\b"
    r"|\.(deleteMany|deleteOne|dropDatabase|dropCollection|findOneAndDelete)\s*\("
    r"|\bdb\.\w+\.(drop|remove)\s*\("
    r"|\bredis\w*\.(del|unlink|flushall|flushdb)\b",
    re.I)
CONTAINER_EXEC = re.compile(
    r"(?<![\w-])(docker|docker-compose|podman|nerdctl|kubectl|oc)(?![\w-])[^;|&\n]*\b(exec|attach)\b",
    re.I)
URL = re.compile(r"\b(postgres(ql)?|mysql|mongodb(\+srv)?|rediss?|mssql|sqlserver)://", re.I)
MCP = re.compile(
    r"sql|postgres|supabase|mongo|database|redis|neon|planetscale|turso|firestore|dynamo"
    r"|(?<![a-z])db(?![a-z])",
    re.I)
DBFILE = re.compile(r"\.(db|sqlite|sqlite3|mdb)$", re.I)


def check(ctx):
    cmd = ctx["command"]
    if cmd:
        if CLIENTS.search(cmd):
            block("database clients are not allowed. The user touches the database.")
        if TOOLS.search(cmd):
            block("database tools and migrations are not allowed without the user.")
        if SQL.search(cmd):
            block("destructive SQL (DROP, TRUNCATE, DELETE FROM, ALTER) is not allowed.")
        if NOSQL.search(cmd):
            block("Mongo or Redis delete and flush operations are not allowed.")
        if CONTAINER_EXEC.search(cmd):
            block("docker exec and similar can reach the database. Not allowed.")
        if URL.search(cmd):
            block("database connection strings are not allowed in commands.")
    if ctx["is_mcp"] and MCP.search(ctx["tool"]):
        block("database tools (MCP) are not allowed.")
    for p in ctx["paths"]:
        if DBFILE.search(p):
            block("database files cannot be read or written directly: " + p)
