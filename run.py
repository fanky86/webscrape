import sys
import os
import json
import re
import urllib.parse
import concurrent.futures
from datetime import datetime
from itertools import count
from bs4 import BeautifulSoup as bs
import requests
from rich import print as prints
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

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

# Default colors
color_text = "[#00FF00]"
color_panel = "#00FF00"
color_table = "#00FF00"

# Try to load theme from file
try:
    if os.path.exists("data/theme_color"):
        with open("data/theme_color", "r") as f:
            file_content = f.read()
            parts = file_content.split("|")
            if len(parts) >= 2:
                color_text = parts[0].strip()
                color_panel = parts[1].strip()
                color_table = color_panel
except Exception:
    pass

def clear():
    """Clear console screen"""
    try:
        if sys.platform.lower().startswith('win'):
            os.system('cls')
        else:
            os.system('clear')
    except:
        pass

def banner():
    """Display banner"""
    clear()
    Console().print(
        Panel(
            """[bold red]███████████████████████ [bold yellow]NAME  : [bold green]FANKY 
[bold red]███████████████████████ [bold yellow]Githb : [bold green]github.com/fanky86  
[bold red]███████████████████████ [bold yellow]script: [bold green]Advanced Web Scraper 
[bold white]███████████████████████          
[bold white]███████████████████████      
[bold white]███████████████████████ 
""",
            width=80,
            style=color_panel,
        )
    )

# ----------[ ENHANCED SCRAPER CLASS ]---------- #
class AdvancedWebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.domain = ""

    def get_all_links(self, url, soup):
        """Extract all links from page"""
        links = []
        try:
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href and href.strip():
                    full_url = urllib.parse.urljoin(url, href)
                    link_type = 'internal' if self.domain in full_url else 'external'
                    links.append({
                        'text': link.get_text(strip=True) or '',
                        'url': full_url,
                        'type': link_type
                    })
        except Exception as e:
            prints(f"{M2}Error extracting links: {str(e)}")
        return links

    def get_all_images(self, url, soup):
        """Extract all images from page"""
        images = []
        try:
            for img in soup.find_all('img', src=True):
                src = img['src']
                if src and src.strip():
                    full_url = urllib.parse.urljoin(url, src)
                    images.append({
                        'src': full_url,
                        'alt': img.get('alt', 'No alt text'),
                        'title': img.get('title', 'No title')
                    })
        except Exception as e:
            prints(f"{M2}Error extracting images: {str(e)}")
        return images

    def get_all_forms(self, url, soup):
        """Extract all forms from page"""
        forms = []
        try:
            for form in soup.find_all('form'):
                action = form.get('action', '')
                form_data = {
                    'action': urllib.parse.urljoin(url, action) if action else url,
                    'method': form.get('method', 'get').upper(),
                    'inputs': []
                }
                
                # Input fields
                for input_tag in form.find_all('input'):
                    form_data['inputs'].append({
                        'name': input_tag.get('name', ''),
                        'type': input_tag.get('type', 'text'),
                        'value': input_tag.get('value', '')
                    })
                
                # Select fields
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
                
                # Textarea fields
                for textarea in form.find_all('textarea'):
                    form_data['inputs'].append({
                        'name': textarea.get('name', ''),
                        'type': 'textarea',
                        'value': textarea.get_text(strip=True)
                    })
                
                forms.append(form_data)
        except Exception as e:
            prints(f"{M2}Error extracting forms: {str(e)}")
        return forms

    def get_meta_tags(self, soup):
        """Extract all meta tags"""
        meta_tags = {}
        try:
            for meta in soup.find_all('meta'):
                name = meta.get('name') or meta.get('property') or meta.get('charset')
                content = meta.get('content', '')
                if name:
                    meta_tags[name] = content
        except Exception as e:
            prints(f"{M2}Error extracting meta tags: {str(e)}")
        return meta_tags

    def get_scripts(self, url, soup):
        """Extract all scripts"""
        scripts = []
        try:
            for script in soup.find_all('script', src=True):
                src = script['src']
                if src and src.strip():
                    full_url = urllib.parse.urljoin(url, src)
                    scripts.append({
                        'src': full_url,
                        'type': script.get('type', 'text/javascript')
                    })
        except Exception as e:
            prints(f"{M2}Error extracting scripts: {str(e)}")
        return scripts

    def get_stylesheets(self, url, soup):
        """Extract all CSS files"""
        stylesheets = []
        try:
            for link in soup.find_all('link', rel='stylesheet'):
                href = link.get('href', '')
                if href and href.strip():
                    full_url = urllib.parse.urljoin(url, href)
                    stylesheets.append(full_url)
        except Exception as e:
            prints(f"{M2}Error extracting stylesheets: {str(e)}")
        return stylesheets

    def get_page_text(self, soup):
        """Extract clean text from page"""
        try:
            # Remove script and style elements
            for script in soup(["script", "style", "meta", "link", "noscript"]):
                script.decompose()
            return soup.get_text(separator='\n', strip=True)
        except Exception as e:
            prints(f"{M2}Error extracting text: {str(e)}")
            return ""

    def scrape_url(self, url, options):
        """Main scraping function"""
        try:
            # Extract domain from URL
            parsed_url = urllib.parse.urlparse(url)
            self.domain = parsed_url.netloc
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                transient=True,
            ) as progress:
                task = progress.add_task(f"[{color_text.strip('[]#')}]Scraping {url}...", total=100)
                
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
                    'content_type': response.headers.get('content-type', 'unknown'),
                    'content_length': len(response.content),
                    'scrape_time': datetime.now().isoformat()
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
                
        except requests.exceptions.RequestException as e:
            return None, f"Network Error: {str(e)}"
        except Exception as e:
            return None, f"Error: {str(e)}"

# ----------[ MENU BOT ]---------- #
class botdata:
    def menu(self):
        """Main menu"""
        banner()
        prints(
            Panel(
                f"""{P2}[{color_text}01{P2}]. Advanced Web Scraper
{P2}[{color_text}02{P2}]. Multi-URL Scraper
{P2}[{color_text}03{P2}]. Form Data Extractor
{P2}[{color_text}04{P2}]. Content Analyzer
{P2}[{color_text}00{P2}]. Exit""",
                width=80,
                style=color_panel,
            )
        )
        menu = console.input(f" {H2}• {P2}pilih menu : ")
        if menu in ["01", "1"]:
            AdvancedWebScraperMenu().main_menu()
        elif menu in ["02", "2"]:
            MultiURLScraper().scrape_multiple()
        elif menu in ["03", "3"]:
            GetDataWeb()
        elif menu in ["04", "4"]:
            ContentAnalyzer().analyze()
        elif menu in ["00", "0"]:
            prints(Panel(f"{H2}Terima kasih telah menggunakan tool ini!", width=80, style=color_panel))
            sys.exit(0)
        else:
            prints(Panel(f"{M2}🙏 Masukan Yang Bener Tolol", width=80, style=color_panel))
            input(f" {H2}• {P2}Tekan Enter untuk melanjutkan...")
            self.menu()

class AdvancedWebScraperMenu:
    def __init__(self):
        self.scraper = AdvancedWebScraper()

    def main_menu(self):
        banner()
        prints(Panel(f"{H2}Advanced Web Scraper - Pilih Opsi Scraping", width=80, style=color_panel))
        
        url = console.input(f" {H2}• {P2}Masukan URL (contoh: https://example.com): ").strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        prints(
            Panel(
                f"""{P2}[{color_text}01{P2}]. All Content
{P2}[{color_text}02{P2}]. Links Only
{P2}[{color_text}03{P2}]. Images Only  
{P2}[{color_text}04{P2}]. Forms Only
{P2}[{color_text}05{P2}]. Meta Tags Only
{P2}[{color_text}06{P2}]. Custom Selection
{P2}[{color_text}00{P2}]. Kembali ke Menu Utama""",
                width=80,
                style=color_panel,
            )
        )
        
        choice = console.input(f" {H2}• {P2}Pilih opsi : ")
        
        if choice in ["00", "0"]:
            botdata().menu()
            return
        
        options_map = {
            '1': ['links', 'images', 'forms', 'meta', 'scripts', 'styles', 'text'],
            '2': ['links'],
            '3': ['images'],
            '4': ['forms'],
            '5': ['meta'],
            '6': self.custom_selection()
        }
        
        options = options_map.get(choice, ['links', 'images', 'forms'])
        if options:  # Only proceed if options is not empty
            self.display_results(url, options)
        else:
            self.main_menu()

    def custom_selection(self):
        """Allow user to select custom scraping options"""
        banner()
        prints(Panel(f"{H2}Pilih elemen yang ingin di-scrape:", width=80, style=color_panel))
        options = []
        
        choices = [
            ('links', 'Scrape links? (y/n): '),
            ('images', 'Scrape images? (y/n): '),
            ('forms', 'Scrape forms? (y/n): '),
            ('meta', 'Scrape meta tags? (y/n): '),
            ('scripts', 'Scrape scripts? (y/n): '),
            ('styles', 'Scrape stylesheets? (y/n): '),
            ('text', 'Scrape text content? (y/n): ')
        ]
        
        for option, prompt in choices:
            if console.input(f" {H2}• {P2}{prompt}").lower() == 'y':
                options.append(option)
        
        return options

    def display_results(self, url, options):
        """Display scraping results"""
        result, error = self.scraper.scrape_url(url, options)
        
        if error:
            prints(Panel(f"{M2}Error: {error}", width=80, style=color_panel))
            input(f" {H2}• {P2}Tekan Enter untuk melanjutkan...")
            self.main_menu()
            return

        # Display results in organized panels
        prints(Panel(f"{H2}Scraping Results for: {url}", width=80, style=color_panel))
        prints(Panel(f"{B2}Title: {P2}{result.get('title', 'N/A')}", width=80, style=color_panel))
        prints(Panel(f"{B2}Status Code: {P2}{result.get('status_code', 'N/A')}", width=80, style=color_panel))
        prints(Panel(f"{B2}Content Type: {P2}{result.get('content_type', 'N/A')}", width=80, style=color_panel))
        prints(Panel(f"{B2}Content Size: {P2}{result.get('content_length', 0)} bytes", width=80, style=color_panel))

        if 'links' in options and 'links' in result and result['links']:
            table = Table(title=f"{H2}Links Found (first 10)", show_header=True, header_style="bold magenta")
            table.add_column("Type", style="cyan", width=10)
            table.add_column("Text", style="white", width=30)
            table.add_column("URL", style="green", width=40)
            
            for link in result['links'][:10]:
                link_text = link['text'][:30] + "..." if len(link['text']) > 30 else link['text']
                link_url = link['url'][:40] + "..." if len(link['url']) > 40 else link['url']
                table.add_row(link['type'], link_text, link_url)
            
            console.print(table)
            prints(Panel(f"{K2}Total Links: {len(result['links'])}", width=80, style=color_panel))

        if 'images' in options and 'images' in result and result['images']:
            table = Table(title=f"{H2}Images Found (first 10)", show_header=True, header_style="bold magenta")
            table.add_column("Alt Text", style="cyan", width=30)
            table.add_column("Source", style="white", width=50)
            
            for img in result['images'][:10]:
                alt_text = img['alt'][:30] or "No alt"
                img_src = img['src'][:50] + "..." if len(img['src']) > 50 else img['src']
                table.add_row(alt_text, img_src)
            
            console.print(table)
            prints(Panel(f"{K2}Total Images: {len(result['images'])}", width=80, style=color_panel))

        if 'forms' in options and 'forms' in result and result['forms']:
            for i, form in enumerate(result['forms'][:5]):  # Show first 5 forms
                prints(Panel(f"{U2}Form {i+1}\n{B2}Action: {P2}{form['action']}\n{B2}Method: {P2}{form['method']}", 
                           width=80, style=color_panel))
                
                if form['inputs']:
                    table = Table(show_header=True, header_style="bold yellow")
                    table.add_column("Name", style="cyan", width=20)
                    table.add_column("Type", style="white", width=15)
                    table.add_column("Value/Options", style="green", width=40)
                    
                    for inp in form['inputs'][:10]:  # Show first 10 inputs
                        value = str(inp.get('value', ''))[:40]
                        if inp.get('type') == 'select':
                            value = f"{len(inp.get('options', []))} options"
                        table.add_row(inp.get('name', ''), inp.get('type', ''), value)
                    
                    console.print(table)
            
            prints(Panel(f"{K2}Total Forms: {len(result['forms'])}", width=80, style=color_panel))

        # Save results option
        save_choice = console.input(f" {H2}• {P2}Save results to file? (y/n): ").lower()
        if save_choice == 'y':
            filename = f"scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                prints(Panel(f"{H2}Results saved to: {filename}", width=80, style=color_panel))
            except Exception as e:
                prints(Panel(f"{M2}Error saving file: {str(e)}", width=80, style=color_panel))
        
        input(f" {H2}• {P2}Tekan Enter untuk melanjutkan...")
        self.main_menu()

class MultiURLScraper:
    def scrape_multiple(self):
        banner()
        prints(Panel(f"{H2}Multi-URL Scraper", width=80, style=color_panel))
        
        urls = []
        prints(f"{H2}• {P2}Masukkan URLs (ketik 'done' ketika selesai):")
        while True:
            url = console.input(f" {H2}→ {P2}URL: ").strip()
            if url.lower() == 'done':
                break
            if url:
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                urls.append(url)
        
        if not urls:
            prints(Panel(f"{M2}Tidak ada URL yang dimasukkan!", width=80, style=color_panel))
            input(f" {H2}• {P2}Tekan Enter untuk melanjutkan...")
            botdata().menu()
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
                        result, error = future.result(timeout=60)
                        if result:
                            results.append(result)
                        elif error:
                            prints(f"{M2}Error scraping {url}: {error}")
                        progress.update(task, advance=1)
                    except Exception as e:
                        prints(f"{M2}Error scraping {url}: {str(e)}")

        # Display summary
        if results:
            table = Table(title="Scraping Summary", show_header=True, header_style="bold magenta")
            table.add_column("No", style="cyan", width=5)
            table.add_column("URL", style="white", width=40)
            table.add_column("Title", style="green", width=30)
            table.add_column("Links", style="yellow", width=10)
            table.add_column("Status", style="red", width=12)
            
            for i, result in enumerate(results, 1):
                status = "✅ Success" if result.get('status_code') == 200 else f"❌ {result.get('status_code')}"
                table.add_row(
                    str(i),
                    result['url'][:40] + "..." if len(result['url']) > 40 else result['url'],
                    result.get('title', 'N/A')[:30] + "..." if len(result.get('title', '')) > 30 else result.get('title', 'N/A'),
                    str(len(result.get('links', []))),
                    status
                )
            
            console.print(table)
            
            # Save summary option
            save_choice = console.input(f" {H2}• {P2}Save summary to file? (y/n): ").lower()
            if save_choice == 'y':
                filename = f"multi_scrape_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(results, f, indent=2, ensure_ascii=False)
                    prints(Panel(f"{H2}Summary saved to: {filename}", width=80, style=color_panel))
                except Exception as e:
                    prints(Panel(f"{M2}Error saving file: {str(e)}", width=80, style=color_panel))
        else:
            prints(Panel(f"{M2}Tidak ada hasil yang berhasil di-scrape!", width=80, style=color_panel))
        
        input(f" {H2}• {P2}Tekan Enter untuk melanjutkan...")
        botdata().menu()

class ContentAnalyzer:
    def analyze(self):
        banner()
        prints(Panel(f"{H2}Content Analyzer", width=80, style=color_panel))
        
        url = console.input(f" {H2}• {P2}Masukan URL untuk dianalisis : ").strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        scraper = AdvancedWebScraper()
        result, error = scraper.scrape_url(url, ['text', 'meta', 'links', 'images'])
        
        if error:
            prints(Panel(f"{M2}Error: {error}", width=80, style=color_panel))
            input(f" {H2}• {P2}Tekan Enter untuk melanjutkan...")
            botdata().menu()
            return

        # Analyze content
        text = result.get('text', '')
        words = text.split()
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        # Count unique words
        unique_words = len(set(words))
        
        # Estimate reading time (average 200 words per minute)
        reading_time = len(words) / 200
        
        prints(Panel(f"{H2}Content Analysis Results for: {url}", width=80, style=color_panel))
        prints(Panel(f"{B2}Title: {P2}{result.get('title', 'N/A')}", width=80, style=color_panel))
        prints(Panel(f"{B2}Word Count: {P2}{len(words)}", width=80, style=color_panel))
        prints(Panel(f"{B2}Unique Words: {P2}{unique_words}", width=80, style=color_panel))
        prints(Panel(f"{B2}Sentence Count: {P2}{len(sentences)}", width=80, style=color_panel))
        prints(Panel(f"{B2}Character Count: {P2}{len(text)}", width=80, style=color_panel))
        prints(Panel(f"{B2}Estimated Reading Time: {P2}{reading_time:.1f} minutes", width=80, style=color_panel))
        prints(Panel(f"{B2}Links Found: {P2}{len(result.get('links', []))}", width=80, style=color_panel))
        prints(Panel(f"{B2}Images Found: {P2}{len(result.get('images', []))}", width=80, style=color_panel))
        prints(Panel(f"{B2}Meta Tags: {P2}{len(result.get('meta_tags', {}))}", width=80, style=color_panel))
        
        # Show most common meta tags
        if 'meta_tags' in result and result['meta_tags']:
            prints(Panel(f"{H2}Important Meta Tags:", width=80, style=color_panel))
            important_tags = ['description', 'keywords', 'author', 'viewport', 'title', 'og:title', 'og:description']
            for tag in important_tags:
                if tag in result['meta_tags']:
                    value = result['meta_tags'][tag]
                    if value:
                        prints(f"  {B2}{tag}: {P2}{value[:50]}{'...' if len(value) > 50 else ''}")
        
        input(f" {H2}• {P2}Tekan Enter untuk melanjutkan...")
        botdata().menu()

# -----------------------[ ORIGINAL FORM SCRAPER ]--------------------#
class GetDataWeb:
    def __init__(self):
        banner()
        prints(Panel(f"{H2}Masukkan URL yang ingin diambil source code-nya", width=80, style=color_panel))
        self.url = console.input(f" {H2}• {P2}Masukan URL : ").strip()
        if not self.url.startswith(('http://', 'https://')):
            self.url = 'https://' + self.url
        
        prints(
            Panel(
                f"""{P2}[{color_text}01{P2}]. Source Payload
{P2}[{color_text}02{P2}]. Parsed Payload 
{P2}[{color_text}03{P2}]. Source Code Post Requests
{P2}[{color_text}00{P2}]. Kembali ke Menu Utama""",
                width=80,
                style=color_panel,
            )
        )
        self.tanya = console.input(f" {H2}• {P2}pilih menu : ")
        
        if self.tanya in ["00", "0"]:
            botdata().menu()
            return
        
        try:
            parsed_url = urllib.parse.urlparse(self.url)
            self.domain = parsed_url.netloc
            self.get_form()
        except Exception as e:
            prints(Panel(f"{M2}Error: {str(e)}", width=80, style=color_panel))
            input(f" {H2}• {P2}Tekan Enter untuk melanjutkan...")
            botdata().menu()

    def get_form(self):
        """Fetch and process forms from URL"""
        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            req = session.get(self.url, timeout=30)
            if req.status_code != 200:
                prints(Panel(f"{M2}Error: HTTP {req.status_code}", width=80, style=color_panel))
                input(f" {H2}• {P2}Tekan Enter untuk melanjutkan...")
                botdata().menu()
                return
            
            raq = bs(req.content, "html.parser")
            forms = raq.find_all("form")
            
            if not forms:
                prints(Panel(f"{M2}Tidak ada form ditemukan di halaman ini", width=80, style=color_panel))
                input(f" {H2}• {P2}Tekan Enter untuk melanjutkan...")
                botdata().menu()
                return
            
            for x in forms:
                if self.tanya in ["1", "01"]:
                    self.printing1(session, req, x)
                elif self.tanya in ["2", "02"]:
                    self.printing2(session, req, x)
                elif self.tanya in ["3", "03"]:
                    self.printing3(session, req, x)
                else:
                    prints(Panel(f"{M2}Pilihan tidak valid", width=80, style=color_panel))
                    break
                
                # Ask if user wants to see next form
                if len(forms) > 1:
                    next_form = console.input(f" {H2}• {P2}Lihat form berikutnya? (y/n): ").lower()
                    if next_form != 'y':
                        break
            
            input(f" {H2}• {P2}Tekan Enter untuk melanjutkan...")
            botdata().menu()
            
        except requests.exceptions.RequestException as e:
            prints(Panel(f"{M2}Network Error: {str(e)}", width=80, style=color_panel))
            input(f" {H2}• {P2}Tekan Enter untuk melanjutkan...")
            botdata().menu()

    def get_head1(self, req):
        """Extract headers"""
        data = {}
        head = req.headers
        usls = ["cookie", "set-cookie", "report-to", "expires", "x-fb-debug", "date", "last-modified", "etag"]
        for x, y in head.items():
            if x.lower() not in usls:
                data[x] = y
        return data

    def get_data1(self, form):
        """Extract form data as dictionary"""
        data = {}
        for y in form.find_all("input"):
            if y.get("name"):
                data[y["name"]] = y.get("value", "")
        return data

    def get_data2(self, form):
        """Extract form elements"""
        return form.find_all("input")

    def get_post1(self, form):
        """Get form action URL"""
        z = form.get("action", "")
        if z.startswith(("https://", "http://")):
            return z
        elif z.startswith("/"):
            return f"https://{self.domain}{z}"
        else:
            return self.url

    def printing1(self, session, req, x):
        """Print source payload"""
        head = self.get_head1(req)
        data = self.get_data1(x)
        post = self.get_post1(x)
        coki = session.cookies.get_dict()
        
        prints(Panel(f"{P2}[Source Payload]", width=80, style=color_panel))
        prints(Panel(f"{P2}[HOST]{H2} {self.domain}", width=80, style=color_panel))
        prints(Panel(f"{P2}[Headers]{H2} {json.dumps(head, indent=2)}", width=80, style=color_panel))
        prints(Panel(f"{P2}[Data]{H2} {json.dumps(data, indent=2)}", width=80, style=color_panel))
        prints(Panel(f"{P2}[Cookies]{H2} {json.dumps(coki, indent=2)}", width=80, style=color_panel))
        prints(Panel(f"{P2}[Action URL]{H2} {post}", width=80, style=color_panel))

    def printing2(self, session, req, x):
        """Print parsed payload"""
        head = self.get_head1(req)
        data = self.get_data2(x)
        post = self.get_post1(x)
        coki = session.cookies.get_dict()
        
        prints(Panel(f"{P2}[Parsed Payload]", width=80, style=color_panel))
        prints(f"\n{P2}headers = {json.dumps(head, indent=2)}")
        prints(f"\n{P2}data = {{")
        for y in data:
            name = y.get("name", "")
            value = y.get("value", "")
            if name:  # Only show inputs with names
                prints(f"    '{name}': '{value}',")
        prints("}")
        prints(f"\n{P2}cookies = {json.dumps(coki, indent=2)}")
        prints(f"\n{P2}action_url = '{post}'")

    def printing3(self, session, req, x):
        """Print source code for POST requests"""
        head = self.get_head1(req)
        data = self.get_data2(x)
        post = self.get_post1(x)
        coki = session.cookies.get_dict()
        
        prints(Panel(f"{P2}[Source Code for POST Request]", width=80, style=color_panel))
        prints(f"\n{P2}import requests")
        prints(f"\n{P2}url = '{self.url}'")
        prints(f"{P2}response = requests.get(url)")
        prints(f"{P2}soup = BeautifulSoup(response.content, 'html.parser')")
        prints(f"\n{P2}headers = {json.dumps(head, indent=2)}")
        prints(f"\n{P2}data = {{")
        for y in data:
            name = y.get("name", "")
            value = y.get("value", "(.*?)")
            if name:
                prints(f"    '{name}': '{value}',")
        prints("}")
        prints(f"\n{P2}cookies = {json.dumps(coki, indent=2)}")
        prints(f"\n{P2}action_url = '{post}'")
        prints(f"\n{P2}# Example POST request:")
        prints(f"{P2}post_response = requests.post(action_url, headers=headers, data=data, cookies=cookies)")
        prints(f"{P2}print(post_response.text)")

# -----------------------[ SYSTEM-CONTROL ]--------------------#
if __name__ == "__main__":
    # Create data directory if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Create default theme file if it doesn't exist
    theme_file = "data/theme_color"
    if not os.path.exists(theme_file):
        try:
            with open(theme_file, "w") as f:
                f.write("[#00FF00]|#00FF00")
        except:
            pass
    
    try:
        botdata().menu()
    except KeyboardInterrupt:
        prints(f"\n\n{M2}Program dihentikan oleh pengguna")
        sys.exit(0)
    except Exception as e:
        prints(f"\n\n{M2}Error: {str(e)}")
        input("Tekan Enter untuk keluar...")
        sys.exit(1)
