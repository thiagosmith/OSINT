#!/usr/bin/env python3
import sys
from ddgs import DDGS

def main():
    if len(sys.argv) < 2:
        print("Uso: python searcher.py <termo>")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    print(f"Resultados para: {query}\n")

    # Retorna apenas os links
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=10):
            print(r['href'])

if __name__ == "__main__":
    main()

