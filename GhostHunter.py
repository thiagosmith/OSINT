import subprocess
import argparse
import os
from typing import List

def run_command(command: List[str], description: str) -> str:
    """Executa um comando shell e captura a saída, tratando erros."""
    print(f"[*] Iniciando {description}...")
    try:
        # Executa o comando. capture_output=True captura stdout e stderr.
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=True, 
            encoding='utf-8'
        )
        print(f"[+] {description} concluído com sucesso.")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[!!!] ERRO ao executar {description}:")
        print(f"       Comando: {' '.join(e.cmd)}")
        print(f"       Stderr: {e.stderr}")
        return ""
    except FileNotFoundError:
        print(f"[!!!] ERRO CRÍTICO: O executável não foi encontrado. Verifique se '{command[0]}' está no seu PATH.")
        return ""

def process_targets(targets: List[str], output_dir: str):
    """Processa cada alvo, rodando as 3 ferramentas e consolidando os resultados."""
    
    all_targets_results = {}

    for domain in targets:
        print("\n" + "="*70)
        print(f"=== PROCESSANDO ALVO: {domain} ===")
        print("="*70)
        
        # Diretórios de saída específicos para cada alvo
        target_dir = os.path.join(output_dir, domain)
        os.makedirs(target_dir, exist_ok=True)
        
        # --- 1. AMASS ---
        # Execução passiva, salvando resultado no diretório do alvo
        amass_cmd = [
            "amass", "enum", "-d", domain, "-passive", 
            "-o", os.path.join(target_dir, "amass_results.txt")
        ]
        run_command(amass_cmd, "AMASS (Passivo)")

        # --- 2. SUBFINDER ---
        subfinder_cmd = [
            "subfinder", "-d", domain, "-silent", 
            "-o", os.path.join(target_dir, "subfinder_results.txt")
        ]
        run_command(subfinder_cmd, "Subfinder")

        # --- 3. ASSETFINDER ---
        assetfinder_cmd = [
            "assetfinder", "--subs-only", domain, 
            "-o", os.path.join(target_dir, "assetfinder_results.txt")
        ]
        run_command(assetfinder_cmd, "Assetfinder")
        
        all_targets_results[domain] = target_dir


def consolidate_results(base_dir: str):
    """Compara todos os arquivos de saída e cria o resultado final sem duplicatas."""
    print("\n" + "*"*70)
    print(">>> INICIANDO FASE DE CONSOLIDAÇÃO E REMOÇÃO DE DUPLICATAS <<<")
    print("*"*70)
    
    final_set = set()
    
    # Itera sobre todos os diretórios de alvo gerados
    for target_dir_name in os.listdir(base_dir):
        target_dir_path = os.path.join(base_dir, target_dir_name)
        
        if not os.path.isdir(target_dir_path):
            continue

        print(f"\n--- Processando dados para o alvo: {target_dir_name} ---")
        
        # Caminhos dos arquivos de saída
        files_to_read = [
            os.path.join(target_dir_path, "amass_results.txt"),
            os.path.join(target_dir_path, "subfinder_results.txt"),
            os.path.join(target_dir_path, "assetfinder_results.txt")
        ]
        
        # Lê todos os arquivos e adiciona os domínios ao conjunto (set)
        for file_path in files_to_read:
            if os.path.exists(file_path):
                print(f"  -> Lendo {os.path.basename(file_path)}...")
                try:
                    with open(file_path, 'r') as f:
                        for line in f:
                            domain = line.strip()
                            if domain:
                                final_set.add(domain)
                except Exception as e:
                    print(f"  [!!!] Falha ao ler arquivo {file_path}: {e}")

    # Salva o conjunto único de domínios
    final_output_path = os.path.join(base_dir, "analise_final.txt")
    with open(final_output_path, 'w') as f:
        for domain in sorted(list(final_set)):
            f.write(domain + '\n')
            
    print("\n" + "#"*70)
    print(">>> FASE DE CONSOLIDAÇÃO CONCLUÍDA <<<")
    print(f"Total de domínios únicos coletados: {len(final_set)}")
    print(f"Arquivo final de inteligência salvo em: {final_output_path}")
    print("#"*70)


def main():
    parser = argparse.ArgumentParser(
        description="GhostHunter: Pipeline de Reconhecimento Passivo Unificado.",
        epilog="ATENÇÃO: Este script depende de amass, subfinder e assetfinder estarem instalados e acessíveis no PATH."
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--domain", type=str, help="Domínio alvo único (e.g., example.com).")
    group.add_argument("-w", "--whitelist", type=str, help="Arquivo contendo uma lista de domínios, um por linha (e.g., list.txt).")
    
    args = parser.parse_args()
    
    # Define o diretório base para salvar todos os resultados
    base_output_dir = "recon_output"
    os.makedirs(base_output_dir, exist_ok=True)
    
    target_list = []
    if args.domain:
        target_list = [args.domain]
        
    elif args.whitelist:
        try:
            with open(args.whitelist, 'r') as f:
                # Filtra linhas vazias e remove espaços em branco
                target_list = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"[!!!] Arquivo de whitelist não encontrado: {args.whitelist}")
            return

    if not target_list:
        print("[!!!] Nenhum alvo fornecido. Encerrando.")
        return

    # 1. Execução das ferramentas para cada alvo
    process_targets(target_list, base_output_dir)
    
    # 2. Consolidação de todos os resultados de todos os alvos processados
    consolidate_results(base_output_dir)


if __name__ == "__main__":
    main()
