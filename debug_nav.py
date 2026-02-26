"""Debug script: explore post-login links to find Notenspiegel path."""

import os

import requests
from bs4 import BeautifulSoup

session = requests.Session()

# Get login page, follow meta refresh
resp = session.get("https://lsf.uni-hildesheim.de/")
soup = BeautifulSoup(resp.text, "html.parser")
meta = soup.find("meta", attrs={"http-equiv": "refresh"})
redir = "https://lsf.uni-hildesheim.de" + meta["content"].split("URL=")[1]
resp = session.get(redir)

# Login
soup = BeautifulSoup(resp.text, "html.parser")
form = soup.find("form")
data = {}
for inp in form.find_all("input"):
    t = (inp.get("type") or "").lower()
    n = inp.get("name")
    if not n:
        continue
    if t in ("hidden", "submit"):
        data[n] = inp.get("value", "")
data["asdf"] = os.environ["LSF_USERNAME"]
data["fdsa"] = os.environ["LSF_PASSWORD"]

resp = session.post(form["action"], data=data)
print(f"Post-login URL: {resp.url}\n")

# Find grade-related links
soup = BeautifulSoup(resp.text, "html.parser")
keywords = ["noten", "prüf", "leistung", "pruef", "ergebnis"]
print("=== Grade-related links ===")
for a in soup.find_all("a", href=True):
    txt = a.get_text(strip=True)
    combined = (txt + a["href"]).lower()
    if any(k in combined for k in keywords):
        print(f"  [{txt}] -> {a['href']}")

print("\n=== All sidebar/menu links ===")
for a in soup.find_all("a", href=True):
    txt = a.get_text(strip=True)
    if txt and len(txt) < 80:
        print(f"  [{txt}] -> {a['href']}")
