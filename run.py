# -----------------------[ DEFF SCRAPT METODE ]--------------------#
import sys,bs4, requests,rich,datetime,os, random 
from bs4 import BeautifulSoup as bs
from datetime import datetime
from itertools import count
from requests import get
from rich import print as prints
from bs4 import BeautifulSoup
from rich import print as cetak
from rich import print as prints
from rich.panel import Panel as nel
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


if "linux" in sys.platform.lower():
	os.system("clear")
elif "win" in sys.platform.lower():
	os.system("cls")
###----------[ MENU BOT ]---------- ###
class botdata:
    def menu(self):
        prints(
            Panel(
                f"""{P2}[{color_text}01{P2}]. Get Data Web [{color_text}02{P2}]. Spam SMS [{color_text}03{P2}]. Kembali Ke menu""",
                width=60,
                style=f"{color_panel}",
            )
        )
        menu = console.input(f" {H2}• {P2}pilih menu : ")
        if menu in ["01", "1"]:
            get_data_web().__init__()
        elif menu in ["02", "2"]:
            spam()
        elif menu in ["03", "3"]:
            back()
        else:
            exit(
                prints(
                    Panel(
                        f"""{M2}🙏 Masukan Yang Bener Tolol""",
                        width=60,
                        style=f"{color_panel}",
                    )
                )
            )


class get_data_web:
    def __init__(self):
        self.xyz = requests.Session()
        prints(
            Panel(
                f"""{H2}masukan url/link yang mau di source code""",
                width=60,
                style=f"{color_panel}",
            )
        )
        url = console.input(f" {H2}• {P2}Masukan URL : ")
        prints(
            Panel(
                f"""{P2}[{color_text}01{P2}].Source Payload	[{color_text}02{P2}].Parsed Payload	\n[{color_text}03{P2}].Source Code Post Requests""",
                width=60,
                style=f"{color_panel}",
            )
        )
        self.tanya = console.input(f" {H2}• {P2}pilih menu : ")
        self.domain = url.split("/")[2]
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
        usls = [
            "cookie",
            "set-cookie",
            "report-to",
            "expires",
            "x-fb-debug",
            "date",
            "last-modified",
            "etag",
        ]
        for x, y in zip(head.keys(), head.values()):
            try:
                if x.lower() in usls:
                    continue
                else:
                    data.update({x: y})
            except Exception as e:
                continue
        return data

    def get_data1(self, form):
        data = {}
        for y in form.find_all("input"):
            try:
                data.update({y["name"]: y["value"]})
            except Exception as e:
                continue
        return data

    def get_data2(self, form):
        data = []
        for y in form.find_all("input"):
            try:
                data.append(y)
            except Exception as e:
                continue
        return data

    def get_post1(self, form):
        z = form["action"]
        if "https://" + self.domain in z:
            return z
        elif "http://" + self.domain in z:
            return z
        else:
            return "https://%s%s" % (self.domain, z)

    def printing1(self, req, x):
        head = self.get_head1(req)
        data = self.get_data1(x)
        post = self.get_post1(x)
        coki = self.xyz.cookies.get_dict()
        prints(
            Panel(f"""{P2}			[Source Payload]{P2}""", width=80, style=f"{color_panel}")
        )
        prints(
            Panel(
                f"""{P2}[HOST]{H2}  %s""" % (self.domain),
                width=80,
                style=f"{color_panel}",
            )
        )
        prints(f"""{P2}[Head]{H2}  %s""" % (head))
        
        prints(f"""{P2}[Data]{H2}  %s""" % (data))
        
        prints(f"""{P2}[Coki]{H2}  %s""" % (coki))
        
        prints(f"""{P2}[Post]{H2}  %s""" % (post))
        

    def printing2(self, req, x):
        head = self.get_head1(req)
        data = self.get_data2(x)
        post = self.get_post1(x)
        coki = self.xyz.cookies.get_dict()
        print("\n\n[PARSED PAYLOAD]\n")
        print("head = {")
        for x, y in zip(head.keys(), head.values()):
            print("    %s%s: %s" % (x, " " * (29 - len(x)), y))
        print("    }")
        print("data = {")
        for x in data:
            try:
                if "value" in str(x):
                    dp = "name=" + re.search("name=(.*?)/>", str(x)).group(1)
                    fp = re.search('value="(.*?)"', str(dp)).group(1)
                    print(
                        "    %s%s: '%s'," % (x["name"], " " * (19 - len(x["name"])), fp)
                    )
                elif "name" in str(x):
                    print("    %s%s: ''," % (x["name"], " " * (19 - len(x["name"]))))
                else:
                    continue
            except Exception as e:
                continue
        print("    }")
        print("cookie = {")
        for x, y in zip(coki.keys(), coki.values()):
            print("    %s%s: %s" % (x, " " * (5 - len(x)), y))
        print("    }")
        print("next = '%s'" % (post))
        print(
            "post = requests.Session().post(next,headers=head,data=data,cookies=cookie)"
        )

    def printing3(self, url, req, x):
        head = self.get_head1(req)
        data = self.get_data2(x)
        post = self.get_post1(x)
        print("\n\n[SOURCE CODE POST REQUESTS]\n")
        print("url  = '%s'" % (url))
        print("requ = bs(requests.Session().get(url).content,'html.parser')")
        print("head = {")
        for x, y in zip(head.keys(), head.values()):
            print("    %s%s: %s" % (x, " " * (29 - len(x)), y))
        print("    }")
        print("data = {")
        for x in data:
            try:
                if "value" in str(x):
                    dp = "name=" + re.search("name=(.*?)/>", str(x)).group(1)
                    fp = re.search('value="(.*?)"', str(dp)).group(1)
                    gp = dp.replace(fp, "(.*?)")
                    rs = "re.search('%s',str(requ)).group(1)" % (gp)
                    print(
                        "    %s%s: %s," % (x["name"], " " * (19 - len(x["name"])), rs)
                    )
                elif "name" in str(x):
                    print("    %s%s: ''," % (x["name"], " " * (19 - len(x["name"]))))
                else:
                    continue
            except Exception as e:
                continue
        print("    }")
        print("cookie = requests.Session().cookies.get_dict()")
        print("next = '%s'" % (post))
        print(
            "post = requests.Session().post(next,headers=head,data=data,cookies=cookie)"
        )


# -----------------------[ SYSTEM-CONTROL ]--------------------#
if __name__ == "__main__":
	botdata().menu()
	
	
