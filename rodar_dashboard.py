import os
import sys

# Ativa o ambiente virtual se existir
if os.path.exists('.venv'):
    if sys.platform == 'win32':
        activate_script = os.path.join('.venv', 'Scripts', 'activate_this.py')
        if os.path.exists(activate_script):
            exec(open(activate_script).read(), {'__file__': activate_script})

# Executa o Streamlit
os.system('streamlit run app.py')
