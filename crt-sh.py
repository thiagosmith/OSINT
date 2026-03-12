#!/usr/bin/env python3
import sys
import requests
from bs4 import BeautifulSoup
# pip install requests beautifulsoup4
def main():
    if len(sys.argv) != 2:
        print(f"Uso: python {sys.argv[0]} dominio.com")
        sys.exit(1)

    dominio = sys.argv[1]
    url = f"https://crt.sh/?q={dominio}"

    # Faz a requisição
    response = requests.get(url)
    if response.status_code != 200:
        print("Erro ao acessar crt.sh")
        sys.exit(1)

    # Faz o parse do HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # Encontra todas as tabelas
    tables = soup.find_all("table")

    # Normalmente a tabela de resultados é a última
    if not tables:
        print("Nenhuma tabela encontrada.")
        sys.exit(1)

    table = tables[-1]
    rows = table.find_all("tr")

    identities = set()
    for row in rows[1:]:  # pula cabeçalho
        cols = row.find_all("td")
        if len(cols) >= 5:  # coluna "Matching Identities" costuma ser a 5ª
            identity = cols[4].get_text(strip=True)
            if identity:
                identities.add(identity)

    # Ordena e mostra
    for identity in sorted(identities):
        print(identity)

if __name__ == "__main__":
    main()
