# -----------------------[ DEFF SCRAPT METODE ]--------------------#
import sys, bs4, requests, rich, datetime, os, random, re
from bs4 import BeautifulSoup as bs
from datetime import datetime
from itertools import count
from rich import print as prints
from rich.panel import Panel
from rich.console import Console

console = Console()
done = False
results = []

# ------------------[  MODULE  ]-------------------#
M2 = "[#FF0000]"  # MERAH
H2 = "[#00FF00]"  # HIJAU
K2 = "[#FFFF00]"  # KUNING
B2 = "[#00C8FF]"  # BIRU
P2 = "[#FFFFFF]"  # PUTIH
U2 = "[#AF00FF]"  # UNGU
O2 = "[#FF8F00]"  # ORANGE
try:
    file_color = open("data/theme_color", "r").read()
    color_text, color_panel = file_color.split("|")[:2]
except:
    color_text = "[#00FF00]"
    color_panel = "#00FF00"

try:
    color_table = open("data/theme_color", "r").read()
except FileNotFoundError:
    color_table = "#00FF00"

if "linux" in sys.platform.lower():
    os.system("clear")
elif "win" in sys.platform.lower():
    os.system("cls")

def banner():
    Console().print(
        Panel(
            """
[bold red]███████████████████████ [bold yellow]NAME  : [bold green]FANKY 
[bold red]███████████████████████ [bold yellow]Githb : [bold green]github.com/fanky86  
[bold red]███████████████████████ [bold yellow]scrip : [bold green]scrapeing website 
[bold white]███████████████████████          
[bold white]███████████████████████          
[bold white]███████████████████████ 
[bold white]""",
            width=60,
            style=f"{color_panel}",
        )
    )

# ----------[ MENU BOT ]---------- #
class botdata:
    def menu(self):
        banner()
        prints(
            Panel(
                f"""{P2}[{color_text}01{P2}].Get Data Web""",
                width=60,
                style=f"{color_panel}",
            )
        )
        menu = console.input(f" {H2}• {P2}pilih menu : ")
        if menu in ["01", "1"]:
            get_data_web()
        else:
            exit(
                prints(
                    Panel(f"{M2}🙏 Masukan Yang Bener Tolol", width=60, style=f"{color_panel}")
                )
            )

class get_data_web:
    def __init__(self):
        self.xyz = requests.Session()
        prints(Panel(f"{H2}Masukkan URL yang ingin diambil source code-nya", width=60, style=f"{color_panel}"))
        url = console.input(f" {H2}• {P2}Masukan URL : ")
        prints(
            Panel(
                f"""{P2}[{color_text}01{P2}].Source Payload [{color_text}02{P2}].Parsed Payload [{color_text}03{P2}].Source Code Post Requests""",
                width=60,
                style=f"{color_panel}",
            )
        )
        self.tanya = console.input(f" {H2}• {P2}pilih menu : ")
        self.domain = url.split('/')[2]  # Memperbaiki ekstraksi domain
        self.get_form(url)

    def get_form(self, url):
        req = self.xyz.get(url)
        raq = bs(req.content, "html.parser")
        for x in raq.find_all("form"):
            if self.tanya in ["1", "01", "a"]:
                self.printing1(req, x)
            elif self.tanya in ["2", "02", "b"]:
                self.printing2(req, x)
            elif self.tanya in ["3", "03", "c"]:
                self.printing3(url, req, x)
            else:
                exit(f"{H2}• {P2} Isi Yang Benar Asu")

    def get_head1(self, req):
        data = {}
        head = req.headers
        usls = ["cookie", "set-cookie", "report-to", "expires", "x-fb-debug", "date", "last-modified", "etag"]
        for x, y in head.items():
            if x.lower() not in usls:
                data[x] = y
        return data

    def get_data1(self, form):
        return {y["name"]: y.get("value", "") for y in form.find_all("input") if "name" in y.attrs}

    def get_data2(self, form):
        return [y for y in form.find_all("input")]

    def get_post1(self, form):
        z = form.get("action", "")
        if z.startswith(("https://", "http://")):
            return z
        return f"https://{self.domain}{z}"

    def printing1(self, req, x):
        head = self.get_head1(req)
        data = self.get_data1(x)
        post = self.get_post1(x)
        coki = self.xyz.cookies.get_dict()
        
        prints(Panel(f"{P2}[Source Payload]", width=80, style=f"{color_panel}"))
        prints(Panel(f"{P2}[HOST]{H2} {self.domain}", width=80, style=f"{color_panel}"))
        prints(f"{P2}[Head]{H2} {head}")
        prints(f"{P2}[Data]{H2} {data}")
        prints(f"{P2}[Coki]{H2} {coki}")
        prints(f"{P2}[Post]{H2} {post}")

    def printing2(self, req, x):
        head = self.get_head1(req)
        data = self.get_data2(x)
        post = self.get_post1(x)
        coki = self.xyz.cookies.get_dict()
        
        prints("\n\n[PARSED PAYLOAD]\n")
        prints(f"head = {head}")
        prints("data = {")
        for y in data:
            try:
                name = y.get("name", "")
                value = y.get("value", "")
                prints(f"    '{name}': '{value}',")
            except:
                continue
        prints("}")
        prints(f"cookie = {coki}")
        prints(f"next = '{post}'")
        prints("post = requests.post(next, headers=head, data=data, cookies=cookie)")

    def printing3(self, url, req, x):
        head = self.get_head1(req)
        data = self.get_data2(x)
        post = self.get_post1(x)
        
        prints("\n\n[SOURCE CODE POST REQUESTS]\n")
        prints(f"url  = '{url}'")
        prints("requ = bs(requests.get(url).content, 'html.parser')")
        prints(f"head = {head}")
        prints("data = {")
        for y in data:
            try:
                name = y.get("name", "")
                value = y.get("value", "(.*?)")
                prints(f"    '{name}': '{value}',")
            except:
                continue
        prints("}")
        prints("cookie = requests.Session().cookies.get_dict()")
        prints(f"next = '{post}'")
        prints("post = requests.post(next, headers=head, data=data, cookies=cookie)")

# -----------------------[ SYSTEM-CONTROL ]--------------------#
if __name__ == "__main__":
    botdata().menu()
