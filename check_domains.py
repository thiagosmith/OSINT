import requests
import sys
from concurrent.futures import ThreadPoolExecutor

# evita warning de SSL
requests.packages.urllib3.disable_warnings()

def check_domain(domain):
    domain = domain.strip()

    if not domain:
        return None

    urls = [
        f"http://{domain}",
        f"https://{domain}"
    ]

    for url in urls:
        try:
            r = requests.get(url, timeout=5, verify=False)
            if r.status_code < 400:
                print(f"[+] ATIVO: {domain}")
                return domain
        except requests.RequestException:
            continue

    print(f"[-] INATIVO: {domain}")
    return None


def main(input_file, output_file=None):
    with open(input_file, "r") as f:
        domains = f.readlines()

    ativos = []

    # threads para acelerar
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(check_domain, domains)

    for result in results:
        if result:
            ativos.append(result)

    print("\n===== DOMÍNIOS ATIVOS =====")
    for d in ativos:
        print(d)

    if output_file:
        with open(output_file, "w") as f:
            for d in ativos:
                f.write(d + "\n")

        print(f"\n[+] Salvo em: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} lista.txt [saida.txt]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    main(input_file, output_file)
