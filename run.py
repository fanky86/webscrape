# -----------------------[ DEFF SCRAPT METODE ]--------------------#
import sys,os
import requests
import re
import random
from bs4 import BeautifulSoup as bs
from rich import print as prints
from rich.panel import Panel
from rich.console import Console

console = Console()

# ------------------[ MODULE COLORS ]-------------------#
M2 = "[#FF0000]"  # MERAH
H2 = "[#00FF00]"  # HIJAU
K2 = "[#FFFF00]"  # KUNING
P2 = "[#FFFFFF]"  # PUTIH

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
