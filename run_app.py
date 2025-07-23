import argparse
import os
import subprocess
import sys


def check_dependencies():
    try:
        import streamlit  # noqa: F401
    except ImportError:
        print(
            "[ERRO] O pacote 'streamlit' não está instalado. Instale com: pip install streamlit"
        )
        sys.exit(1)


def run_streamlit_app(no_cache_flag: bool, port: int):
    env = os.environ.copy()
    if no_cache_flag:
        env["STREAMLIT_SMART_CACHE_DISABLED"] = "True"
        print("INFO: Rodando Streamlit com @smart_cache_data desabilitado.")

    # Comandos para auto-reload automático quando arquivos mudarem
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app.py",
        "--server.port",
        str(port),
        "--server.fileWatcherType",
        "auto",  # Auto-detecta mudanças nos arquivos
        "--server.runOnSave",
        "true",  # Executa novamente quando salvar
        "--client.toolbarMode",
        "developer",  # Modo desenvolvedor
        "--server.allowRunOnSave",
        "true",  # Permite execução automática ao salvar
    ]
    print(f"[INFO] Executando com auto-reload: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERRO] Falha ao rodar Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("[INFO] Execução interrompida pelo usuário.")
        sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the LULC Dashboard Streamlit application."
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Run the application with @smart_cache_data effectively disabled for this session.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Porta para rodar o Streamlit (padrão: 8501)",
    )
    args = parser.parse_args()
    check_dependencies()
    print(f"[INFO] Acesse o dashboard em: http://localhost:{args.port}")
    run_streamlit_app(no_cache_flag=args.no_cache, port=args.port)
