import json
import types
import asyncio
import sys
import io
import os
import threading
import subprocess
import inspect
import concurrent.futures as cf
import zipfile
import time as _time
import datetime
import re
import urllib.request as _urllib_req
from typing import List, Optional

import discord
from discord.ext import commands, tasks
from discord import app_commands

# ============================================================
#   NightCloud XP Checker Bot — Public Multi-Server Bot
#   Set your bot token and owner ID below before running
# ============================================================
TOKEN    ="MTQ5NDcwMDU1NzE4Mzc1MDE1NA.GnlijK.pFYxk-y1d5l50TSlCiojWokvh5vuz4FDYb2Diw"
OWNER_ID = 1406302154586718220  # Global bot owner (your Discord ID)
WEBHOOK  = "https://discord.com/api/webhooks/1447612558596116723/Gm1iL_Jii4ertOR_4iuvw2Qi12FxtfBMONwEdHq6OiaLH4PGmOE6OrarLl1Cn2-vHCDe"
# ============================================================

# ─── NightCloud Custom Emoji Constants ───────────────────────
E_BOOKS     = "<a:Books_:1494702836645368039>"
E_NOTES     = "<:Nc_Notes:1494678310549192714>"
E_AXE       = "<a:NeAxe:1494702882388181063>"
E_STAR      = "<a:Star:1494702845377904811>"
E_XBOX      = "<:Xbox:1494702971223543850>"
E_ADD       = "<:_add:1494690584365895841>"
E_BANS      = "<:bans:1494702849207177496>"
E_BOOST     = "<a:bosst:1494702781917823158>"
E_EMAIL     = "<:email:1494702924423626753>"
E_LINE      = "<a:line:1494702878248534108>"
E_LINKS     = "<:links:1494705729528139887>"
E_OFFLINE   = "<a:nc_Offline:1494675886790672435>"
E_ONLINE    = "<a:nc_Online:1494675909331124304>"
E_ANNOUNCE  = "<a:nc_announcement:1494677518693957632>"
E_ARROW     = "<a:nc_arrow:1494371876447719424>"
E_ANALYSIS  = "<:nc_analysis:1494677760273027163>"
E_UNLOCKED  = "<:nc_unlocked:1494678003354173450>"
E_TICK      = "<a:nc_tick:1494677197523517510>"
E_YELLOW    = "<a:s_yellow:1494702871818666098>"
E_TIMER     = "<a:timer:1494702811685064784>"
E_WARNING   = "<a:nc_warningbug:1494678349950484673>"
E_DOT       = "<a:nc_dot:1494675772688961698>"
E_GOLD      = "<:gold:1494702774376599636>"
E_HEARTS    = "<a:hearts_blue:1494702766378193057>"

# Semantic aliases — keep the rest of the code working unchanged
E_SPARKLE       = E_STAR
E_UPLOAD        = E_ADD
E_DIAMOND       = E_GOLD
E_GREEN         = E_ONLINE
E_BOOSTER       = E_BOOST
E_COPPER        = E_ANALYSIS
E_DIAMOND_VAULT = E_BOOKS
E_DONUT         = E_HEARTS
E_BAN           = E_BANS
E_BOX           = E_NOTES
E_REASON        = E_ANNOUNCE
E_GREENDOT      = E_DOT
E_STOCK_YELLOW  = E_YELLOW
E_STOCK_BROWN   = E_TIMER
E_STOCK_PINK    = E_WARNING

EMOJI_MANIFEST = [
    ("Books_",          1494702836645368039, True),
    ("Nc_Notes",        1494678310549192714, False),
    ("NeAxe",           1494702882388181063, True),
    ("Star",            1494702845377904811, True),
    ("Xbox",            1494702971223543850, False),
    ("_add",            1494690584365895841, False),
    ("bans",            1494702849207177496, False),
    ("bosst",           1494702781917823158, True),
    ("email",           1494702924423626753, False),
    ("line",            1494702878248534108, True),
    ("links",           1494705729528139887, False),
    ("nc_Offline",      1494675886790672435, True),
    ("nc_Online",       1494675909331124304, True),
    ("nc_announcement", 1494677518693957632, True),
    ("nc_arrow",        1494371876447719424, True),
    ("nc_analysis",     1494677760273027163, False),
    ("nc_unlocked",     1494678003354173450, False),
    ("nc_tick",         1494677197523517510, True),
    ("s_yellow",        1494702871818666098, True),
    ("timer",           1494702811685064784, True),
    ("nc_warningbug",   1494678349950484673, True),
    ("nc_dot",          1494675772688961698, True),
    ("gold",            1494702774376599636, False),
    ("hearts_blue",     1494702766378193057, True),
]

_EMOJI_FALLBACKS = {
    # Semantic names used by ge() calls throughout the bot
    "sparkle":       E_STAR,
    "upload":        E_ADD,
    "diamond":       E_GOLD,
    "green":         E_ONLINE,
    "booster":       E_BOOST,
    "copper":        E_ANALYSIS,
    "diamond_vault": E_BOOKS,
    "donut":         E_HEARTS,
    "ban":           E_BANS,
    "box":           E_NOTES,
    "arrow":         E_ARROW,
    "reason":        E_ANNOUNCE,
    "greendot":      E_DOT,
    "stock_yellow":  E_YELLOW,
    "stock_brown":   E_TIMER,
    "stock_pink":    E_WARNING,
    # Direct NightCloud emoji names (for guilds that have them installed)
    "Books_":          E_BOOKS,
    "Nc_Notes":        E_NOTES,
    "NeAxe":           E_AXE,
    "Star":            E_STAR,
    "Xbox":            E_XBOX,
    "_add":            E_ADD,
    "bans":            E_BANS,
    "bosst":           E_BOOST,
    "email":           E_EMAIL,
    "line":            E_LINE,
    "links":           E_LINKS,
    "nc_Offline":      E_OFFLINE,
    "nc_Online":       E_ONLINE,
    "nc_announcement": E_ANNOUNCE,
    "nc_arrow":        E_ARROW,
    "nc_analysis":     E_ANALYSIS,
    "nc_unlocked":     E_UNLOCKED,
    "nc_tick":         E_TICK,
    "s_yellow":        E_YELLOW,
    "timer":           E_TIMER,
    "nc_warningbug":   E_WARNING,
    "nc_dot":          E_DOT,
    "gold":            E_GOLD,
    "hearts_blue":     E_HEARTS,
}

# ─── Xpchecker emojis (progress embeds) ──────────────────────
UNLOCK_EMOJI  = E_UNLOCKED
ALERT_EMOJI   = E_WARNING
LOADING_EMOJI = E_TIMER

# ─── Colours ─────────────────────────────────────────────────
C_MAIN   = 0x1A1C20
C_OK     = 0x57F287
C_ERR    = 0xED4245
C_WARN   = 0xF0A500
C_INFO   = 0x5865F2
C_GOLD   = 0xFFD700
C_DARK   = 0x2B2D31
C_PURPLE = 0x9B59B6

SEPARATOR = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"

# ─── Emoji helpers ────────────────────────────────────────────
def ge(name: str, guild=None) -> str:
    # Always prefer hardcoded NightCloud constants — this ensures the
    # correct emoji is shown even if the guild still has old-named emojis
    # installed from a previous /installemoji run.
    if name in _EMOJI_FALLBACKS:
        return _EMOJI_FALLBACKS[name]
    # Fallthrough: try live guild/bot emoji cache for any unknown name
    if guild is not None:
        emoji = discord.utils.get(guild.emojis, name=name)
        if emoji:
            prefix = "a" if emoji.animated else ""
            return f"<{prefix}:{emoji.name}:{emoji.id}>"
    emoji = discord.utils.get(bot.emojis, name=name)
    if emoji:
        prefix = "a" if emoji.animated else ""
        return f"<{prefix}:{emoji.name}:{emoji.id}>"
    return f":{name}:"


class _GE:
    __slots__ = ("_guild",)
    def __init__(self, guild):
        self._guild = guild
    def __getattr__(self, item: str):
        return ge(item.lower(), self._guild)


def GuildEmojis(guild) -> _GE:
    return _GE(guild)

# ─── asyncio.to_thread compat (Python < 3.9) ─────────────────
if not hasattr(asyncio, "to_thread"):
    import functools
    async def _to_thread_compat(func, *args, **kwargs):
        loop = asyncio.get_running_loop()
        pfunc = functools.partial(func, *args, **kwargs) if (args or kwargs) else func
        return await loop.run_in_executor(None, pfunc)
    asyncio.to_thread = _to_thread_compat

# ─── Access list ─────────────────────────────────────────────
ACCESS_LIST   = {}
_ACCESS_FILE  = "xpchecker_access.json"


def _is_global_owner(user_id: int) -> bool:
    return OWNER_ID and int(OWNER_ID) == int(user_id)


def _is_guild_owner(guild: discord.Guild, user_id: int) -> bool:
    """Server owner is automatically the bot owner for that guild."""
    return guild is not None and guild.owner_id == int(user_id)


def _is_owner(guild: discord.Guild, user_id: int) -> bool:
    return _is_global_owner(user_id) or _is_guild_owner(guild, user_id)


def _has_access(guild: discord.Guild, user_id: int) -> bool:
    if _is_owner(guild, user_id):
        return True
    exp = ACCESS_LIST.get(int(user_id))
    if exp is None:
        return False
    if exp == -1:
        return True
    return _time.time() < exp


def _load_access_list():
    global ACCESS_LIST
    try:
        if os.path.exists(_ACCESS_FILE):
            with open(_ACCESS_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
                if isinstance(raw, dict):
                    now = _time.time()
                    cleaned = {}
                    for k, v in raw.items():
                        try:
                            uid, ev = int(k), int(v)
                        except Exception:
                            continue
                        if ev == -1 or ev > now:
                            cleaned[uid] = ev
                    ACCESS_LIST = cleaned
    except Exception:
        pass


def _save_access_list():
    try:
        with open(_ACCESS_FILE, "w", encoding="utf-8") as f:
            json.dump({str(k): int(v) for k, v in ACCESS_LIST.items()}, f, indent=2)
    except Exception:
        pass


def _parse_duration(s: str) -> int:
    s = (s or "").strip().lower()
    if s in ("perm", "permanent", "infinite"):
        return -1
    try:
        if s.endswith("mo"):  return int(s[:-2]) * 30 * 24 * 3600
        if s.endswith("d"):   return int(s[:-1]) * 24 * 3600
        if s.endswith("h"):   return int(s[:-1]) * 3600
        if s.endswith("m"):   return int(s[:-1]) * 60
        if s.endswith("s"):   return int(s[:-1])
        return int(s)
    except Exception:
        return 0

# ─── Embed builders ───────────────────────────────────────────
def _footer(embed: discord.Embed, guild=None) -> discord.Embed:
    if bot.user:
        embed.set_footer(text="NightCloud Checker • Public Bot", icon_url=bot.user.display_avatar.url)
    embed.timestamp = datetime.datetime.utcnow()
    return embed


def base_embed(title=None, description=None, color=C_MAIN, guild=None) -> discord.Embed:
    return _footer(discord.Embed(title=title, description=description, color=color), guild)


def ok_embed(desc, title="Success", guild=None) -> discord.Embed:
    dot = ge("greendot", guild)
    return base_embed(f"{dot}  {title}", desc, C_OK, guild)


def error_embed(desc, title="Error", guild=None) -> discord.Embed:
    ban = ge("ban", guild)
    return base_embed(f"{ban}  {title}", desc, C_ERR, guild)


def warn_embed(desc, title="Warning", guild=None) -> discord.Embed:
    sy = ge("stock_yellow", guild)
    return base_embed(f"{sy}  {title}", desc, C_WARN, guild)


def info_embed(desc, title="Info", guild=None) -> discord.Embed:
    sp = ge("sparkle", guild)
    return base_embed(f"{sp}  {title}", desc, C_INFO, guild)

# ─── Per-guild prefix ─────────────────────────────────────────
_GUILD_PREFIXES: dict = {}
_PREFIX_FILE = "nightcloud_prefixes.json"
DEFAULT_PREFIX = "g "


def _load_prefixes():
    global _GUILD_PREFIXES
    try:
        if os.path.exists(_PREFIX_FILE):
            with open(_PREFIX_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
                _GUILD_PREFIXES = {int(k): str(v) for k, v in raw.items()}
    except Exception:
        pass


def _save_prefixes():
    try:
        with open(_PREFIX_FILE, "w", encoding="utf-8") as f:
            json.dump({str(k): v for k, v in _GUILD_PREFIXES.items()}, f, indent=2)
    except Exception:
        pass


def _get_prefix(bot_instance, message):
    if message.guild:
        return _GUILD_PREFIXES.get(message.guild.id, DEFAULT_PREFIX)
    return DEFAULT_PREFIX


# ─── Guild tier system ────────────────────────────────────────
GUILD_TIERS: dict = {}   # guild_id -> "premium" | "booster"
_TIER_FILE = "nightcloud_tiers.json"
NORMAL_SLOTS  = 3
PREMIUM_SLOTS = 6


def _load_tiers():
    global GUILD_TIERS
    try:
        if os.path.exists(_TIER_FILE):
            with open(_TIER_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
                GUILD_TIERS = {int(k): str(v) for k, v in raw.items()}
    except Exception:
        pass


def _save_tiers():
    try:
        with open(_TIER_FILE, "w", encoding="utf-8") as f:
            json.dump({str(k): v for k, v in GUILD_TIERS.items()}, f, indent=2)
    except Exception:
        pass


def _guild_slot_limit(guild_id: int) -> int:
    tier = GUILD_TIERS.get(guild_id, "")
    if tier == "booster":
        return 999999
    if tier == "premium":
        return PREMIUM_SLOTS
    return NORMAL_SLOTS


# ─── Per-guild active run tracking ───────────────────────────
# guild_id -> set of user_ids currently running a check
GUILD_ACTIVE_RUNS: dict = {}


def _guild_active_count(guild_id: int) -> int:
    return len(GUILD_ACTIVE_RUNS.get(guild_id, set()))


def _guild_can_run(guild_id: int) -> bool:
    return _guild_active_count(guild_id) < _guild_slot_limit(guild_id)


def _guild_add_run(guild_id: int, user_id: int):
    GUILD_ACTIVE_RUNS.setdefault(guild_id, set()).add(int(user_id))


def _guild_remove_run(guild_id: int, user_id: int):
    GUILD_ACTIVE_RUNS.get(guild_id, set()).discard(int(user_id))


def _guild_user_running(guild_id: int, user_id: int) -> bool:
    return int(user_id) in GUILD_ACTIVE_RUNS.get(guild_id, set())


# ─── Bot setup ────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix=_get_prefix, intents=intents, help_command=None)

# ─── Engine loader ────────────────────────────────────────────
sm = types.SimpleNamespace()
CURRENT_RUN_NAME   = ""
RESULT_STORE       = {}
RUN_CURRENT_NAME   = {}
RUNS               = {}
ENGINE_AVAILABLE   = False
STOPPING           = False
# Per-user stop flags: user_id -> bool
USER_STOPPING: dict = {}
FIRST_WORKER_ERROR = None
# Per-user first worker errors: user_id -> str
USER_FIRST_WORKER_ERROR: dict = {}
RUNTIME_WEBHOOK: Optional[str] = None

_SOURCE_PATHS = [
    r"C:\\Users\\Al sabith\\Downloads\\silent-mc-checker-main\\silent-mc-checker-main\\SilentRoot MC\\windows\\silentmain.py",
    r"/home/container/silentmain.py",
    r"/home/container/Silent-mc checker/silentmain.py",
]
_loaded = False
_ENGINE_SOURCE = None
_ENGINE_PATH   = None
_last_engine_error: Exception = Exception("Engine not attempted yet")
_attempted_installs: set = set()

_pip_name_map = {
    "socks": ["PySocks"],
    "websocket": ["websocket-client"],
    "PIL": ["pillow"],
    "requests": ["requests"],
    "colorama": ["colorama"],
    "readchar": ["readchar"],
    "bcrypt": ["bcrypt"],
    "bs4": ["beautifulsoup4"],
    "cv2": ["opencv-python"],
    "yaml": ["PyYAML"],
    "aiohttp": ["aiohttp"],
    "psutil": ["psutil"],
}


def _pip_install_for(mod: str) -> bool:
    pkgs = _pip_name_map.get(mod, [mod])
    for pkg in pkgs:
        try:
            r = subprocess.run([sys.executable, "-m", "pip", "install", pkg], check=False)
            if r.returncode == 0:
                return True
        except Exception:
            pass
    return False


def _ensure_stub_modules():
    try:
        from types import ModuleType as _Mod

        def _noop(*a, **k): return None
        def _noop_str(*a, **k): return ""
        def _noop_list(*a, **k): return []

        if "tkinter" not in sys.modules:
            tk = _Mod("tkinter")
            fd = _Mod("tkinter.filedialog")
            fd.askopenfilename = _noop_str
            fd.askdirectory = _noop_str
            tk.filedialog = fd
            sys.modules["tkinter"] = tk
            sys.modules["tkinter.filedialog"] = fd

        # ── minecraft stubs ──────────────────────────────────────
        # Ensure base module exists
        for sub in ("minecraft", "minecraft.networking", "minecraft.networking.connection",
                    "minecraft.networking.packets", "minecraft.authentication", "minecraft.exceptions"):
            if sub not in sys.modules:
                mod = _Mod(sub)
                mod.__path__ = []
                sys.modules[sub] = mod

        # minecraft.networking.connection — Connection stub
        mc_conn = sys.modules["minecraft.networking.connection"]
        if not hasattr(mc_conn, "Connection"):
            class Connection:
                def __init__(self, *a, **k): pass
                def connect(self, *a, **k): pass
                def disconnect(self, *a, **k): pass
                def register_packet_listener(self, *a, **k): pass
            mc_conn.Connection = Connection

        # minecraft.networking.packets — common packet stubs
        mc_pkt = sys.modules["minecraft.networking.packets"]
        for _pkt_name in (
            "Packet", "PacketListener", "LoginDisconnectPacket", "EncryptionRequestPacket",
            "LoginSuccessPacket", "SetCompressionPacket", "LoginPluginRequestPacket",
            "DisconnectPacket", "ChatMessagePacket", "PlayerPositionAndLookPacket",
            "serverbound", "clientbound",
        ):
            if not hasattr(mc_pkt, _pkt_name):
                if _pkt_name in ("serverbound", "clientbound"):
                    sub_mod = _Mod(f"minecraft.networking.packets.{_pkt_name}")
                    sub_mod.__path__ = []
                    setattr(mc_pkt, _pkt_name, sub_mod)
                    sys.modules[f"minecraft.networking.packets.{_pkt_name}"] = sub_mod
                else:
                    class _StubPacket:
                        def __init__(self, *a, **k): pass
                        def read(self, *a, **k): pass
                        def send(self, *a, **k): pass
                    _StubPacket.__name__ = _pkt_name
                    setattr(mc_pkt, _pkt_name, _StubPacket)

        # minecraft.authentication — AuthenticationToken stub
        mc_auth = sys.modules["minecraft.authentication"]
        for _auth_name in ("AuthenticationToken", "Profile", "LoginResponse"):
            if not hasattr(mc_auth, _auth_name):
                class _StubAuth:
                    def __init__(self, *a, **k): pass
                    def authenticate(self, *a, **k): pass
                    def refresh(self, *a, **k): pass
                    def validate(self, *a, **k): return True
                _StubAuth.__name__ = _auth_name
                setattr(mc_auth, _auth_name, _StubAuth)

        # minecraft.exceptions — common exception stubs
        mc_exc = sys.modules["minecraft.exceptions"]
        for _exc_name in ("LoginDisconnect", "VersionMismatch", "YggdrasilError"):
            if not hasattr(mc_exc, _exc_name):
                _StubExc = type(_exc_name, (Exception,), {})
                setattr(mc_exc, _exc_name, _StubExc)

    except Exception:
        pass


_ensure_stub_modules()

for _p in _SOURCE_PATHS:
    try:
        with open(_p, "r", encoding="utf-8", errors="ignore") as f:
            _code = f.read()
    except Exception as e:
        _last_engine_error = e
        continue
    while True:
        try:
            exec(compile(_code, _p, "exec"), sm.__dict__)
            _loaded = True
            _ENGINE_SOURCE = _code
            _ENGINE_PATH   = _p
            break
        except ModuleNotFoundError as e:
            _last_engine_error = e
            mod = getattr(e, "name", None)
            if mod and mod not in _attempted_installs:
                _attempted_installs.add(mod)
                _pip_install_for(mod)
                continue
            break
        except Exception as e:
            _last_engine_error = e
            break
    if _loaded:
        break


def _get_display_hits() -> int:
    def _gi(name):
        try: return int(getattr(sm, name, 0) or 0)
        except: return 0
    base = _gi("hits")
    if base > 0:
        return base
    return _gi("xgp") + _gi("xgpu") + _gi("bedrock")


def make_engine_namespace() -> types.SimpleNamespace:
    ns = types.SimpleNamespace()
    if _ENGINE_SOURCE and _ENGINE_PATH:
        try:
            exec(compile(_ENGINE_SOURCE, _ENGINE_PATH, "exec"), ns.__dict__)
            return ns
        except Exception:
            pass
    try:
        for k, v in sm.__dict__.items():
            ns.__dict__[k] = v
    except Exception:
        pass
    return ns


def _ensure_engine_symbols():
    global ENGINE_AVAILABLE
    if not _loaded:
        ENGINE_AVAILABLE = False
        return
    if not hasattr(sm, "Checker") or not callable(getattr(sm, "Checker", None)):
        candidates = ["Checker", "checker", "check", "run_checker", "start_checker",
                      "main_checker", "check_combo", "run_check", "startcheck"]
        for cand in candidates:
            func = getattr(sm, cand, None)
            if callable(func):
                try:
                    func("test@example.com:password123")
                    sm.Checker = func
                    break
                except Exception:
                    continue
    for _k in ("checked", "hits", "bad", "sfa", "mfa", "twofa", "other", "errors"):
        if not hasattr(sm, _k):
            try: setattr(sm, _k, 0)
            except: pass
    ENGINE_AVAILABLE = hasattr(sm, "Checker") and callable(sm.Checker)


_ensure_engine_symbols()
ENGINE_AVAILABLE = callable(getattr(sm, "Checker", None))

# ─── Result storage helpers ───────────────────────────────────
def _normalize_bytes(b: bytes) -> List[str]:
    s = b.decode("utf-8", errors="ignore")
    out, seen = [], set()
    for ln in (x.strip() for x in s.splitlines() if x.strip()):
        if ln not in seen:
            seen.add(ln)
            out.append(ln)
    return out


def _map_proxy(arg: str) -> str:
    s = (arg or "").lower()
    if s in ("none", "no", "n", "4", "proxyless"): return "'4'"
    if s in ("auto", "5"):    return "'5'"
    if s in ("http", "1"):    return "'1'"
    if s in ("socks4", "2"):  return "'2'"
    if s in ("socks5", "3"):  return "'3'"
    return "'4'"


def _apply_proxy_list(lines: List[str], ptype: str):
    if not hasattr(sm, "proxylist"):
        sm.proxylist = []
    sm.proxylist.clear()
    if ptype == "'4'":
        return
    for ln in lines or []:
        ln = (ln or "").strip().split()[0]
        if ln and ":" in ln:
            sm.proxylist.append(ln)


def _clear_results_for_current(user_id: int):
    try:
        prefix_name = RUN_CURRENT_NAME.get(int(user_id), "")
        if prefix_name:
            prefix = f"results/{prefix_name}/".lower()
            for k in [k for k in list(RESULT_STORE.keys()) if k.startswith(prefix)]:
                try: del RESULT_STORE[k]
                except: pass
        RUN_CURRENT_NAME.pop(int(user_id), None)
    except Exception:
        pass


def _suppress_writes():
    import builtins
    real_open     = builtins.open
    real_makedirs = os.makedirs

    class _NoCloseStringIO(io.StringIO):
        def close(self):
            try: self.seek(0, io.SEEK_END)
            except: pass

    def safe_open(file, mode="r", *args, **kwargs):
        try: p = str(file)
        except: p = ""
        norm = p.replace("\\", "/").lower()
        if "results/" in norm or norm.endswith("/results") or norm.endswith("results"):
            if any(m in mode for m in ("w", "a", "+")):
                key = norm
                buf = RESULT_STORE.get(key)
                if buf is None:
                    buf = _NoCloseStringIO()
                    RESULT_STORE[key] = buf
                try: buf.seek(0, io.SEEK_END)
                except: pass
                return buf
        return real_open(file, mode, *args, **kwargs)

    def safe_makedirs(name, mode=0o777, exist_ok=False):
        try: p = str(name)
        except: p = ""
        norm = p.replace("\\", "/").lower()
        if "results/" in norm or norm.endswith("/results") or norm.endswith("results"):
            return
        return real_makedirs(name, mode=mode, exist_ok=exist_ok)

    builtins.open = safe_open
    os.makedirs   = safe_makedirs


async def _post_run_cleanup(ns=None, user_id: Optional[int] = None):
    try:
        global STOPPING, FIRST_WORKER_ERROR
        if user_id is not None:
            USER_STOPPING.pop(int(user_id), None)
            USER_FIRST_WORKER_ERROR.pop(int(user_id), None)
        else:
            STOPPING = False
            FIRST_WORKER_ERROR = None
        # Only clean up the per-run namespace, never touch the global sm
        target = ns if ns is not None else sm
        if hasattr(target, "_OriginalChecker"):
            try: target.Checker = target._OriginalChecker
            except: pass
            try: delattr(target, "_OriginalChecker")
            except: pass
        for k in ("checked", "hits", "bad", "sfa", "mfa", "twofa", "other"):
            try: setattr(target, k, 0)
            except: pass
        try: target.Combos = []
        except: pass
        try:
            if hasattr(target, "proxylist"):
                target.proxylist.clear()
        except: pass
    except Exception:
        pass


async def run_check(combos: List[str], threads: int, proxy_type: str,
                    proxy_lines: Optional[List[str]] = None,
                    fname_hint: str = "discord", user_id: Optional[int] = None,
                    ns=None):
    """Run a check using an isolated per-user namespace (ns).
    Never modifies the global sm so concurrent runs don't interfere."""
    global STOPPING, CURRENT_RUN_NAME
    uid = int(user_id) if user_id is not None else None

    # Use provided isolated namespace; fall back to global sm only if none given
    target = ns if ns is not None else sm

    _suppress_writes()
    try:
        if hasattr(target, "loadconfig") and callable(target.loadconfig):
            target.loadconfig()
    except Exception:
        pass
    if not hasattr(target, "config") or not isinstance(getattr(target, "config"), dict):
        target.config = {}

    def _cset(k, v):
        try: target.config[k] = v
        except:
            try: target.config.set(k, v)
            except: pass

    for k in ("hypixelname", "hypixellevel", "hypixelfirstlogin", "hypixellastlogin",
               "optifinecape", "mcapes", "access", "hypixelsbcoins", "hypixelbwstars",
               "hypixelban", "namechange", "lastchanged", "donutcheck", "payment",
               "cookies", "embed"):
        _cset(k, True)
    _cset("proxylessban", False)

    for _k in ("checked", "hits", "bad", "sfa", "mfa", "twofa", "other", "errors"):
        try: setattr(target, _k, 0)
        except: pass

    if not hasattr(target, "thread"):
        target.thread = 50
    target.thread    = max(1, min(500, int(threads)))
    target.proxytype = proxy_type
    target.screen    = "'2'"
    target.fname     = fname_hint

    run_key = f"{uid}_{fname_hint}" if uid is not None else fname_hint
    CURRENT_RUN_NAME = run_key
    if uid is not None:
        RUN_CURRENT_NAME[uid] = run_key

    target.Combos          = combos
    target.wrapper_checked = 0

    try:
        _ensure_engine_symbols()
    except Exception:
        pass

    if not callable(getattr(target, "Checker", None)):
        raise RuntimeError(
            "Checker function not found. Engine loaded: {}. "
            "Upload silentmain.py to one of: {}. Last error: {}".format(
                _loaded, ", ".join(_SOURCE_PATHS), repr(_last_engine_error))
        )

    # Per-user stop flag
    if uid is not None:
        USER_STOPPING[uid] = False
    else:
        STOPPING = False

    if proxy_type == "'5'":
        if hasattr(target, "get_proxies"):
            await asyncio.to_thread(target.get_proxies)
    elif proxy_type != "'4'":
        _apply_proxy_list_ns(proxy_lines or [], proxy_type, target)

    target.start_time = _time.time()
    if uid is not None:
        USER_FIRST_WORKER_ERROR[uid] = None
    else:
        global FIRST_WORKER_ERROR
        FIRST_WORKER_ERROR = None

    if hasattr(target, "Checker") and not hasattr(target, "_OriginalChecker"):
        target._OriginalChecker = target.Checker
        _rt_install_lock    = threading.Lock()
        _rt_installed: set  = set()
        _first_err_lock     = threading.Lock()
        _wrapper_count_lock = threading.Lock()

        def _WrappedChecker(c):
            # Check per-user stop flag
            stopping_now = USER_STOPPING.get(uid, False) if uid is not None else STOPPING
            if stopping_now:
                return None
            try:
                if not isinstance(c, str):
                    c = str(c)
                res = target._OriginalChecker(c)
                return res
            except Exception as e:
                try: target.errors = getattr(target, "errors", 0) + 1
                except: pass
                try:
                    if uid is not None:
                        if USER_FIRST_WORKER_ERROR.get(uid) is None:
                            with _first_err_lock:
                                if USER_FIRST_WORKER_ERROR.get(uid) is None:
                                    USER_FIRST_WORKER_ERROR[uid] = f"{type(e).__name__}: {e}"
                    else:
                        global FIRST_WORKER_ERROR
                        if FIRST_WORKER_ERROR is None:
                            with _first_err_lock:
                                if FIRST_WORKER_ERROR is None:
                                    FIRST_WORKER_ERROR = f"{type(e).__name__}: {e}"
                except: pass
                retried = False
                if isinstance(e, ModuleNotFoundError):
                    mod = getattr(e, "name", None)
                    if mod:
                        with _rt_install_lock:
                            if mod not in _rt_installed:
                                _rt_installed.add(mod)
                                _pip_install_for(mod)
                                retried = True
                if retried:
                    try: return target._OriginalChecker(c)
                    except: return None
                return None
            finally:
                try:
                    with _wrapper_count_lock:
                        target.wrapper_checked = getattr(target, "wrapper_checked", 0) + 1
                except: pass

        target.Checker = _WrappedChecker

    def _worker():
        with cf.ThreadPoolExecutor(max_workers=target.thread) as ex:
            futs = []
            for c in target.Combos:
                stopping_now = USER_STOPPING.get(uid, False) if uid is not None else STOPPING
                if stopping_now:
                    break
                futs.append(ex.submit(target.Checker, c))
            if futs:
                cf.wait(futs)

    await asyncio.to_thread(_worker)


def _apply_proxy_list_ns(lines: List[str], ptype: str, target):
    """Like _apply_proxy_list but operates on an arbitrary namespace."""
    if not hasattr(target, "proxylist"):
        target.proxylist = []
    target.proxylist.clear()
    if ptype == "'4'":
        return
    for ln in lines or []:
        ln = (ln or "").strip().split()[0]
        if ln and ":" in ln:
            target.proxylist.append(ln)

# ─── Progress embed ───────────────────────────────────────────
def _build_status_embed(total: int, checked: int, hits: int, bad: int,
                        threads: int, start_ts: float, guild=None) -> discord.Embed:
    E = GuildEmojis(guild)

    percent = min(100.0, (checked / max(1, total)) * 100.0)
    bar_len  = 22
    filled   = int(bar_len * percent / 100.0)
    bar      = "█" * filled + "░" * (bar_len - filled)

    elapsed = int(asyncio.get_running_loop().time() - start_ts)
    def fmt(t):
        h, r = divmod(t, 3600)
        m, s = divmod(r, 60)
        return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

    twofa  = getattr(sm, "twofa",  0)
    errors = getattr(sm, "errors", 0)
    sfa    = getattr(sm, "sfa",    0)
    mfa    = getattr(sm, "mfa",    0)

    valid_emails = getattr(sm, "validemails", None)
    if valid_emails is None:
        valid_emails = hits

    def _gi(name):
        try: return int(getattr(sm, name, 0) or 0)
        except: return 0

    total_hits = _gi("hits") or _get_display_hits()
    xbox_hits  = _gi("xgp") + _gi("xgpu") + _gi("bedrock")
    mc_hits    = max(0, total_hits - xbox_hits)

    e = discord.Embed(
        title=f"{LOADING_EMOJI}  NightCloud Checker — Live Progress",
        description=f"{SEPARATOR}",
        color=C_DARK,
    )

    e.add_field(
        name=f"{E.UPLOAD}  Progress",
        value=(
            f"`{percent:>5.1f}%`  (**{checked}** / **{total}**)\n"
            f"`{bar}`\n"
            f"{E.ARROW} Remaining: **{max(0, total - checked)}** "
            f"• Threads: **{threads}** "
            f"• Elapsed: **{fmt(elapsed)}**"
        ),
        inline=False,
    )

    e.add_field(name=f"{UNLOCK_EMOJI}  Hits",           value=f"```{hits}```",          inline=True)
    e.add_field(name=f"{E.GREEN}  Valid Emails",         value=f"```{valid_emails}```",   inline=True)
    e.add_field(name=f"{E.DIAMOND}  2FA",                value=f"```{twofa}```",          inline=True)
    e.add_field(name=f"{E.BAN}  Invalid",                value=f"```{bad}```",            inline=True)
    e.add_field(name=f"{ALERT_EMOJI}  Errors",           value=f"```{errors}```",         inline=True)
    e.add_field(name=f"{E.COPPER}  SFA / MFA",           value=f"```{sfa} / {mfa}```",   inline=True)

    e.add_field(
        name=f"{E.DIAMOND_VAULT}  Hit Breakdown",
        value=(
            f"{E.BOOSTER} Xbox: `{xbox_hits}`\n"
            f"{E.DONUT} Minecraft: `{mc_hits}`"
        ),
        inline=True,
    )
    e.add_field(
        name=f"{E.STOCK_YELLOW}  Validation Log",
        value=(
            f"Xbox Validated: `{xbox_hits}`\n"
            f"MC Validated: `{mc_hits}`"
        ),
        inline=True,
    )

    _footer(e, guild)
    return e

# ─── Result sender ────────────────────────────────────────────
async def _send_results(ctx: commands.Context):
    try:
        run_name = RUN_CURRENT_NAME.get(int(ctx.author.id), CURRENT_RUN_NAME)
        prefix   = f"results/{run_name}/".lower() if run_name else ""
        chosen   = [(k, v) for k, v in RESULT_STORE.items() if k.startswith(prefix)]

        if not chosen and run_name and "_" in run_name:
            suffix    = run_name.split("_", 1)[1]
            alt_pfx   = f"results/{suffix}/".lower()
            chosen    = [(k, v) for k, v in RESULT_STORE.items() if k.startswith(alt_pfx)]

        if not chosen:
            chosen = [(k, v) for k, v in RESULT_STORE.items() if k.startswith("results/")]

        if not chosen:
            return

        mem = io.BytesIO()
        with zipfile.ZipFile(mem, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for k, buf in chosen:
                name = k.split(prefix, 1)[-1]
                try:    data = buf.getvalue().encode("utf-8", errors="ignore")
                except: data = str(buf.getvalue()).encode("utf-8", errors="ignore")
                z.writestr(name or "file.txt", data)
        mem.seek(0)

        E = GuildEmojis(ctx.guild)
        e = ok_embed(
            f"{E.BOX} Results ZIP for run `{CURRENT_RUN_NAME}` attached below.",
            title="Run Complete",
            guild=ctx.guild,
        )
        await ctx.send(embed=e, file=discord.File(mem, filename=f"{CURRENT_RUN_NAME}_results.zip"))

        wanted = ["Hits.txt", "DonutUnbanned.txt", "XboxHits.txt",
                  "XboxGamePassUltimate.txt", "XboxGamePass.txt",
                  "2fa.txt", "SFA.txt", "MFA.txt", "Banned.txt", "Unbanned.txt"]
        for w in wanted:
            for k, buf in chosen:
                if k.endswith(w.lower()):
                    try:
                        data = io.BytesIO(buf.getvalue().encode("utf-8", errors="ignore"))
                        await ctx.send(file=discord.File(data, filename=w))
                    except Exception:
                        pass
                    break
    except Exception:
        pass

# ─── Bot events ───────────────────────────────────────────────
STATUS_MSGS = [
    ("g help | NightCloud Checker",       discord.ActivityType.listening),
    ("NightCloud | {n} servers",          discord.ActivityType.watching),
    ("NightCloud Account Checker",        discord.ActivityType.playing),
    ("Checking combos...",          discord.ActivityType.watching),
    ("g help | NightCloud Checker",       discord.ActivityType.listening),
    ("{n} servers protected",       discord.ActivityType.watching),
    ("XP Checker | NightCloud",           discord.ActivityType.playing),
]
_status_idx = 0


@tasks.loop(seconds=15)
async def rotate_status():
    global _status_idx
    name, atype = STATUS_MSGS[_status_idx % len(STATUS_MSGS)]
    name = name.replace("{n}", str(len(bot.guilds)))
    await bot.change_presence(activity=discord.Activity(type=atype, name=name), status=discord.Status.online)
    _status_idx += 1


@bot.event
async def on_ready():
    print(f"[NightCloud] Ready — {bot.user} ({bot.user.id}) | {len(bot.guilds)} guilds")
    _load_access_list()
    _load_prefixes()
    _load_tiers()
    rotate_status.start()
    try:
        synced = await bot.tree.sync()
        print(f"[NightCloud] Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"[NightCloud] Slash sync error: {e}")

# ─── Guild check: server channels only ───────────────────────
async def _guild_only(ctx: commands.Context) -> bool:
    if not ctx.guild:
        await ctx.author.send(
            embed=error_embed("This command only works in server channels, not in DMs.")
        )
        return False
    return True

# ─── /installemoji ────────────────────────────────────────────
def _fetch_emoji_bytes(url: str) -> bytes:
    req = _urllib_req.Request(url, headers={"User-Agent": "NightCloudBot/1.0"})
    with _urllib_req.urlopen(req, timeout=10) as resp:
        return resp.read()


@bot.tree.command(name="installemoji", description="Install NightCloud custom emojis into this server")
@app_commands.default_permissions(manage_emojis=True)
async def installemoji(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    if not guild:
        await interaction.followup.send("This command must be used in a server.", ephemeral=True)
        return

    E = GuildEmojis(guild)
    installed, skipped, failed = [], [], []
    existing_names = {e.name for e in guild.emojis}

    for name, emoji_id, animated in EMOJI_MANIFEST:
        if name in existing_names:
            skipped.append(name)
            continue
        ext = "gif" if animated else "png"
        url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}"
        try:
            img = await asyncio.to_thread(_fetch_emoji_bytes, url)
            cr  = await guild.create_custom_emoji(name=name, image=img, reason="NightCloud /installemoji")
            installed.append(f"{cr} `:{cr.name}:`")
        except discord.Forbidden:
            failed.append(f"`{name}` — missing **Manage Emojis** permission")
        except discord.HTTPException as ex:
            failed.append(f"`{name}` — {ex.text or ex}")
        except Exception as ex:
            failed.append(f"`{name}` — {ex}")

    lines = []
    if installed: lines.append(f"{E.greendot} **Installed ({len(installed)}):**\n" + "  ".join(installed))
    if skipped:   lines.append(f"{E.arrow} **Already exist ({len(skipped)}):** " + ", ".join(f"`{s}`" for s in skipped))
    if failed:    lines.append(f"{E.ban} **Failed ({len(failed)}):**\n" + "\n".join(failed)[:800])
    if not lines: lines.append("Nothing to do — all emojis are already installed.")

    e = discord.Embed(
        title=f"{E.sparkle}  NightCloud — Emoji Installation",
        description=SEPARATOR + "\n" + "\n\n".join(lines),
        color=C_OK if not failed else C_WARN,
    )
    _footer(e, guild)
    await interaction.followup.send(embed=e, ephemeral=True)

# ─── /help slash ─────────────────────────────────────────────
@bot.tree.command(name="help", description="Show NightCloud Checker commands")
async def slash_help(interaction: discord.Interaction):
    guild = interaction.guild
    E = GuildEmojis(guild)
    p = _GUILD_PREFIXES.get(guild.id, DEFAULT_PREFIX) if guild else DEFAULT_PREFIX
    e = discord.Embed(
        title=f"{E.sparkle}  NightCloud Checker — Help",
        description=f"```\nPublic Account Checker Bot\n```\n{SEPARATOR}",
        color=C_INFO,
    )
    cmds = [
        (f"{p}run",                   "Start an interactive check (attach combo in channel)"),
        (f"{p}check",                 "One-shot check — attach combo file directly"),
        (f"{p}stop",                  "Stop your checking session"),
        (f"{p}files",                 "Download results ZIP for the last run"),
        (f"{p}show <name>",           "Send a single result file (Hits, 2fa, SFA …)"),
        (f"{p}stats",                 "View live stats for the active run"),
        (f"{p}engine",                "Upload engine file (attach silentmain.py) — owner only"),
        (f"{p}status",                "Show engine status, tier, and active sessions"),
        (f"{p}prefix <new>",          "Change this server's command prefix — server owner only"),
        (f"{p}access @user <dur>",    "Grant access — owner only (1d, 12h, perm …)"),
        (f"{p}revoke @user",          "Revoke access — owner only"),
        (f"{p}premium <guildid>",     "Grant Premium (6 slots) to a server — bot owner only"),
        (f"{p}booster <guildid>",     "Grant Booster (unlimited) to a server — bot owner only"),
        (f"{p}removetier <guildid>",  "Remove tier from a server — bot owner only"),
    ]
    for cmd, desc in cmds:
        e.add_field(name=f"{E.arrow} `{cmd}`", value=desc, inline=False)
    e.add_field(name=f"{E.diamond} Slash", value="`/installemoji` — Install NightCloud emojis\n`/help` — This menu", inline=False)
    _footer(e, guild)
    await interaction.response.send_message(embed=e, ephemeral=True)

# ─── Commands ─────────────────────────────────────────────────
@bot.command(name="help")
async def help_cmd(ctx: commands.Context):
    if not await _guild_only(ctx):
        return
    guild = ctx.guild
    E = GuildEmojis(guild)
    p = ctx.prefix
    e = discord.Embed(
        title=f"{E.sparkle}  NightCloud Checker — Help",
        description=f"```\nPublic Account Checker Bot\n```\n{SEPARATOR}",
        color=C_INFO,
    )
    cmds = [
        (f"{p}run",                   "Start an interactive check session in this channel"),
        (f"{p}check",                 "Attach combo file and check in one step"),
        (f"{p}stop",                  "Stop your checking session"),
        (f"{p}files",                 "Download results ZIP for the last run"),
        (f"{p}show <name>",           "Send a single result file (Hits / 2fa / SFA / MFA)"),
        (f"{p}stats",                 "Live stats for the running check"),
        (f"{p}engine",                "Upload engine file (attach silentmain.py) — owner only"),
        (f"{p}status",                "Show engine status, tier, and active sessions"),
        (f"{p}prefix <new>",          "Change this server's command prefix — server owner only"),
        (f"{p}access @user <dur>",    "Grant access — server owner only (1d / 12h / perm)"),
        (f"{p}revoke @user",          "Revoke access — server owner only"),
        (f"{p}premium <guildid>",     "Grant Premium (6 slots) to a server — bot owner only"),
        (f"{p}booster <guildid>",     "Grant Booster (unlimited) to a server — bot owner only"),
        (f"{p}removetier <guildid>",  "Remove tier from a server — bot owner only"),
    ]
    for cmd, desc in cmds:
        e.add_field(name=f"{E.arrow} `{cmd}`", value=desc, inline=False)
    _footer(e, guild)
    await ctx.send(embed=e)


@bot.command(name="run")
async def run_cmd(ctx: commands.Context):
    if not await _guild_only(ctx):
        return
    guild = ctx.guild
    E = GuildEmojis(guild)

    if not _has_access(guild, ctx.author.id):
        return await ctx.send(embed=error_embed("You are not authorised to run checks.", guild=guild))

    if _guild_user_running(guild.id, ctx.author.id):
        return await ctx.send(embed=warn_embed("You already have a check running. Use `g stop` to stop it first.", guild=guild))

    if not _guild_can_run(guild.id):
        tier = GUILD_TIERS.get(guild.id, "")
        limit = _guild_slot_limit(guild.id)
        if tier == "premium":
            upsell = (
                f"This server has reached its **Premium limit ({PREMIUM_SLOTS} sessions)**.\n"
                f"Boost the server to get **unlimited** sessions! 🚀"
            )
        else:
            upsell = (
                f"This server has reached its **free limit ({NORMAL_SLOTS} active sessions)**.\n\n"
                f"**Want more?**\n"
                f"• DM the owner for **Premium** — `6 slots` for `1M OwO` 💎\n"
                f"• **Boost** the server for **Unlimited** sessions 🚀"
            )
        return await ctx.send(embed=warn_embed(upsell, title="Session Limit Reached", guild=guild))

    if not ENGINE_AVAILABLE or not callable(getattr(sm, "Checker", None)):
        return await ctx.send(embed=error_embed(
            f"Engine not loaded on this machine.\n"
            f"Upload `silentmain.py` to one of:\n```\n" + "\n".join(_SOURCE_PATHS) + "```",
            guild=guild,
        ))

    def _same_channel(m):
        return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

    # Threads
    await ctx.send(embed=info_embed("How many threads? **(1 – 500)** — reply within 30s.", guild=guild))
    try:
        m1      = await bot.wait_for("message", timeout=30.0, check=_same_channel)
        threads = max(1, min(500, int(m1.content.strip())))
    except Exception:
        return await ctx.send(embed=error_embed("Timed out or invalid thread count. Cancelled.", guild=guild))

    # Proxy type
    await ctx.send(embed=info_embed(
        f"{E.arrow} Proxy type?\n`none` | `http` | `socks4` | `socks5` | `auto` — reply within 30s.",
        guild=guild,
    ))
    try:
        m2         = await bot.wait_for("message", timeout=30.0, check=_same_channel)
        proxy_type = _map_proxy(m2.content.strip())
    except Exception:
        return await ctx.send(embed=error_embed("Timed out. Cancelled.", guild=guild))

    # Combo file
    await ctx.send(embed=info_embed(
        f"{E.upload} Attach your **combo file** (email:pass per line) — 60s.",
        guild=guild,
    ))
    try:
        m3 = await bot.wait_for("message", timeout=60.0, check=_same_channel)
        if not m3.attachments:
            return await ctx.send(embed=error_embed("No attachment found. Cancelled.", guild=guild))
        combo_att = m3.attachments[0]
        combos    = _normalize_bytes(await combo_att.read())
        if not combos:
            return await ctx.send(embed=error_embed("No valid combos found in file.", guild=guild))
    except Exception:
        return await ctx.send(embed=error_embed("Failed to read combo file. Cancelled.", guild=guild))

    # Proxy file (if needed)
    proxy_lines: Optional[List[str]] = None
    if proxy_type in ("'1'", "'2'", "'3'"):
        await ctx.send(embed=info_embed(
            f"{E.arrow} Attach **proxy file** (ip:port per line) or type `skip` — 60s.",
            guild=guild,
        ))
        try:
            m4 = await bot.wait_for("message", timeout=60.0, check=_same_channel)
            if m4.attachments:
                ptxt        = await m4.attachments[0].read()
                proxy_lines = [ln.strip() for ln in ptxt.decode("utf-8", errors="ignore").splitlines() if ln.strip()]
            elif m4.content.strip().lower() == "skip":
                proxy_lines = []
            else:
                return await ctx.send(embed=error_embed("No proxies provided. Cancelled.", guild=guild))
        except Exception:
            return await ctx.send(embed=error_embed("Failed to read proxy file. Cancelled.", guild=guild))

    fname_hint   = os.path.splitext(combo_att.filename)[0]
    start_ts     = asyncio.get_running_loop().time()
    total_combos = len(combos)

    _guild_add_run(guild.id, ctx.author.id)
    engine = make_engine_namespace()
    RUNS[int(ctx.author.id)] = {
        "engine": engine, "start_ts": start_ts, "total": total_combos,
        "threads": threads, "proxy_type": proxy_type, "fname_hint": fname_hint,
    }

    start_e = discord.Embed(
        title=f"{E.sparkle}  NightCloud Checker — Starting",
        description=f"{SEPARATOR}",
        color=C_INFO,
    )
    _proxy_display = proxy_type.strip("'")
    start_e.add_field(name=f"{E.upload} Combos",   value=f"`{total_combos:,}`",    inline=True)
    start_e.add_field(name=f"{E.booster} Threads", value=f"`{threads}`",           inline=True)
    start_e.add_field(name=f"{E.arrow} Proxy",     value=f"`{_proxy_display}`",   inline=True)
    start_e.add_field(name=f"{E.box} File",        value=f"`{combo_att.filename}`", inline=False)
    _footer(start_e, guild)
    await ctx.send(embed=start_e)

    def _get_ns_display_hits(ns) -> int:
        def _gi(name):
            try: return int(getattr(ns, name, 0) or 0)
            except: return 0
        base = _gi("hits")
        if base > 0:
            return base
        return _gi("xgp") + _gi("xgpu") + _gi("bedrock")

    async def _mk_embed():
        checked = getattr(engine, "wrapper_checked", 0)
        hits    = _get_ns_display_hits(engine)
        bad     = getattr(engine, "bad", 0)
        return _build_status_embed(total_combos, checked, hits, bad, threads, start_ts, guild)

    msg = await ctx.send(embed=await _mk_embed())

    async def updater():
        last_snap = None
        while True:
            await asyncio.sleep(4)
            try:
                checked  = getattr(engine, "wrapper_checked", 0)
                hits     = _get_ns_display_hits(engine)
                bad      = getattr(engine, "bad", 0)
                snapshot = (checked, hits, bad)
                if snapshot != last_snap:
                    last_snap = snapshot
                    await msg.edit(embed=_build_status_embed(total_combos, checked, hits, bad, threads, start_ts, guild))
            except Exception:
                pass
            if getattr(engine, "wrapper_checked", 0) >= len(getattr(engine, "Combos", [])):
                break

    task = asyncio.create_task(updater())
    try:
        await run_check(combos, threads, proxy_type, proxy_lines, fname_hint, ctx.author.id, ns=engine)
    except Exception as e:
        await ctx.send(embed=error_embed(f"Run failed: `{e}`", guild=guild))
    finally:
        _guild_remove_run(guild.id, ctx.author.id)
        await asyncio.sleep(1)
        if not task.done():
            task.cancel()
        try: await msg.edit(embed=await _mk_embed())
        except: pass
        first_err = USER_FIRST_WORKER_ERROR.get(int(ctx.author.id))
        if first_err:
            await ctx.send(embed=warn_embed(f"First worker error: `{first_err}`", guild=guild))
        await ctx.send(embed=ok_embed(f"{E.upload} Sending result files...", guild=guild))
        await asyncio.sleep(5)
        await _send_results(ctx)
        await _post_run_cleanup(ns=engine, user_id=ctx.author.id)
        _clear_results_for_current(ctx.author.id)
        RUNS.pop(int(ctx.author.id), None)
        await ctx.send(embed=ok_embed(f"{E.greendot} Run finished!", guild=guild))


@bot.command(name="check")
async def check_cmd(ctx: commands.Context):
    if not await _guild_only(ctx):
        return
    guild = ctx.guild
    E = GuildEmojis(guild)

    if not _has_access(guild, ctx.author.id):
        return await ctx.send(embed=error_embed("You are not authorised to run checks.", guild=guild))

    if _guild_user_running(guild.id, ctx.author.id):
        return await ctx.send(embed=warn_embed("You already have a check running. Use `g stop` to stop it first.", guild=guild))

    if not _guild_can_run(guild.id):
        tier = GUILD_TIERS.get(guild.id, "")
        if tier == "premium":
            upsell = (
                f"This server has reached its **Premium limit ({PREMIUM_SLOTS} sessions)**.\n"
                f"Boost the server to get **unlimited** sessions! 🚀"
            )
        else:
            upsell = (
                f"This server has reached its **free limit ({NORMAL_SLOTS} active sessions)**.\n\n"
                f"**Want more?**\n"
                f"• DM the owner for **Premium** — `6 slots` for `1M OwO` 💎\n"
                f"• **Boost** the server for **Unlimited** sessions 🚀"
            )
        return await ctx.send(embed=warn_embed(upsell, title="Session Limit Reached", guild=guild))

    if not ENGINE_AVAILABLE:
        return await ctx.send(embed=error_embed("Engine not loaded. Upload `silentmain.py`.", guild=guild))

    def _same_channel(m):
        return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

    await ctx.send(embed=info_embed("How many threads? **(1–500)**", guild=guild))
    try:
        m1      = await bot.wait_for("message", timeout=30.0, check=_same_channel)
        threads = max(1, min(500, int(m1.content.strip())))
    except Exception:
        return await ctx.send(embed=error_embed("Timed out. Cancelled.", guild=guild))

    await ctx.send(embed=info_embed(
        f"{E.arrow} Proxy? `none` | `http` | `socks4` | `socks5` | `auto`",
        guild=guild,
    ))
    try:
        m2         = await bot.wait_for("message", timeout=30.0, check=_same_channel)
        proxy_type = _map_proxy(m2.content.strip())
    except Exception:
        return await ctx.send(embed=error_embed("Timed out. Cancelled.", guild=guild))

    await ctx.send(embed=info_embed(f"{E.upload} Attach your combo file — 60s.", guild=guild))
    try:
        m3 = await bot.wait_for("message", timeout=60.0, check=_same_channel)
        if not m3.attachments:
            return await ctx.send(embed=error_embed("No attachment. Cancelled.", guild=guild))
        combo_att = m3.attachments[0]
        combos    = _normalize_bytes(await combo_att.read())
        if not combos:
            return await ctx.send(embed=error_embed("No combos found in file.", guild=guild))
    except Exception:
        return await ctx.send(embed=error_embed("Failed to read combo. Cancelled.", guild=guild))

    proxy_lines = None
    if proxy_type in ("'1'", "'2'", "'3'"):
        await ctx.send(embed=info_embed(f"{E.arrow} Attach proxy file or type `skip` — 60s.", guild=guild))
        try:
            m4 = await bot.wait_for("message", timeout=60.0, check=_same_channel)
            if m4.attachments:
                ptxt        = await m4.attachments[0].read()
                proxy_lines = [ln.strip() for ln in ptxt.decode("utf-8", errors="ignore").splitlines() if ln.strip()]
            elif m4.content.strip().lower() == "skip":
                proxy_lines = []
            else:
                return await ctx.send(embed=error_embed("No proxies. Cancelled.", guild=guild))
        except Exception:
            return await ctx.send(embed=error_embed("Failed to read proxies. Cancelled.", guild=guild))

    fname_hint   = os.path.splitext(combo_att.filename)[0]
    start_ts     = asyncio.get_running_loop().time()
    total_combos = len(combos)

    _guild_add_run(guild.id, ctx.author.id)
    engine = make_engine_namespace()
    RUNS[int(ctx.author.id)] = {
        "engine": engine, "start_ts": start_ts, "total": total_combos,
        "threads": threads, "proxy_type": proxy_type, "fname_hint": fname_hint,
    }

    start_e = discord.Embed(
        title=f"{E.sparkle}  NightCloud Checker — Starting",
        description=SEPARATOR,
        color=C_INFO,
    )
    _proxy_display2 = proxy_type.strip("'")
    start_e.add_field(name=f"{E.upload} Combos",   value=f"`{total_combos:,}`",  inline=True)
    start_e.add_field(name=f"{E.booster} Threads", value=f"`{threads}`",         inline=True)
    start_e.add_field(name=f"{E.arrow} Proxy",     value=f"`{_proxy_display2}`", inline=True)
    _footer(start_e, guild)
    await ctx.send(embed=start_e)

    def _get_ns_display_hits_check(ns) -> int:
        def _gi(name):
            try: return int(getattr(ns, name, 0) or 0)
            except: return 0
        base = _gi("hits")
        if base > 0:
            return base
        return _gi("xgp") + _gi("xgpu") + _gi("bedrock")

    async def _mk_embed():
        checked = getattr(engine, "wrapper_checked", 0)
        hits    = _get_ns_display_hits_check(engine)
        bad     = getattr(engine, "bad", 0)
        return _build_status_embed(total_combos, checked, hits, bad, threads, start_ts, guild)

    msg = await ctx.send(embed=await _mk_embed())

    async def updater():
        last_snap = None
        while True:
            await asyncio.sleep(2)
            try:
                checked  = getattr(engine, "wrapper_checked", 0)
                hits     = _get_ns_display_hits_check(engine)
                bad      = getattr(engine, "bad", 0)
                snapshot = (checked, hits, bad)
                if snapshot != last_snap:
                    last_snap = snapshot
                    await msg.edit(embed=await _mk_embed())
            except: pass
            if getattr(engine, "wrapper_checked", 0) >= total_combos:
                break

    task = asyncio.create_task(updater())
    try:
        await run_check(combos, threads, proxy_type, proxy_lines, fname_hint, ctx.author.id, ns=engine)
    except Exception as e:
        await ctx.send(embed=error_embed(f"Run failed: `{e}`", guild=guild))
    finally:
        _guild_remove_run(guild.id, ctx.author.id)
        await asyncio.sleep(1)
        if not task.done():
            task.cancel()
        try: await msg.edit(embed=await _mk_embed())
        except: pass
        first_err = USER_FIRST_WORKER_ERROR.get(int(ctx.author.id))
        if first_err:
            await ctx.send(embed=warn_embed(f"First worker error: `{first_err}`", guild=guild))
        await ctx.send(embed=ok_embed("Sending results...", guild=guild))
        await asyncio.sleep(5)
        await _send_results(ctx)
        await _post_run_cleanup(ns=engine, user_id=ctx.author.id)
        _clear_results_for_current(ctx.author.id)
        RUNS.pop(int(ctx.author.id), None)
        await ctx.send(embed=ok_embed(f"{E.greendot} Check finished!", guild=guild))


@bot.command(name="stop")
async def stop_cmd(ctx: commands.Context):
    if not await _guild_only(ctx):
        return
    guild = ctx.guild
    E = GuildEmojis(guild)

    if not _has_access(guild, ctx.author.id):
        return await ctx.send(embed=error_embed("You are not authorised to stop runs.", guild=guild))

    if not _guild_user_running(guild.id, ctx.author.id) and not _is_owner(guild, ctx.author.id):
        return await ctx.send(embed=warn_embed("You don't have an active session in this server.", guild=guild))

    # Only stop THIS user's run — not all concurrent runs
    uid = int(ctx.author.id)
    USER_STOPPING[uid] = True
    _guild_remove_run(guild.id, ctx.author.id)
    await ctx.send(embed=warn_embed(f"{E.arrow} Stopping your session... sending available results.", guild=guild))
    await _send_results(ctx)


@bot.command(name="files")
async def files_cmd(ctx: commands.Context):
    if not await _guild_only(ctx):
        return
    guild = ctx.guild
    E = GuildEmojis(guild)

    run_name = RUN_CURRENT_NAME.get(int(ctx.author.id), CURRENT_RUN_NAME)
    prefix   = f"results/{run_name}/".lower() if run_name else ""
    chosen   = [(k, v) for k, v in RESULT_STORE.items() if k.startswith(prefix)]

    if not chosen:
        return await ctx.send(embed=error_embed("No result files captured for the last run.", guild=guild))

    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for k, buf in chosen:
            name = k.split(prefix, 1)[-1]
            try:    data = buf.getvalue().encode("utf-8", errors="ignore")
            except: data = str(buf.getvalue()).encode("utf-8", errors="ignore")
            z.writestr(name or "file.txt", data)
    mem.seek(0)

    e = ok_embed(f"{E.box} Results ZIP ready.", guild=guild)
    await ctx.send(embed=e, file=discord.File(mem, filename=f"{run_name or 'results'}_results.zip"))


@bot.command(name="show")
async def show_cmd(ctx: commands.Context, name: str = "Hits"):
    if not await _guild_only(ctx):
        return
    guild = ctx.guild

    run_name = RUN_CURRENT_NAME.get(int(ctx.author.id), CURRENT_RUN_NAME)
    prefix   = f"results/{run_name}/".lower() if run_name else ""
    wanted   = name.strip().lower().replace(".txt", "") + ".txt"
    for k, buf in RESULT_STORE.items():
        if k.startswith(prefix) and k.endswith(wanted):
            data = io.BytesIO(buf.getvalue().encode("utf-8", errors="ignore"))
            return await ctx.send(file=discord.File(data, filename=wanted))
    await ctx.send(embed=error_embed(f"File `{wanted}` not found for this run.", guild=guild))


@bot.command(name="stats")
async def stats_cmd(ctx: commands.Context):
    if not await _guild_only(ctx):
        return
    guild = ctx.guild
    E = GuildEmojis(guild)

    # Use per-user run namespace if available, else fall back to global sm
    run_info = RUNS.get(int(ctx.author.id))
    ns = run_info["engine"] if run_info and "engine" in run_info else sm

    def _nsgi(name):
        try: return int(getattr(ns, name, 0) or 0)
        except: return 0

    total           = len(getattr(ns, "Combos", []))
    wrapper_checked = _nsgi("wrapper_checked")
    hits_base       = _nsgi("hits")
    hits            = hits_base if hits_base > 0 else (_nsgi("xgp") + _nsgi("xgpu") + _nsgi("bedrock"))
    bad             = _nsgi("bad")
    sfa             = _nsgi("sfa")
    mfa             = _nsgi("mfa")
    twofa           = _nsgi("twofa")
    errors          = _nsgi("errors")

    e = discord.Embed(
        title=f"{E.stock_yellow}  NightCloud — Live Stats",
        description=SEPARATOR,
        color=C_GOLD,
    )
    e.add_field(name=f"{E.booster} Total Combos",   value=f"`{total:,}`",           inline=True)
    e.add_field(name=f"{E.upload} Processed",       value=f"`{wrapper_checked:,}`", inline=True)
    e.add_field(name=f"{E.greendot} Hits",          value=f"`{hits}`",              inline=True)
    e.add_field(name=f"{E.ban} Bad",                value=f"`{bad}`",               inline=True)
    e.add_field(name=f"{E.copper} SFA",             value=f"`{sfa}`",               inline=True)
    e.add_field(name=f"{E.diamond} MFA",            value=f"`{mfa}`",               inline=True)
    e.add_field(name=f"{E.diamond_vault} 2FA",      value=f"`{twofa}`",             inline=True)
    e.add_field(name=f"{E.reason} Errors",          value=f"`{errors}`",            inline=True)
    _footer(e, guild)
    await ctx.send(embed=e)


@bot.command(name="access")
async def access_cmd(ctx: commands.Context, member: discord.Member, duration: str = "1d"):
    if not await _guild_only(ctx):
        return
    guild = ctx.guild
    E = GuildEmojis(guild)

    if not _is_owner(guild, ctx.author.id):
        return await ctx.send(embed=error_embed(
            "Only the **server owner** or global bot owner can grant access.", guild=guild
        ))

    secs = _parse_duration(duration)
    if secs == 0:
        return await ctx.send(embed=error_embed("Invalid duration. Examples: `1d`, `12h`, `30m`, `perm`", guild=guild))

    expiry = -1 if secs == -1 else int(_time.time() + secs)
    ACCESS_LIST[int(member.id)] = expiry
    _save_access_list()
    when = "permanent" if expiry == -1 else f"until <t:{expiry}:R>"
    await ctx.send(embed=ok_embed(
        f"{E.greendot} Access granted to {member.mention} — **{when}**.", guild=guild
    ))


@bot.command(name="revoke", aliases=["remove", "rmaccess"])
async def revoke_cmd(ctx: commands.Context, member: discord.Member):
    if not await _guild_only(ctx):
        return
    guild = ctx.guild
    E = GuildEmojis(guild)

    if not _is_owner(guild, ctx.author.id):
        return await ctx.send(embed=error_embed(
            "Only the **server owner** or global bot owner can revoke access.", guild=guild
        ))

    ACCESS_LIST.pop(int(member.id), None)
    _save_access_list()
    await ctx.send(embed=ok_embed(f"{E.ban} Access revoked for {member.mention}.", guild=guild))


# ─── g engine — upload engine file via Discord attachment ─────
# Primary path (Pterodactyl panel). Falls back to local directory if unavailable.
_ENGINE_SAVE_PATH = "/home/container/silentmain.py"
_ENGINE_SAVE_PATH_FALLBACK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "silentmain.py")


def _reload_engine_from_source(code: str, path: str) -> str:
    """Load engine code into the global sm namespace. Returns error string or empty string on success."""
    global _loaded, _ENGINE_SOURCE, _ENGINE_PATH, _last_engine_error, ENGINE_AVAILABLE
    _ensure_stub_modules()
    _attempted = set()
    while True:
        try:
            exec(compile(code, path, "exec"), sm.__dict__)
            _loaded = True
            _ENGINE_SOURCE = code
            _ENGINE_PATH = path
            _ensure_engine_symbols()
            ENGINE_AVAILABLE = hasattr(sm, "Checker") and callable(sm.Checker)
            return ""
        except ModuleNotFoundError as e:
            _last_engine_error = e
            mod = getattr(e, "name", None)
            if mod and mod not in _attempted:
                _attempted.add(mod)
                _pip_install_for(mod)
                continue
            return f"Missing module: `{mod}` — could not auto-install."
        except Exception as e:
            _last_engine_error = e
            return f"`{type(e).__name__}: {e}`"


@bot.command(name="engine")
async def engine_cmd(ctx: commands.Context):
    if not await _guild_only(ctx):
        return
    guild = ctx.guild
    E = GuildEmojis(guild)

    if not _is_owner(guild, ctx.author.id):
        return await ctx.send(embed=error_embed(
            "Only the **server owner** or global bot owner can upload the engine.", guild=guild
        ))

    if not ctx.message.attachments:
        return await ctx.send(embed=error_embed(
            "Attach your `silentmain.py` file to this message and try again.", guild=guild
        ))

    att = ctx.message.attachments[0]
    if not att.filename.endswith(".py"):
        return await ctx.send(embed=error_embed(
            f"Expected a `.py` file but got `{att.filename}`.", guild=guild
        ))

    msg = await ctx.send(embed=info_embed(
        f"{E.upload if hasattr(E, 'upload') else ''} Downloading engine file…", guild=guild
    ))

    try:
        raw = await att.read()
        code = raw.decode("utf-8", errors="ignore")
    except Exception as e:
        return await msg.edit(embed=error_embed(f"Failed to read attachment: `{e}`", guild=guild))

    # Try primary path first, then fall back to local directory
    save_path = _ENGINE_SAVE_PATH
    saved = False
    for _path in (_ENGINE_SAVE_PATH, _ENGINE_SAVE_PATH_FALLBACK):
        try:
            parent = os.path.dirname(_path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(_path, "w", encoding="utf-8") as f:
                f.write(code)
            save_path = _path
            saved = True
            break
        except Exception:
            continue

    if not saved:
        # No disk save — load purely in-memory using a temp label
        save_path = "<memory>"

    await msg.edit(embed=info_embed("Engine saved. Loading… (up to 60s)", guild=guild))

    err = ""
    timed_out = False
    try:
        err = await asyncio.wait_for(
            asyncio.to_thread(_reload_engine_from_source, code, save_path),
            timeout=60.0
        )
    except asyncio.TimeoutError:
        timed_out = True
        # Engine load blocked — check if Checker is available anyway
        _ensure_engine_symbols()

    if timed_out and not ENGINE_AVAILABLE:
        saved_note = f"File saved to `{save_path}`." if saved else "File could not be saved to disk."
        return await msg.edit(embed=error_embed(
            f"Engine took longer than 60 seconds to load and no `Checker` function was found.\n"
            f"The engine may have blocking code at the top level (network calls, loops, `input()`).\n"
            f"{saved_note} The bot will retry on next restart.",
            title="Load Timed Out",
            guild=guild,
        ))

    if timed_out and ENGINE_AVAILABLE:
        return await msg.edit(embed=ok_embed(
            f"Engine took a while but `Checker` is ready! You can now run `g check` or `g run`.",
            title="Engine Ready (slow load)",
            guild=guild,
        ))

    if err:
        return await msg.edit(embed=error_embed(
            f"Engine file saved but failed to load:\n{err}", title="Load Failed", guild=guild
        ))

    if ENGINE_AVAILABLE:
        saved_loc = f"`{save_path}`" if saved else "memory only"
        await msg.edit(embed=ok_embed(
            f"Engine loaded successfully from `{att.filename}`!\n"
            f"Saved to: {saved_loc}\n"
            f"`Checker` function is ready. You can now run `g check` or `g run`.",
            title="Engine Ready",
            guild=guild,
        ))
    else:
        await msg.edit(embed=warn_embed(
            f"File saved and executed, but no `Checker` function was found in `{att.filename}`.\n"
            f"Make sure the engine defines a `Checker(combo)` function.",
            title="Engine Loaded (No Checker)",
            guild=guild,
        ))


@bot.command(name="status")
async def status_cmd(ctx: commands.Context):
    if not await _guild_only(ctx):
        return
    guild = ctx.guild
    E = GuildEmojis(guild)

    tier      = GUILD_TIERS.get(guild.id, "free")
    active    = _guild_active_count(guild.id)
    limit     = _guild_slot_limit(guild.id)
    limit_str = "Unlimited" if limit >= 999999 else str(limit)
    pfx       = _GUILD_PREFIXES.get(guild.id, DEFAULT_PREFIX)

    e = discord.Embed(
        title=f"{E.sparkle}  NightCloud — Engine Status",
        description=SEPARATOR,
        color=C_OK if ENGINE_AVAILABLE else C_ERR,
    )
    e.add_field(
        name=f"{E.greendot if ENGINE_AVAILABLE else E.ban}  Engine",
        value="`Loaded`" if ENGINE_AVAILABLE else "`Not Loaded`",
        inline=True,
    )
    e.add_field(
        name=f"{E.arrow}  Path",
        value=f"`{_ENGINE_PATH}`" if _ENGINE_PATH else "`—`",
        inline=True,
    )
    if not ENGINE_AVAILABLE:
        err_str = repr(_last_engine_error)[:300] if _last_engine_error else "No error info"
        e.add_field(
            name=f"{E.reason}  Last Error",
            value=f"```{err_str}```",
            inline=False,
        )
        e.add_field(
            name=f"{E.upload}  How to fix",
            value=f"Run `{pfx}engine` and attach your `silentmain.py` file.",
            inline=False,
        )
    e.add_field(
        name=f"{E.diamond_vault}  Server Tier",
        value=f"`{tier.capitalize()}`",
        inline=True,
    )
    e.add_field(
        name=f"{E.booster}  Active Sessions",
        value=f"`{active} / {limit_str}`",
        inline=True,
    )
    e.add_field(
        name=f"{E.arrow}  Prefix",
        value=f"`{pfx}`",
        inline=True,
    )
    if GUILD_ACTIVE_RUNS.get(guild.id):
        runners = " ".join(f"<@{uid}>" for uid in GUILD_ACTIVE_RUNS[guild.id])
        e.add_field(name=f"{E.greendot}  Running Users", value=runners, inline=False)
    _footer(e, guild)
    await ctx.send(embed=e)


# ─── g premium / g booster ────────────────────────────────────
@bot.command(name="premium")
async def premium_cmd(ctx: commands.Context, guild_id: str = ""):
    guild = ctx.guild
    E = GuildEmojis(guild)

    if not _is_global_owner(ctx.author.id):
        return await ctx.send(embed=error_embed("Only the **global bot owner** can grant Premium.", guild=guild))

    target_id = int(guild_id) if guild_id.strip().isdigit() else (guild.id if guild else None)
    if target_id is None:
        return await ctx.send(embed=error_embed("Please provide a valid server ID.\nUsage: `g premium <guildid>`", guild=guild))

    GUILD_TIERS[target_id] = "premium"
    _save_tiers()

    target_guild = bot.get_guild(target_id)
    name = target_guild.name if target_guild else str(target_id)
    await ctx.send(embed=ok_embed(
        f"{E.diamond} **{name}** (`{target_id}`) has been granted **Premium**!\n"
        f"They now have **{PREMIUM_SLOTS} concurrent checker slots**.",
        title="Premium Granted",
        guild=guild,
    ))


@bot.command(name="booster")
async def booster_cmd(ctx: commands.Context, guild_id: str = ""):
    guild = ctx.guild
    E = GuildEmojis(guild)

    if not _is_global_owner(ctx.author.id):
        return await ctx.send(embed=error_embed("Only the **global bot owner** can grant Booster.", guild=guild))

    target_id = int(guild_id) if guild_id.strip().isdigit() else (guild.id if guild else None)
    if target_id is None:
        return await ctx.send(embed=error_embed("Please provide a valid server ID.\nUsage: `g booster <guildid>`", guild=guild))

    GUILD_TIERS[target_id] = "booster"
    _save_tiers()

    target_guild = bot.get_guild(target_id)
    name = target_guild.name if target_guild else str(target_id)
    await ctx.send(embed=ok_embed(
        f"{E.booster} **{name}** (`{target_id}`) has been granted **Booster** tier!\n"
        f"They now have **Unlimited** concurrent checker slots.",
        title="Booster Granted",
        guild=guild,
    ))


@bot.command(name="removetier")
async def removetier_cmd(ctx: commands.Context, guild_id: str = ""):
    guild = ctx.guild
    E = GuildEmojis(guild)

    if not _is_global_owner(ctx.author.id):
        return await ctx.send(embed=error_embed("Only the **global bot owner** can remove tiers.", guild=guild))

    target_id = int(guild_id) if guild_id.strip().isdigit() else (guild.id if guild else None)
    if target_id is None:
        return await ctx.send(embed=error_embed("Please provide a valid server ID.", guild=guild))

    GUILD_TIERS.pop(target_id, None)
    _save_tiers()

    target_guild = bot.get_guild(target_id)
    name = target_guild.name if target_guild else str(target_id)
    await ctx.send(embed=ok_embed(
        f"{E.ban} **{name}** (`{target_id}`) tier has been removed. Back to **Free** ({NORMAL_SLOTS} slots).",
        title="Tier Removed",
        guild=guild,
    ))


# ─── g prefix ────────────────────────────────────────────────
@bot.command(name="prefix")
async def prefix_cmd(ctx: commands.Context, *, new_prefix: str = ""):
    if not await _guild_only(ctx):
        return
    guild = ctx.guild
    E = GuildEmojis(guild)

    if not _is_owner(guild, ctx.author.id):
        return await ctx.send(embed=error_embed(
            "Only the **server owner** or global bot owner can change the prefix.", guild=guild
        ))

    new_prefix = new_prefix.strip()
    if not new_prefix:
        current = _GUILD_PREFIXES.get(guild.id, DEFAULT_PREFIX)
        return await ctx.send(embed=info_embed(
            f"Current prefix: `{current}`\nUsage: `{current}prefix <new prefix>`",
            guild=guild,
        ))

    if len(new_prefix) > 10:
        return await ctx.send(embed=error_embed("Prefix must be 10 characters or fewer.", guild=guild))

    old_prefix = _GUILD_PREFIXES.get(guild.id, DEFAULT_PREFIX)
    _GUILD_PREFIXES[guild.id] = new_prefix
    _save_prefixes()

    await ctx.send(embed=ok_embed(
        f"Prefix changed from `{old_prefix}` → `{new_prefix}`\n"
        f"All commands now use `{new_prefix}` — e.g. `{new_prefix}help`",
        title="Prefix Updated",
        guild=guild,
    ))


# ─── Entry ───────────────────────────────────────────────────
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(name)s: %(message)s")
    logging.getLogger("discord").setLevel(logging.INFO)
    print("[NightCloud] Starting bot…")
    print(f"[NightCloud] Global owner ID: {OWNER_ID}")
    print(f"[NightCloud] Token present: {'yes' if TOKEN and len(TOKEN) > 20 else 'no'}")
    bot.run(TOKEN)
