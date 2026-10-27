#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║  WEB DATA EXTRACTOR — FULL META EDITION v3.0.0              ║
║  Extract forms → build payloads → generate runnable scripts  ║
║  Python 3.10+ · Tested on Chrome/131 UA · 2026-ready         ║
╚══════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import os
import re
import sys
import json
import time
import textwrap
import subprocess
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse, urlencode, parse_qs

# ══════════════════════════════════════════════════════════════
# 1. DEPENDENCY BOOTSTRAP (robust, version-pinned)
# ══════════════════════════════════════════════════════════════
_PKGS = {
    "requests":       "requests>=2.31.0",
    "bs4":            "beautifulsoup4>=4.12.0",
    "rich":           "rich>=13.7.0",
    "lxml":           "lxml>=5.0.0",          # optional parser, lebih cepat
}


def _missing() -> list[str]:
    out = []
    for mod, spec in _PKGS.items():
        try:
            __import__(mod)
        except ImportError:
            out.append(spec)
    return out


def _bootstrap() -> None:
    miss = _missing()
    if not miss:
        return
    print(f"[!] Dependency kurang: {', '.join(miss)}")
    if input("    Install otomatis? (y/N): ").strip().lower() != "y":
        sys.exit(1)
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", *miss])
    except subprocess.CalledProcessError as e:
        print(f"[x] Instalasi gagal: {e}")
        sys.exit(1)
    print("[✓] Instalasi selesai. Jalankan ulang program.\n")
    sys.exit(0)


_bootstrap()

import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.theme import Theme
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn

# ══════════════════════════════════════════════════════════════
# 2. THEME + CONSOLE
# ══════════════════════════════════════════════════════════════
console = Console(theme=Theme({
    "brand":  "bold cyan",
    "ok":     "bold green",
    "warn":   "bold yellow",
    "bad":    "bold red",
    "key":    "bold magenta",
    "val":    "white",
    "dim":    "dim white",
    "accent": "bold bright_blue",
}))

# ══════════════════════════════════════════════════════════════
# 3. CONSTANTS — UA UPDATE 2026
# ══════════════════════════════════════════════════════════════
APP_NAME    = "Web Data Extractor"
APP_VERSION = "3.0.0"
APP_AUTHOR  = "@bot"

# UA Chrome 131 stabil (Des 2024→2026). Fallback chain untuk anti-WAF.
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.6 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
]

DEFAULT_HEADERS = {
    "Accept":           "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language":  "en-US,en;q=0.9,id;q=0.8",
    "Accept-Encoding":  "gzip, deflate, br",
    "Cache-Control":    "no-cache",
    "Pragma":           "no-cache",
    "Sec-Ch-Ua":        '"Chromium";v="131", "Not_A Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest":   "document",
    "Sec-Fetch-Mode":   "navigate",
    "Sec-Fetch-Site":   "none",
    "Sec-Fetch-User":   "?1",
    "Upgrade-Insecure-Requests": "1",
}

HEADER_BLACKLIST = {
    "cookie", "set-cookie", "report-to", "expires", "date",
    "last-modified", "etag", "content-length", "content-encoding",
    "connection", "keep-alive", "transfer-encoding", "server",
    "x-fb-debug", "cf-ray", "cf-cache-status", "alt-svc",
    "strict-transport-security", "content-security-policy",
}

TIMEOUT   = 30
RETRIES   = 3
BACKOFF   = 1.5

# ══════════════════════════════════════════════════════════════
# 4. DATA MODEL
# ══════════════════════════════════════════════════════════════
@dataclass
class FormField:
    name:     str
    value:    str
    ftype:    str = "text"
    dynamic:  bool = False     # True = perlu di-scrape ulang (csrf, token)


@dataclass
class FormPayload:
    host:     str
    action:   str
    method:   str
    enctype:  str
    fields:   list[FormField] = field(default_factory=list)
    headers:  dict[str, str]  = field(default_factory=dict)
    cookies:  dict[str, str]  = field(default_factory=dict)

    def data_dict(self) -> dict[str, str]:
        return {f.name: f.value for f in self.fields}

    def to_dict(self) -> dict:
        return asdict(self)


# ══════════════════════════════════════════════════════════════
# 5. UTILITIES
# ══════════════════════════════════════════════════════════════
def banner() -> None:
    console.clear()
    console.print(Panel.fit(
        f"[brand]{APP_NAME}[/brand]  [dim]v{APP_VERSION} · META[/dim]\n"
        f"[dim]Form Payload & Request Builder — 2026 Ready[/dim]\n"
        f"[dim]by {APP_AUTHOR}[/dim]",
        border_style="cyan",
        padding=(1, 4),
    ))


def err(msg: str) -> None:
    console.print(Panel(f"[bad]{msg}[/bad]", border_style="red", title="Error"))


def pause() -> None:
    console.input("\n[dim]Tekan ENTER untuk lanjut...[/dim]")


def safe_filename(url: str) -> str:
    host = urlparse(url).netloc or "output"
    host = re.sub(r"[^a-zA-Z0-9._-]+", "_", host)
    ts   = time.strftime("%Y%m%d_%H%M%S")
    return f"payload_{host}_{ts}.py"


# ══════════════════════════════════════════════════════════════
# 6. EXTRACTOR CORE — retry + UA fallback + auto parser
# ══════════════════════════════════════════════════════════════
class WebExtractor:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.session.headers["User-Agent"] = USER_AGENTS[0]

    # ---------- HTTP ----------
    def fetch(self, url: str) -> tuple[requests.Response, BeautifulSoup] | None:
        last_exc: Optional[Exception] = None

        for attempt in range(1, RETRIES + 1):
            # Rotasi UA tiap retry
            self.session.headers["User-Agent"] = USER_AGENTS[(attempt - 1) % len(USER_AGENTS)]

            try:
                resp = self.session.get(url, timeout=TIMEOUT, allow_redirects=True)
                resp.raise_for_status()

                # Pilih parser terbaik yang tersedia
                try:
                    soup = BeautifulSoup(resp.content, "lxml")
                except Exception:
                    soup = BeautifulSoup(resp.content, "html.parser")

                return resp, soup

            except requests.exceptions.SSLError:
                err("SSL handshake gagal — sertifikat situs tidak valid.")
                return None

            except requests.exceptions.ConnectionError as e:
                last_exc = e
                if attempt < RETRIES:
                    console.print(f"[warn]↻ Percobaan {attempt}/{RETRIES} gagal koneksi, retry...[/warn]")
                    time.sleep(BACKOFF * attempt)
                    continue
                err("Koneksi gagal setelah semua retry.")
                return None

            except requests.exceptions.Timeout:
                last_exc = None
                if attempt < RETRIES:
                    console.print(f"[warn]↻ Percobaan {attempt}/{RETRIES} timeout, retry...[/warn]")
                    continue
                err(f"Timeout > {TIMEOUT}s setelah {RETRIES} percobaan.")
                return None

            except requests.exceptions.HTTPError as e:
                code = e.response.status_code
                if code in (403, 429) and attempt < RETRIES:
                    console.print(f"[warn]↻ HTTP {code} (anti-bot?), retry dgn UA baru...[/warn]")
                    time.sleep(BACKOFF * attempt * 2)
                    continue
                err(f"HTTP {code} — {e.response.reason}")
                return None

            except requests.exceptions.RequestException as e:
                err(f"Request gagal: {e}")
                return None

        if last_exc:
            err(f"Gagal total: {last_exc}")
        return None

    # ---------- HEADERS ----------
    @staticmethod
    def _clean_headers(raw) -> dict[str, str]:
        return {k: v for k, v in raw.items()
                if k.lower() not in HEADER_BLACKLIST}

    # ---------- FORM PARSING ----------
    @staticmethod
    def _is_dynamic(name: str, value: str) -> bool:
        """Token/CSRF yang berubah per request."""
        n = name.lower()
        if any(x in n for x in ("csrf", "token", "nonce", "_wpnonce",
                                "authenticity", "requestverification")):
            return True
        # Heuristik: panjang & base64-ish
        if value and len(value) >= 20 and re.fullmatch(r"[A-Za-z0-9_\-+/=]+", value):
            return True
        return False

    def _extract_fields(self, form) -> list[FormField]:
        fields: list[FormField] = []

        # INPUT
        for tag in form.find_all("input"):
            name = tag.get("name")
            if not name:
                continue
            ftype = (tag.get("type") or "text").lower()

            if ftype in ("submit", "button", "reset", "image", "file"):
                continue
            if ftype in ("checkbox", "radio"):
                if tag.has_attr("checked"):
                    fields.append(FormField(name, tag.get("value", "on"), ftype))
                continue

            value = tag.get("value", "")
            fields.append(FormField(name, value, ftype, self._is_dynamic(name, value)))

        # TEXTAREA
        for tag in form.find_all("textarea"):
            name = tag.get("name")
            if name:
                val = tag.text or ""
                fields.append(FormField(name, val, "textarea", self._is_dynamic(name, val)))

        # SELECT
        for tag in form.find_all("select"):
            name = tag.get("name")
            if not name:
                continue
            chosen = tag.find("option", selected=True) or tag.find("option")
            val = chosen.get("value", "") if chosen else ""
            fields.append(FormField(name, val, "select"))

        return fields

    @staticmethod
    def _resolve_action(form, base_url: str) -> str:
        action = (form.get("action") or "").strip()
        if not action:
            return base_url
        return urljoin(base_url, action)

    def build_payload(self, resp, form, base_url: str) -> FormPayload:
        return FormPayload(
            host=urlparse(base_url).netloc,
            action=self._resolve_action(form, base_url),
            method=(form.get("method") or "GET").upper(),
            enctype=(form.get("enctype") or "application/x-www-form-urlencoded").lower(),
            fields=self._extract_fields(form),
            headers=self._clean_headers(dict(resp.headers)),
            cookies=self.session.cookies.get_dict(),
        )


# ══════════════════════════════════════════════════════════════
# 7. GENERATOR — kode Python siap eksekusi (valid 100%)
# ══════════════════════════════════════════════════════════════
class CodeGenerator:
    """Hasilkan script Python yang benar-benar jalan."""

    @staticmethod
    def _dict_literal(name: str, obj: dict[str, str], indent: int = 0) -> str:
        pad = " " * indent
        if not obj:
            return f"{pad}{name} = {{}}"
        lines = [f"{pad}{name} = {{"]
        for k, v in obj.items():
            lines.append(f"{pad}    {k!r}: {v!r},")
        lines.append(f"{pad}}}")
        return "\n".join(lines)

    @staticmethod
    def _dynamic_expr(field: FormField) -> str:
        """Ekspresi regex yang aman, support urutan atribut apapun."""
        n = re.escape(field.name)
        # match name="X" ... value="Y" ATAU value="Y" ... name="X"
        return (
            f"(_m := re.search("
            f"r'name=[\"\\']{n}[\"\\'][^>]*?value=[\"\\']([^\"\\']*)', str(requ)) "
            f"or re.search("
            f"r'value=[\"\\']([^\"\\']*)[\"\\'][^>]*?name=[\"\\']{n}[\"\\']', str(requ)))"
            f".group(1) if _m else ''"
        )

    @classmethod
    def build_script(cls, url: str, payload: FormPayload) -> str:
        script: list[str] = [
            "#!/usr/bin/env python3",
            '"""Auto-generated by Web Data Extractor v3.0.0"""',
            "",
            "import re",
            "import requests",
            "from bs4 import BeautifulSoup",
            "",
            f"URL  = {url!r}",
            f"METHOD = {payload.method!r}",
            f"ACTION = {payload.action!r}",
            "",
            "# ── Session & fetch ──",
            "session = requests.Session()",
            "session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'})",
            "resp = session.get(URL, timeout=30)",
            "resp.raise_for_status()",
            "requ = BeautifulSoup(resp.content, 'html.parser')",
            "",
            "# ── Headers ──",
            cls._dict_literal("headers", payload.headers),
            "",
            "# ── Data ──",
            "data = {",
        ]

        for f in payload.fields:
            if f.dynamic:
                script.append(f"    {f.name!r}: {cls._dynamic_expr(f)},")
            else:
                script.append(f"    {f.name!r}: {f.value!r},")
        script.append("}")
        script.append("")

        script += [
            "# ── Cookies ──",
            "cookies = session.cookies.get_dict()",
            "",
            "# ── Send ──",
            "if METHOD.upper() == 'POST':",
            "    final = session.post(ACTION, headers=headers, data=data, cookies=cookies, timeout=30)",
            "else:",
            "    final = session.get(ACTION, headers=headers, params=data, cookies=cookies, timeout=30)",
            "",
            "print(f'[✓] Status: {final.status_code}')",
            "print(final.text[:300])",
        ]

        return "\n".join(script)


# ══════════════════════════════════════════════════════════════
# 8. RENDERERS
# ══════════════════════════════════════════════════════════════
def render_summary(payload: FormPayload) -> None:
    t = Table(title="[brand]Source Payload[/brand]", border_style="cyan", show_lines=True)
    t.add_column("Field", style="key", no_wrap=True)
    t.add_column("Value", style="val", overflow="fold")

    t.add_row("HOST",    payload.host)
    t.add_row("METHOD",  payload.method)
    t.add_row("ACTION",  payload.action)
    t.add_row("ENCTYPE", payload.enctype)
    t.add_row("HEADERS", json.dumps(payload.headers, indent=2))
    t.add_row("DATA",    json.dumps(payload.data_dict(), indent=2))
    t.add_row("COOKIES", json.dumps(payload.cookies, indent=2))
    console.print(t)


def render_parsed(payload: FormPayload) -> None:
    gen = CodeGenerator
    console.print("\n[warn]── PARSED PAYLOAD ──[/warn]\n")
    console.print(gen._dict_literal("headers", payload.headers))
    console.print()
    console.print(gen._dict_literal("data", payload.data_dict()))
    console.print()
    console.print(gen._dict_literal("cookies", payload.cookies))
    console.print()
    console.print(f"next = {payload.action!r}")


def render_source_code(url: str, payload: FormPayload) -> str:
    code = CodeGenerator.build_script(url, payload)
    console.print("\n[warn]── SOURCE CODE ──[/warn]\n")
    console.print(Syntax(code, "python", theme="monokai", line_numbers=False, word_wrap=True))
    return code


# ══════════════════════════════════════════════════════════════
# 9. FLOW
# ══════════════════════════════════════════════════════════════
def ask_url() -> str:
    raw = Prompt.ask("[accent]URL target[/accent]").strip()
    if not raw:
        raise ValueError("URL kosong")
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw
    return raw


def choose_mode() -> str:
    console.print(Panel(
        "[key]1[/key]. Source Payload    (ringkasan tabel)\n"
        "[key]2[/key]. Parsed Payload    (dict Python)\n"
        "[key]3[/key]. Source Code       (skrip siap copy-paste)\n"
        "[key]4[/key]. Save to File      (skrip .py di disk)",
        title="Output Mode",
        border_style="green",
        padding=(0, 2),
    ))
    return Prompt.ask("[accent]Pilih mode[/accent]",
                      choices=["1", "2", "3", "4"], default="3")


def run_extractor() -> None:
    try:
        url = ask_url()
    except ValueError:
        err("URL tidak valid.")
        return

    mode = choose_mode()
    ex   = WebExtractor()

    with Progress(SpinnerColumn(), TextColumn("[brand]{task.description}[/brand]"),
                  console=console, transient=True) as prog:
        task = prog.add_task("Mengambil halaman...", total=None)
        result = ex.fetch(url)
        prog.update(task, description="Selesai.")

    if not result:
        return

    resp, soup = result
    forms = soup.find_all("form")
    if not forms:
        err("Tidak ada <form> pada halaman ini.")
        return

    console.print(
        f"\n[ok]✓[/ok] HTTP [accent]{resp.status_code}[/accent] · "
        f"[ok]{len(forms)} form[/ok] · final URL: [dim]{resp.url}[/dim]\n"
    )

    # Base URL untuk resolve action = URL final (setelah redirect)
    base = resp.url

    saved_files: list[Path] = []

    for idx, form in enumerate(forms, 1):
        console.print(f"[brand]── Form #{idx} ──[/brand]")
        payload = ex.build_payload(resp, form, base)

        if mode == "1":
            render_summary(payload)
        elif mode == "2":
            render_parsed(payload)
        elif mode == "3":
            render_source_code(base, payload)
        else:
            code = CodeGenerator.build_script(base, payload)
            fname = safe_filename(base).replace(".py", f"_f{idx}.py")
            path = Path.cwd() / fname
            path.write_text(code, encoding="utf-8")
            saved_files.append(path)
            console.print(f"[ok]✓[/ok] Disimpan: [accent]{path}[/accent]")

        console.print()

    if saved_files:
        console.print(f"[ok]Total {len(saved_files)} file disimpan.[/ok]")
        if Confirm.ask("[accent]Jalankan file pertama sekarang?[/accent]", default=False):
            try:
                subprocess.run([sys.executable, str(saved_files[0])], check=False)
            except Exception as e:
                err(f"Gagal menjalankan: {e}")


def main_menu() -> None:
    while True:
        banner()
        console.print(Panel(
            "[key]1[/key]. Extract Web Data\n"
            "[key]2[/key]. Keluar",
            title="Menu", border_style="green", padding=(0, 2),
        ))
        choice = Prompt.ask("[accent]Pilihan[/accent]", choices=["1", "2"], default="1")
        if choice == "1":
            try:
                run_extractor()
            except KeyboardInterrupt:
                console.print("\n[warn]Dibatalkan.[/warn]")
            except Exception as e:
                err(f"Unexpected: {e}")
            pause()
        else:
            console.print("[ok]Sampai jumpa.[/ok]")
            return


# ══════════════════════════════════════════════════════════════
# 10. ENTRY
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[warn]Program dihentikan.[/warn]")
    except Exception as e:
        err(f"Fatal: {e}")
        sys.exit(1)
