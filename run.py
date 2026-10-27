import requests
from bs4 import BeautifulSoup as bs
import re
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Inisialisasi Rich Console
console = Console()

# Variabel warna untuk styling
P2 = "[bold cyan]"
color_text = "[bold yellow]"
color_panel = "bold green"
H2 = "[bold white]"
M2 = "[bold red]"

# Fungsi placeholder untuk back dan spam
def back():
    console.print(Panel("Kembali ke menu utama...", style=color_panel))
    # Logika untuk kembali ke menu utama

def spam():
    console.print(Panel("Fitur spam SMS belum diimplementasikan", style=color_panel))
    # Logika untuk spam SMS

# Fungsi prints untuk kompatibilitas dengan kode lama
def prints(content):
    if isinstance(content, Panel):
        console.print(content)
    else:
        console.print(content)

class botdata:
    def menu(self):
        prints(Panel(f"""{P2}[{color_text}01{P2}]. Get Data Web [{color_text}02{P2}]. Spam SMS [{color_text}03{P2}]. Kembali Ke menu""",
                     width=80, padding=(0,7), style=f"{color_panel}"))
        menu = console.input(f" {H2}• {P2}pilih menu : ")
        if menu in["01","1"]:
            get_data_web()
        elif menu in["02","2"]:
            spam()
        elif menu in["03","3"]:
            back()
        else:
            prints(Panel(f"""{M2}🙏 Masukan Yang Bener Tolol""", width=80, style=f"{color_panel}"))
            self.menu()

class get_data_web:
    
    def __init__(self):
        self.xyz = requests.Session()
        prints(Panel(f"""{H2}masukan url/link yang mau di source code""", 
                     width=80, padding=(0,6), style=f"{color_panel}"))
        url = console.input(f" {H2}• {P2}Masukan URL : ")
        
        # Validasi URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        prints(Panel(f"""{P2}[{color_text}01{P2}].Source Payload\t[{color_text}02{P2}].Parsed Payload\t\n[{color_text}03{P2}].Source Code Post Requests""",
                     width=80, padding=(0,7), style=f"{color_panel}"))
        self.tanya = console.input(f" {H2}• {P2}pilih menu : ")
        
        try:
            self.domain = url.split('/')[2]
            self.get_form(url)
        except IndexError:
            prints(Panel(f"{M2}URL tidak valid!", width=80, style=f"{color_panel}"))
            get_data_web().__init__()
       
    def get_form(self, url):
        try:
            req = self.xyz.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            req.raise_for_status()
        except requests.exceptions.RequestException as e:
            prints(Panel(f"{M2}Error: Gagal mengakses URL - {str(e)}", width=80, style=color_panel))
            return
            
        try:
            raq = bs(req.content, 'html.parser')
        except Exception as e:
            prints(Panel(f"{M2}Error: Gagal parsing HTML - {str(e)}", width=80, style=color_panel))
            return
            
        forms = raq.find_all('form')
        if not forms:
            prints(Panel(f"{M2}Tidak ditemukan form di halaman ini", width=80, style=color_panel))
            return
            
        for x in forms:
            if self.tanya in ['1','01','a']: 
                self.printing1(req, x)
            elif self.tanya in ['2','02','b']: 
                self.printing2(req, x)
            elif self.tanya in ['3','03','c']: 
                self.printing3(url, req, x)
            else: 
                prints(Panel(f"{M2}Isi Yang Benar Asu!", width=80, style=color_panel))
                return

    def get_head1(self, req):
        data = {}
        head = req.headers
        usls = ['cookie', 'set-cookie', 'report-to', 'expires', 
                'x-fb-debug', 'date', 'last-modified', 'etag', 
                'content-length', 'content-encoding']
        for x, y in head.items():
            try:
                if x.lower() in usls: 
                    continue
                else: 
                    data.update({x: y})
            except Exception: 
                continue
        return data

    def get_data1(self, form):
        data = {}
        for y in form.find_all('input'):
            try:
                if 'name' in y.attrs:
                    value = y.get('value', '')
                    data.update({y['name']: value})
            except Exception: 
                continue
        return data

    def get_data2(self, form):
        data = []
        for y in form.find_all('input'):
            try:
                data.append(y)
            except Exception: 
                continue
        return data

    def get_post1(self, form):
        if 'action' not in form.attrs:
            return f'https://{self.domain}'
        
        z = form['action']
        if z.startswith('https://') or z.startswith('http://'):
            return z
        elif z.startswith('//'):
            return 'https:' + z
        elif z.startswith('/'):
            return f'https://{self.domain}{z}'
        else:
            return f'https://{self.domain}/{z}'

    def printing1(self, req, x):
        head = self.get_head1(req)
        data = self.get_data1(x)
        post = self.get_post1(x)
        coki = self.xyz.cookies.get_dict()
        
        prints(Panel(f"""{P2}[Source Payload]{P2}""", width=80, style=color_panel))
        prints(Panel(f"""{P2}[HOST]{H2}  {self.domain}""", width=80, style=color_panel))
        prints(Panel(f"""{P2}[Head]{H2}  {head}""", width=80, style=color_panel))
        prints(Panel(f"""{P2}[Data]{H2}  {data}""", width=80, style=color_panel))
        prints(Panel(f"""{P2}[Coki]{H2}  {coki}""", width=80, style=color_panel))
        prints(Panel(f"""{P2}[Post]{H2}  {post}""", width=80, style=color_panel))
            
    def printing2(self, req, x):
        head = self.get_head1(req)
        data = self.get_data2(x)
        post = self.get_post1(x)
        coki = self.xyz.cookies.get_dict()
        
        console.print('\n\n[bold yellow][PARSED PAYLOAD][/bold yellow]\n')
        console.print('[bold cyan]head = {[/bold cyan]')
        for key, value in head.items():
            spaces = ' ' * (30 - len(key))
            console.print(f'    [green]"{key}"[/green]{spaces}: [yellow]"{value}"[/yellow],')
        console.print('[bold cyan]    }[/bold cyan]\n')
        
        console.print('[bold cyan]data = {[/bold cyan]')
        for input_tag in data:
            try:
                name = input_tag.get('name', '')
                if name:
                    value = input_tag.get('value', '')
                    spaces = ' ' * (20 - len(name))
                    console.print(f'    [green]"{name}"[/green]{spaces}: [yellow]"{value}"[/yellow],')
            except Exception:
                continue
        console.print('[bold cyan]    }[/bold cyan]\n')
        
        console.print('[bold cyan]cookie = {[/bold cyan]')
        for key, value in coki.items():
            spaces = ' ' * (25 - len(key))
            console.print(f'    [green]"{key}"[/green]{spaces}: [yellow]"{value}"[/yellow],')
        console.print('[bold cyan]    }[/bold cyan]\n')
        
        console.print(f'[bold cyan]next[/bold cyan] = [yellow]"{post}"[/yellow]')
        console.print('[bold cyan]post[/bold cyan] = requests.Session().post(next, headers=head, data=data, cookies=cookie)')
        
    def printing3(self, url, req, x):
        head = self.get_head1(req)
        data = self.get_data2(x)
        post = self.get_post1(x)
        
        console.print('\n\n[bold yellow][SOURCE CODE POST REQUESTS][/bold yellow]\n')
        console.print(f'[bold cyan]url[/bold cyan]  = [yellow]"{url}"[/yellow]')
        console.print('[bold cyan]requ[/bold cyan] = bs(requests.Session().get(url).content, "html.parser")')
        
        console.print('[bold cyan]head = {[/bold cyan]')
        for key, value in head.items():
            spaces = ' ' * (30 - len(key))
            console.print(f'    [green]"{key}"[/green]{spaces}: [yellow]"{value}"[/yellow],')
        console.print('[bold cyan]    }[/bold cyan]\n')
        
        console.print('[bold cyan]data = {[/bold cyan]')
        for input_tag in data:
            try:
                name = input_tag.get('name', '')
                if name:
                    value = input_tag.get('value', '')
                    if value:
                        # Create regex pattern for dynamic value extraction
                        pattern = f'name="{re.escape(name)}" value="([^"]*)"'
                        regex_line = f're.search(r"{pattern}", str(requ)).group(1)'
                        spaces = ' ' * (20 - len(name))
                        console.print(f'    [green]"{name}"[/green]{spaces}: {regex_line},')
                    else:
                        spaces = ' ' * (20 - len(name))
                        console.print(f'    [green]"{name}"[/green]{spaces}: [yellow]""[/yellow],')
            except Exception:
                continue
        console.print('[bold cyan]    }[/bold cyan]\n')
        
        console.print('[bold cyan]cookie[/bold cyan] = requests.Session().cookies.get_dict()')
        console.print(f'[bold cyan]next[/bold cyan]  = [yellow]"{post}"[/yellow]')
        console.print('[bold cyan]post[/bold cyan]  = requests.Session().post(next, headers=head, data=data, cookies=cookie)')

# Fungsi main untuk menjalankan program
def main():
    console.clear()
    console.print(Panel.fit("[bold cyan]WEB DATA EXTRACTOR TOOL[/bold cyan]", 
                           style="bold magenta", subtitle="by @bot"))
    
    # Create botdata instance and show menu
    bot = botdata()
    bot.menu()

if __name__ == "__main__":
    # Install required packages jika belum ada
    try:
        from rich.console import Console
    except ImportError:
        import subprocess
        import sys
        console.print("[red]Package 'rich' belum terinstall![/red]")
        install = input("Install package 'rich'? (y/n): ")
        if install.lower() == 'y':
            subprocess.check_call([sys.executable, "-m", "pip", "install", "rich", "requests", "beautifulsoup4"])
            console.print("[green]Package berhasil diinstall! Silakan jalankan ulang program.[/green]")
        else:
            console.print("[yellow]Program tidak dapat berjalan tanpa package 'rich'.[/yellow]")
        sys.exit(1)
    
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Program dihentikan oleh pengguna[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
