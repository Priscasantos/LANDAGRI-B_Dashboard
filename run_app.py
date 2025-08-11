import argparse
import os
import subprocess
import sys


def check_dependencies():
    """
    Verifica se o pacote 'streamlit' está instalado.
    Caso não esteja, exibe uma mensagem de erro em pt-BR e encerra o programa.
    """
    try:
        import streamlit  # noqa: F401
    except ImportError:
        print(
            "[ERRO] O pacote 'streamlit' não está instalado. Instale com: pip install streamlit"
        )
        sys.exit(1)


def run_streamlit_app(no_cache_flag: bool, port: int):
    """
    Executa o aplicativo Streamlit com opções de auto-reload e cache.
    Mensagens e comentários em pt-BR conforme diretrizes gerais.
    """
    env = os.environ.copy()
    if no_cache_flag:
        env["STREAMLIT_SMART_CACHE_DISABLED"] = "True"
        print("[INFO] Rodando Streamlit com @smart_cache_data desabilitado.")

    # Comando para auto-reload automático quando arquivos forem alterados
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app.py",
        "--server.port",
        str(port),
        "--server.fileWatcherType",
        "auto",  # Detecta alterações automaticamente
        "--server.runOnSave",
        "true",  # Executa novamente ao salvar
        "--client.toolbarMode",
        "developer",  # Modo desenvolvedor
        "--server.allowRunOnSave",
        "true",  # Permite execução automática ao salvar
    ]
    print(f"[INFO] Executando com auto-reload: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERRO] Falha ao executar o Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("[INFO] Execução interrompida pelo usuário.")
        sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Executa o aplicativo Streamlit do Dashboard LULC."
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Executa o aplicativo com @smart_cache_data desabilitado nesta sessão.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Porta para executar o Streamlit (padrão: 8501)",
    )
    args = parser.parse_args()
    check_dependencies()
    print(f"[INFO] Acesse o dashboard em: http://localhost:{args.port}")
    run_streamlit_app(no_cache_flag=args.no_cache, port=args.port)
