import requests
import socket
import dns.resolver
import sys
import json
import csv
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings()

TIMEOUT = 5
THREADS = 30


def resolve_domain(domain):
    try:
        answers = dns.resolver.resolve(domain, 'A')
        return [rdata.to_text() for rdata in answers]
    except:
        return []


def get_title(html):
    try:
        soup = BeautifulSoup(html, "html.parser")
        return soup.title.string.strip() if soup.title else ""
    except:
        return ""


def check_domain(domain):
    domain = domain.strip()
    if not domain:
        return None

    ips = resolve_domain(domain)
    if not ips:
        print(f"[-] DNS FAIL: {domain}")
        return None

    urls = [f"http://{domain}", f"https://{domain}"]

    for url in urls:
        try:
            r = requests.get(url, timeout=TIMEOUT, verify=False)

            title = get_title(r.text)
            server = r.headers.get("Server", "")

            result = {
                "domain": domain,
                "url": url,
                "status": r.status_code,
                "title": title,
                "server": server,
                "ips": ips
            }

            print(f"[+] {domain} | {r.status_code} | {title}")

            return result

        except requests.RequestException:
            continue

    print(f"[-] INATIVO: {domain}")
    return None


def save_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def save_csv(data, filename):
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["domain", "url", "status", "title", "server", "ips"])
        writer.writeheader()
        for row in data:
            row["ips"] = ",".join(row["ips"])
            writer.writerow(row)


def main(input_file):
    with open(input_file, "r") as f:
        domains = f.readlines()

    results = []

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = executor.map(check_domain, domains)

    for r in futures:
        if r:
            results.append(r)

    print(f"\n🔥 Total ativos: {len(results)}")

    save_json(results, "ativos.json")
    save_csv(results, "ativos.csv")

    print("[+] Salvo em ativos.json e ativos.csv")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} lista.txt")
        sys.exit(1)

    main(sys.argv[1])
