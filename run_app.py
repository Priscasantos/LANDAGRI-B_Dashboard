import subprocess
import sys
import os
import argparse

def run_streamlit_app(no_cache_flag: bool):
    env = os.environ.copy()
    if no_cache_flag:
        env["STREAMLIT_SMART_CACHE_DISABLED"] = "True"
        print("INFO: Attempting to run Streamlit with @smart_cache_data disabled.")
    
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], env=env)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the LULC Dashboard Streamlit application.")
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Run the application with @smart_cache_data effectively disabled for this session."
    )
    args = parser.parse_args()
    run_streamlit_app(no_cache_flag=args.no_cache)