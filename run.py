import sys, bs4, requests, rich, datetime, os, random, re, json, urllib.parse
from bs4 import BeautifulSoup as bs
from datetime import datetime
from itertools import count
from rich import print as prints
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
import concurrent.futures

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

def clear():
    try:
        if "linux" in sys.platform.lower():
            os.system("clear")
        elif "win" in sys.platform.lower():
            os.system("cls")
    except:
        pass
        
def banner():
    clear()
    Console().print(
        Panel(
            """
[bold red]███████████████████████ [bold yellow]NAME  : [bold green]FANKY 
[bold red]███████████████████████ [bold yellow]Githb : [bold green]github.com/fanky86  
[bold red]███████████████████████ [bold yellow]scrip : [bold green]Advanced Web Scraper 
[bold white]███████████████████████          
[bold white]███████████████████████      
[bold white]███████████████████████ 
[bold white]""",
            width=80,
            style=f"{color_panel}",
        )
    )

# ----------[ ENHANCED SCRAPER CLASS ]---------- #
class AdvancedWebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def get_all_links(self, url, soup):
        """Extract all links from page"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urllib.parse.urljoin(url, href)
            links.append({
                'text': link.get_text(strip=True),
                'url': full_url,
                'type': 'internal' if self.domain in full_url else 'external'
            })
        return links

    def get_all_images(self, url, soup):
        """Extract all images from page"""
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            full_url = urllib.parse.urljoin(url, src)
            images.append({
                'src': full_url,
                'alt': img.get('alt', 'No alt text'),
                'title': img.get('title', 'No title')
            })
        return images

    def get_all_forms(self, url, soup):
        """Extract all forms from page"""
        forms = []
        for form in soup.find_all('form'):
            form_data = {
                'action': urllib.parse.urljoin(url, form.get('action', '')),
                'method': form.get('method', 'get').upper(),
                'inputs': []
            }
            
            for input_tag in form.find_all('input'):
                form_data['inputs'].append({
                    'name': input_tag.get('name', ''),
                    'type': input_tag.get('type', 'text'),
                    'value': input_tag.get('value', '')
                })
            
            for select in form.find_all('select'):
                options = []
                for option in select.find_all('option'):
                    options.append({
                        'value': option.get('value', ''),
                        'text': option.get_text(strip=True)
                    })
                form_data['inputs'].append({
                    'name': select.get('name', ''),
                    'type': 'select',
                    'options': options
                })
            
            forms.append(form_data)
        return forms

    def get_meta_tags(self, soup):
        """Extract all meta tags"""
        meta_tags = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content', '')
            if name:
                meta_tags[name] = content
        return meta_tags

    def get_scripts(self, url, soup):
        """Extract all scripts"""
        scripts = []
        for script in soup.find_all('script', src=True):
            src = script['src']
            full_url = urllib.parse.urljoin(url, src)
            scripts.append({
                'src': full_url,
                'type': script.get('type', 'text/javascript')
            })
        return scripts

    def get_stylesheets(self, url, soup):
        """Extract all CSS files"""
        stylesheets = []
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href', '')
            if href:
                full_url = urllib.parse.urljoin(url, href)
                stylesheets.append(full_url)
        return stylesheets

    def get_page_text(self, soup):
        """Extract clean text from page"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        return soup.get_text(separator='\n', strip=True)

    def scrape_url(self, url, options):
        """Main scraping function"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                transient=True,
            ) as progress:
                task = progress.add_task(f"[{color_text}]Scraping {url}...", total=100)
                
                response = self.session.get(url, timeout=30)
                progress.update(task, advance=30)
                
                if response.status_code != 200:
                    return None, f"Error: HTTP {response.status_code}"
                
                soup = bs(response.content, 'html.parser')
                progress.update(task, advance=30)
                
                result = {
                    'url': url,
                    'title': soup.title.string if soup.title else 'No title',
                    'status_code': response.status_code,
                    'headers': dict(response.headers)
                }
                
                # Apply selected scraping options
                if 'links' in options:
                    result['links'] = self.get_all_links(url, soup)
                if 'images' in options:
                    result['images'] = self.get_all_images(url, soup)
                if 'forms' in options:
                    result['forms'] = self.get_all_forms(url, soup)
                if 'meta' in options:
                    result['meta_tags'] = self.get_meta_tags(soup)
                if 'scripts' in options:
                    result['scripts'] = self.get_scripts(url, soup)
                if 'styles' in options:
                    result['stylesheets'] = self.get_stylesheets(url, soup)
                if 'text' in options:
                    result['text'] = self.get_page_text(soup)
                
                progress.update(task, advance=40)
                return result, None
                
        except Exception as e:
            return None, f"Error: {str(e)}"

# ----------[ MENU BOT ]---------- #
class botdata:
    def menu(self):
        banner()
        prints(
            Panel(
                f"""{P2}[{color_text}01{P2}]. Advanced Web Scraper
{P2}[{color_text}02{P2}]. Multi-URL Scraper
{P2}[{color_text}03{P2}]. Form Data Extractor
{P2}[{color_text}04{P2}]. Content Analyzer""",
                width=80,
                style=f"{color_panel}",
            )
        )
        menu = console.input(f" {H2}• {P2}pilih menu : ")
        if menu in ["01", "1"]:
            AdvancedWebScraperMenu().main_menu()
        elif menu in ["02", "2"]:
            MultiURLScraper().scrape_multiple()
        elif menu in ["03", "3"]:
            get_data_web()
        elif menu in ["04", "4"]:
            ContentAnalyzer().analyze()
        else:
            exit(
                prints(
                    Panel(f"{M2}🙏 Masukan Yang Bener Tolol", width=80, style=f"{color_panel}")
                )
            )

class AdvancedWebScraperMenu:
    def __init__(self):
        self.scraper = AdvancedWebScraper()

    def main_menu(self):
        banner()
        prints(Panel(f"{H2}Advanced Web Scraper - Pilih Opsi Scraping", width=80, style=f"{color_panel}"))
        
        url = console.input(f" {H2}• {P2}Masukan URL : ")
        
        prints(
            Panel(
                f"""{P2}[{color_text}01{P2}]. All Content
{P2}[{color_text}02{P2}]. Links Only
{P2}[{color_text}03{P2}]. Images Only  
{P2}[{color_text}04{P2}]. Forms Only
{P2}[{color_text}05{P2}]. Meta Tags Only
{P2}[{color_text}06{P2}]. Custom Selection""",
                width=80,
                style=f"{color_panel}",
            )
        )
        
        choice = console.input(f" {H2}• {P2}Pilih opsi : ")
        
        options_map = {
            '1': ['links', 'images', 'forms', 'meta', 'scripts', 'styles', 'text'],
            '2': ['links'],
            '3': ['images'],
            '4': ['forms'],
            '5': ['meta'],
            '6': self.custom_selection()
        }
        
        options = options_map.get(choice, ['links', 'images', 'forms'])
        self.display_results(url, options)

    def custom_selection(self):
        prints(Panel(f"{H2}Pilih elemen yang ingin di-scrape:", width=80, style=f"{color_panel}"))
        options = []
        if console.input(f" {H2}• {P2}Scrape links? (y/n): ").lower() == 'y':
            options.append('links')
        if console.input(f" {H2}• {P2}Scrape images? (y/n): ").lower() == 'y':
            options.append('images')
        if console.input(f" {H2}• {P2}Scrape forms? (y/n): ").lower() == 'y':
            options.append('forms')
        if console.input(f" {H2}• {P2}Scrape meta tags? (y/n): ").lower() == 'y':
            options.append('meta')
        return options

    def display_results(self, url, options):
        result, error = self.scraper.scrape_url(url, options)
        
        if error:
            prints(Panel(f"{M2}Error: {error}", width=80, style=f"{color_panel}"))
            return

        # Display results in organized panels
        prints(Panel(f"{H2}Scraping Results for: {url}", width=80, style=f"{color_panel}"))
        prints(Panel(f"{B2}Title: {P2}{result.get('title', 'N/A')}", width=80, style=f"{color_panel}"))
        prints(Panel(f"{B2}Status Code: {P2}{result.get('status_code', 'N/A')}", width=80, style=f"{color_panel}"))

        if 'links' in options and 'links' in result:
            table = Table(title=f"{H2}Links Found", show_header=True, header_style="bold magenta")
            table.add_column("Type", style="cyan")
            table.add_column("Text", style="white")
            table.add_column("URL", style="green")
            
            for link in result['links'][:10]:  # Show first 10 links
                table.add_row(link['type'], link['text'][:50] + "..." if len(link['text']) > 50 else link['text'], link['url'][:70] + "..." if len(link['url']) > 70 else link['url'])
            
            console.print(table)
            prints(Panel(f"{K2}Total Links: {len(result['links'])}", width=80, style=f"{color_panel}"))

        if 'images' in options and 'images' in result:
            table = Table(title=f"{H2}Images Found", show_header=True, header_style="bold magenta")
            table.add_column("Alt Text", style="cyan")
            table.add_column("Source", style="white")
            
            for img in result['images'][:10]:
                table.add_row(img['alt'][:30] or "No alt", img['src'][:70] + "..." if len(img['src']) > 70 else img['src'])
            
            console.print(table)
            prints(Panel(f"{K2}Total Images: {len(result['images'])}", width=80, style=f"{color_panel}"))

        if 'forms' in options and 'forms' in result:
            for i, form in enumerate(result['forms']):
                prints(Panel(f"{U2}Form {i+1}\n{B2}Action: {P2}{form['action']}\n{B2}Method: {P2}{form['method']}", width=80, style=f"{color_panel}"))
                
                if form['inputs']:
                    table = Table(show_header=True, header_style="bold yellow")
                    table.add_column("Name", style="cyan")
                    table.add_column("Type", style="white")
                    table.add_column("Value", style="green")
                    
                    for inp in form['inputs']:
                        table.add_row(
                            inp.get('name', ''),
                            inp.get('type', ''),
                            str(inp.get('value', ''))[:50]
                        )
                    
                    console.print(table)

        # Save results option
        if console.input(f" {H2}• {P2}Save results to file? (y/n): ").lower() == 'y':
            filename = f"scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            prints(Panel(f"{H2}Results saved to: {filename}", width=80, style=f"{color_panel}"))

class MultiURLScraper:
    def scrape_multiple(self):
        banner()
        prints(Panel(f"{H2}Multi-URL Scraper", width=80, style=f"{color_panel}"))
        
        urls = []
        prints(f"{H2}• {P2}Masukkan URLs (ketik 'done' ketika selesai):")
        while True:
            url = console.input(f" {H2}→ {P2}URL: ")
            if url.lower() == 'done':
                break
            if url:
                urls.append(url)
        
        if not urls:
            prints(Panel(f"{M2}Tidak ada URL yang dimasukkan!", width=80, style=f"{color_panel}"))
            return

        scraper = AdvancedWebScraper()
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
        ) as progress:
            task = progress.add_task("Scraping multiple URLs...", total=len(urls))
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_url = {executor.submit(scraper.scrape_url, url, ['links', 'title']): url for url in urls}
                
                for future in concurrent.futures.as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        result, error = future.result()
                        if result:
                            results.append(result)
                        progress.update(task, advance=1)
                    except Exception as e:
                        prints(f"{M2}Error scraping {url}: {str(e)}")

        # Display summary
        table = Table(title="Scraping Summary", show_header=True, header_style="bold magenta")
        table.add_column("URL", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("Links", style="green")
        table.add_column("Status", style="yellow")
        
        for result in results:
            table.add_row(
                result['url'][:50] + "..." if len(result['url']) > 50 else result['url'],
                result.get('title', 'N/A')[:30] + "..." if len(result.get('title', '')) > 30 else result.get('title', 'N/A'),
                str(len(result.get('links', []))),
                "✅ Success" if result.get('status_code') == 200 else "❌ Failed"
            )
        
        console.print(table)

class ContentAnalyzer:
    def analyze(self):
        banner()
        prints(Panel(f"{H2}Content Analyzer", width=80, style=f"{color_panel}"))
        
        url = console.input(f" {H2}• {P2}Masukan URL untuk dianalisis : ")
        
        scraper = AdvancedWebScraper()
        result, error = scraper.scrape_url(url, ['text', 'meta', 'links', 'images'])
        
        if error:
            prints(Panel(f"{M2}Error: {error}", width=80, style=f"{color_panel}"))
            return

        # Analyze content
        text = result.get('text', '')
        words = text.split()
        sentences = text.split('.')
        
        prints(Panel(f"{H2}Content Analysis Results", width=80, style=f"{color_panel}"))
        prints(Panel(f"{B2}Word Count: {P2}{len(words)}", width=80, style=f"{color_panel}"))
        prints(Panel(f"{B2}Sentence Count: {P2}{len(sentences)}", width=80, style=f"{color_panel}"))
        prints(Panel(f"{B2}Character Count: {P2}{len(text)}", width=80, style=f"{color_panel}"))
        prints(Panel(f"{B2}Links Found: {P2}{len(result.get('links', []))}", width=80, style=f"{color_panel}"))
        prints(Panel(f"{B2}Images Found: {P2}{len(result.get('images', []))}", width=80, style=f"{color_panel}"))

# -----------------------[ ORIGINAL FORM SCRAPER ]--------------------#
class get_data_web:
    def __init__(self):
        self.xyz = requests.Session()
        prints(Panel(f"{H2}Masukkan URL yang ingin diambil source code-nya", width=80, style=f"{color_panel}"))
        url = console.input(f" {H2}• {P2}Masukan URL : ")
        prints(
            Panel(
                f"""{P2}[{color_text}01{P2}].Source Payload [{color_text}02{P2}].Parsed Payload [{color_text}03{P2}].Source Code Post Requests""",
                width=80,
                style=f"{color_panel}",
            )
        )
        self.tanya = console.input(f" {H2}• {P2}pilih menu : ")
        self.domain = url.split('/')[2] if '//' in url else url.split('/')[0]
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
    try:os.system("git pull")
    except:pass
    botdata().menu()
