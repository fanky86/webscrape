# 🕸️ Web Scraping Python

A simple Python web scraping project using **BeautifulSoup 4** and **Requests**, compatible with Debian and Ubuntu Linux.

## ✨ Features

- Extract HTML content from websites.
- Parse HTML using BeautifulSoup 4.
- Send HTTP requests using Requests.
- Compatible with Debian and Ubuntu.
- Uses Python virtual environments (`venv`).
- Avoids system-wide Python package conflicts (PEP 668).

## 📋 Requirements

- Debian or Ubuntu Linux
- Python 3
- Python virtual environment support
- Internet connection

## 🚀 Installation

### 1. Clone the repository

Replace `YOUR_USERNAME` with your GitHub username and `YOUR_REPOSITORY` with your repository name.

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

### 2. Install system dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-full git
```

### 3. Create a virtual environment

```bash
python3 -m venv .venv
```

### 4. Activate the virtual environment

```bash
source .venv/bin/activate
```

### 5. Install Python dependencies

```bash
python -m pip install --upgrade pip
python -m pip install beautifulsoup4 requests
```

Alternatively, if the repository includes a `requirements.txt` file:

```bash
python -m pip install -r requirements.txt
```

## 📁 Project Structure

```text
webscrape/
├── .venv/              # Local Python virtual environment
├── scrape.py           # Main scraping script
├── requirements.txt    # Python dependencies
├── .gitignore          # Git exclusions
└── README.md           # Project documentation
```

## 💻 Usage

Run the scraping script from the project directory:

```bash
source .venv/bin/activate
python scrape.py
```

### Example Code

```python
import requests
from bs4 import BeautifulSoup

url = "https://example.com"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    url,
    headers=headers,
    timeout=15
)

response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

if soup.title:
    print("Page title:", soup.title.get_text(strip=True))

for link in soup.find_all("a", href=True):
    print(link.get_text(strip=True), link["href"])
```

Save the example as `scrape.py` and execute it using Python.

## 📦 requirements.txt

Create a file named `requirements.txt`:

```text
beautifulsoup4
requests
```

Install dependencies with:

```bash
python -m pip install -r requirements.txt
```

## 🐧 Debian / Ubuntu Compatibility

This project is designed to work with Debian-based distributions that enforce Python package management restrictions through **PEP 668**.

If you encounter:

```text
error: externally-managed-environment
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install beautifulsoup4 requests
```

Do not install project dependencies directly into the system Python environment.

## 🔒 Security and Responsible Scraping

- Respect the target website's Terms of Service.
- Check `robots.txt` and applicable scraping policies.
- Avoid excessive requests that could overload a website.
- Use reasonable timeouts and request rates.
- Do not scrape private information or access-controlled content without authorization.
- Never commit API keys, passwords, session cookies, or other secrets.

## 🛠️ Troubleshooting

### `python3: command not found`

Install Python:

```bash
sudo apt update
sudo apt install -y python3
```

### `No module named venv`

Install virtual environment support:

```bash
sudo apt install -y python3-venv python3-full
```

### `No module named bs4`

Activate the virtual environment and install BeautifulSoup:

```bash
source .venv/bin/activate
python -m pip install beautifulsoup4
```

### `No module named requests`

```bash
source .venv/bin/activate
python -m pip install requests
```

### Leave the virtual environment

```bash
deactivate
```

## 📄 License

This project is available under the MIT License if a corresponding `LICENSE` file is included in the repository.

---

**Built with Python 🐍, Requests, and BeautifulSoup 4.**
