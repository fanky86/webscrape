# -----------------------[ DEFF SCRAPT METODE ]--------------------#
import requests, bs4, json, os, sys, random, datetime, time, re, rich, base64, subprocess, uuid, calendar
from time import sleep
from datetime import date, datetime
from rich import pretty
from rich.tree import Tree
from rich.panel import Panel
from rich import print as cetak
from rich import print as rprint
from rich import print as prints
from rich.progress import track
from rich.text import Text as tekz
from rich.console import Console
from rich.text import Text
from rich.columns import Columns
from rich.panel import Panel as nel
from rich.panel import Panel as panel
from bs4 import BeautifulSoup as sop
from bs4 import BeautifulSoup as par
from rich.console import Group as gp
from bs4 import BeautifulSoup as parser
from rich.columns import Columns as col
from rich.console import Console as sol
from rich.console import Console
from bs4 import BeautifulSoup as beautifulsoup
from rich.markdown import Markdown as mark
from concurrent.futures import ThreadPoolExecutor as tred
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn


done = False
results = []

console = Console()

# ------------------[ MODULE COLORS ]-------------------#
M2 = "[#FF0000]"  # MERAH
H2 = "[#00FF00]"  # HIJAU
K2 = "[#FFFF00]"  # KUNING
B2 = "[#00C8FF]"  # BIRU
P2 = "[#FFFFFF]"  # PUTIH
U2 = "[#AF00FF]"  # UNGU
O2 = "[#FF8F00]"  # ORANGE
try:
    file_color = open("data/theme_color", "r").read()
    color_text = file_color.split("|")[0]
    color_panel = file_color.split("|")[1]
except:
    color_text = "[#00FF00]"
    W1 = random.choice([M2, H2, K2])
    W2 = random.choice([K2, M2, K2])
    W3 = random.choice([H2, K2, M2])
    color_panel = "#00FF00"
    color_ok = "#00FF00"
    color_cp = "#FFFF00"
try:
    color_table = open("data/theme_color", "r").read()
except FileNotFoundError:
    color_table = "#00FF00"
#------------[ INDICATION ]---------------#
P = '\x1b[1;97m' # PUTIH
M = '\x1b[1;91m' # MERAH
H = '\x1b[1;92m' # HIJAU
K = '\x1b[1;93m' # KUNING
B = '\x1b[1;94m' # BIRU
U = '\x1b[1;95m' # UNGU
O = '\x1b[1;96m' # BIRU MUDA
N = '\x1b[0m'	# WARNA MATI

# Warna Default
try:
    file_color = open("data/theme_color", "r").read()
    color_text = file_color.split("|")[0]
    color_panel = file_color.split("|")[1]
except FileNotFoundError:
    color_text = H2
    color_panel = H2

# Membersihkan Layar
if "linux" in sys.platform.lower():
    os.system("clear")
elif "win" in sys.platform.lower():
    os.system("cls")

# -----------------------[ MENU BOT ]--------------------#
class BotData:
    def menu(self):
        prints(
            Panel(
                f"{P2}[{color_text}01{P2}]. Get Data Web [{color_text}03{P2}]. Kembali Ke Menu",
                width=60,
                style=color_panel,
            )
        )
        menu = console.input(f" {H2}• {P2}Pilih Menu: ")
        if menu in ["01", "1"]:
            GetDataWeb()
        elif menu in ["03", "3"]:
            exit("Kembali ke menu utama.")
        else:
            prints(
                Panel(
                    f"{M2}🙏 Masukkan yang benar!",
                    width=60,
                    style=color_panel,
                )
            )
            self.menu()

# -----------------------[ SCRAPING CLASS ]--------------------#
class GetDataWeb:
    def __init__(self):
        self.session = requests.Session()
        prints(
            Panel(
                f"{H2}Masukkan URL/Link yang akan diambil source code-nya",
                width=60,
                style=color_panel,
            )
        )
        url = console.input(f" {H2}• {P2}Masukkan URL: ")
        prints(
            Panel(
                f"{P2}[{color_text}01{P2}]. Source Payload\n[{color_text}02{P2}]. Parsed Payload\n[{color_text}03{P2}]. Source Code Post Requests",
                width=60,
                style=color_panel,
            )
        )
        self.option = console.input(f" {H2}• {P2}Pilih Menu: ")
        self.domain = url.split("/")[2]  # Mendapatkan domain dari URL
        self.get_form(url)

    def get_form(self, url):
        req = self.session.get(url)
        soup = bs(req.content, "html.parser")
        for form in soup.find_all("form"):
            if self.option in ["1", "01"]:
                self.printing1(req, form)
            elif self.option in ["2", "02"]:
                self.printing2(req, form)
            elif self.option in ["3", "03"]:
                self.printing3(url, req, form)
            else:
                prints(
                    Panel(
                        f"{M2}• {P2}Pilih menu yang benar!",
                        width=60,
                        style=color_panel,
                    )
                )

    def get_head(self, req):
        headers = req.headers
        filtered_headers = {
            k: v
            for k, v in headers.items()
            if k.lower() not in ["cookie", "set-cookie", "expires", "date"]
        }
        return filtered_headers

    def get_data(self, form):
        data = {}
        for input_tag in form.find_all("input"):
            try:
                data[input_tag["name"]] = input_tag.get("value", "")
            except KeyError:
                continue
        return data

    def get_post_url(self, form):
        action = form.get("action", "")
        if action.startswith("http"):
            return action
        else:
            return f"https://{self.domain}{action}"

    def printing1(self, req, form):
        headers = self.get_head(req)
        data = self.get_data(form)
        post_url = self.get_post_url(form)
        cookies = self.session.cookies.get_dict()

        prints(
            Panel(
                f"{P2}[SOURCE PAYLOAD]",
                width=80,
                style=color_panel,
            )
        )
        prints(Panel(f"{P2}[HOST]{H2} {self.domain}", width=80, style=color_panel))
        prints(f"{P2}[HEADERS]{H2} {headers}")
        prints(f"{P2}[DATA]{H2} {data}")
        prints(f"{P2}[COOKIES]{H2} {cookies}")
        prints(f"{P2}[POST URL]{H2} {post_url}")

    def printing2(self, req, form):
        headers = self.get_head(req)
        data = self.get_data(form)
        post_url = self.get_post_url(form)
        cookies = self.session.cookies.get_dict()

        print("\n\n[PARSED PAYLOAD]\n")
        print("headers = {")
        for key, value in headers.items():
            print(f"    '{key}': '{value}',")
        print("}")
        print("data = {")
        for key, value in data.items():
            print(f"    '{key}': '{value}',")
        print("}")
        print("cookies = {")
        for key, value in cookies.items():
            print(f"    '{key}': '{value}',")
        print("}")
        print(f"post_url = '{post_url}'")

    def printing3(self, url, req, form):
        headers = self.get_head(req)
        data = self.get_data(form)
        post_url = self.get_post_url(form)

        print("\n\n[SOURCE CODE POST REQUESTS]\n")
        print(f"url = '{url}'")
        print("headers = {")
        for key, value in headers.items():
            print(f"    '{key}': '{value}',")
        print("}")
        print("data = {")
        for key, value in data.items():
            print(f"    '{key}': '{value}',")
        print("}")
        print(f"post_url = '{post_url}'")


# -----------------------[ SYSTEM-CONTROL ]--------------------#
if __name__ == "__main__":
    BotData().menu()
