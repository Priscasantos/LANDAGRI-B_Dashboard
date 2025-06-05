# -*- coding: utf-8 -*-
"""
Scripts de Instalação - Windows/Linux
====================================

Este script cria os arquivos de instalação automática para Windows (.bat) 
e Linux/Mac (.sh) do software de comparação de iniciativas LULC.

Autor: Análise Comparativa de Iniciativas LULC
Data: 2024
"""

import os

def create_windows_installer():
    """
    Cria o script de instalação para Windows (.bat).
    """
    
    bat_content = '''@echo off
chcp 65001 > nul
echo.
echo 🌍 Instalador do Comparador de Iniciativas LULC - Windows
echo ========================================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Por favor, instale Python 3.8 ou superior.
    echo    Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python encontrado:
python --version

REM Verificar se pip está instalado
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip não encontrado. Por favor, reinstale Python com pip.
    pause
    exit /b 1
)

echo ✅ pip encontrado:
python -m pip --version
echo.

REM Criar ambiente virtual
echo 🏗️ Criando ambiente virtual...
if exist "lulc_env" (
    echo ⚠️ Ambiente virtual já existe, removendo...
    rmdir /s /q "lulc_env"
)

python -m venv lulc_env
if errorlevel 1 (
    echo ❌ Erro ao criar ambiente virtual
    pause
    exit /b 1
)

echo ✅ Ambiente virtual criado com sucesso!

REM Ativar ambiente virtual e instalar dependências
echo.
echo 📦 Ativando ambiente virtual e instalando dependências...
call lulc_env\\Scripts\\activate.bat

python -m pip install --upgrade pip
if errorlevel 1 (
    echo ❌ Erro ao atualizar pip
    pause
    exit /b 1
)

python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Erro ao instalar dependências
    echo Verifique se o arquivo requirements.txt existe
    pause
    exit /b 1
)

echo.
echo ✅ Instalação concluída com sucesso!
echo.
echo 🚀 Para executar o aplicativo:
echo    1. Ative o ambiente virtual: lulc_env\\Scripts\\activate.bat
echo    2. Execute: streamlit run app.py
echo.
echo 💡 Ou execute o arquivo run_app.bat
echo.

REM Criar script de execução
echo @echo off > run_app.bat
echo call lulc_env\\Scripts\\activate.bat >> run_app.bat
echo streamlit run app.py >> run_app.bat
echo pause >> run_app.bat

echo ✅ Script de execução 'run_app.bat' criado!

pause
'''
    
    try:
        with open('install.bat', 'w', encoding='utf-8') as f:
            f.write(bat_content)
        print("✅ Arquivo install.bat criado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar install.bat: {e}")
        return False

def create_linux_installer():
    """
    Cria o script de instalação para Linux/Mac (.sh).
    """
    
    sh_content = '''#!/bin/bash

echo ""
echo "🌍 Instalador do Comparador de Iniciativas LULC - Linux/Mac"
echo "=========================================================="
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.8 ou superior."
    echo "   Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    echo "   CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "   macOS: brew install python3"
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Verificar se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Instalando..."
    if command -v apt &> /dev/null; then
        sudo apt install python3-pip
    elif command -v yum &> /dev/null; then
        sudo yum install python3-pip
    elif command -v brew &> /dev/null; then
        brew install python3
    else
        echo "❌ Não foi possível instalar pip automaticamente."
        echo "   Por favor, instale pip3 manualmente."
        exit 1
    fi
fi

echo "✅ pip encontrado: $(pip3 --version)"
echo ""

# Criar ambiente virtual
echo "🏗️ Criando ambiente virtual..."
if [ -d "lulc_env" ]; then
    echo "⚠️ Ambiente virtual já existe, removendo..."
    rm -rf lulc_env
fi

python3 -m venv lulc_env
if [ $? -ne 0 ]; then
    echo "❌ Erro ao criar ambiente virtual"
    echo "   Talvez precise instalar python3-venv:"
    echo "   Ubuntu/Debian: sudo apt install python3-venv"
    exit 1
fi

echo "✅ Ambiente virtual criado com sucesso!"

# Ativar ambiente virtual e instalar dependências
echo ""
echo "📦 Ativando ambiente virtual e instalando dependências..."
source lulc_env/bin/activate

python -m pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo "❌ Erro ao atualizar pip"
    exit 1
fi

python -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependências"
    echo "Verifique se o arquivo requirements.txt existe"
    exit 1
fi

echo ""
echo "✅ Instalação concluída com sucesso!"
echo ""
echo "🚀 Para executar o aplicativo:"
echo "   1. Ative o ambiente virtual: source lulc_env/bin/activate"
echo "   2. Execute: streamlit run app.py"
echo ""
echo "💡 Ou execute o arquivo run_app.sh"
echo ""

# Criar script de execução
cat > run_app.sh << 'EOF'
#!/bin/bash
source lulc_env/bin/activate
streamlit run app.py
EOF

chmod +x run_app.sh

echo "✅ Script de execução 'run_app.sh' criado!"
echo ""
echo "🎉 Instalação completa! Divirta-se explorando as iniciativas LULC!"
'''
    
    try:
        with open('install.sh', 'w', encoding='utf-8') as f:
            f.write(sh_content)
        
        # Tornar o arquivo executável no Linux/Mac
        try:
            os.chmod('install.sh', 0o755)
        except:
            pass  # Pode falhar no Windows, mas não é problema
        
        print("✅ Arquivo install.sh criado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar install.sh: {e}")
        return False

def create_readme_file():
    """
    Cria um arquivo README.md atualizado com instruções de instalação.
    """
    
    readme_content = '''# 🌍 Comparador de Iniciativas LULC

Software interativo para análise comparativa de iniciativas globais e brasileiras de mapeamento de cobertura e uso da terra (Land Use Land Cover - LULC).

## 📋 Sobre o Projeto

Este software permite explorar e comparar 14 principais iniciativas de mapeamento LULC, incluindo:

### 🌍 Iniciativas Globais
- Copernicus Global Land Cover Service (CGLS)
- Dynamic World (GDW)
- ESRI-10m Annual LULC
- FROM-GLC
- WorldCover 10m 2021
- Land Cover CCI
- MODIS Land Cover
- GLC_FCS30

### 🇧🇷 Iniciativas Brasileiras
- MapBiomas Brasil
- PRODES Amazônia
- DETER Amazônia
- PRODES Cerrado
- TerraClass Amazônia
- IBGE Monitoramento

## 🚀 Instalação Rápida

### Windows
```bash
# Clone ou baixe o projeto
# Execute o instalador automático
install.bat
```

### Linux/Mac
```bash
# Clone ou baixe o projeto
# Torne o instalador executável e execute
chmod +x install.sh
./install.sh
```

## 📦 Instalação Manual

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passos
1. **Clone o repositório ou baixe os arquivos**

2. **Crie um ambiente virtual**
   ```bash
   python -m venv lulc_env
   ```

3. **Ative o ambiente virtual**
   
   Windows:
   ```bash
   lulc_env\\Scripts\\activate
   ```
   
   Linux/Mac:
   ```bash
   source lulc_env/bin/activate
   ```

4. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

5. **Execute o aplicativo**
   ```bash
   streamlit run app.py
   ```

## 🖥️ Executando o Software

### Opção 1: Scripts automáticos
- **Windows:** Execute `run_app.bat`
- **Linux/Mac:** Execute `./run_app.sh`

### Opção 2: Comando manual
```bash
# Ative o ambiente virtual
source lulc_env/bin/activate  # Linux/Mac
# ou
lulc_env\\Scripts\\activate   # Windows

# Execute o aplicativo
streamlit run app.py
```

## 📊 Funcionalidades

### 🔍 Análise Interativa
- **Filtros dinâmicos:** Por tipo, resolução, acurácia e metodologia
- **Métricas principais:** Estatísticas resumidas das iniciativas
- **Visualizações:** Gráficos interativos com Plotly

### 📈 Visualizações Disponíveis
1. **Resolução vs Acurácia:** Scatter plot com análise de correlação
2. **Cobertura Temporal:** Timeline das iniciativas
3. **Distribuição de Classes:** Histogramas e gráficos de barras
4. **Metodologias:** Pizza e box plots por metodologia
5. **Heatmap de Características:** Matriz de comparação técnica

### ⚖️ Comparação Direta
- **Seleção de iniciativas:** Compare até duas iniciativas lado a lado
- **Gráfico radar:** Visualização normalizada de características
- **Tabela comparativa:** Detalhes técnicos lado a lado

### 🔍 Exploração Detalhada
- **Metadados completos:** Informações metodológicas detalhadas
- **Validação:** Processos de validação de cada iniciativa
- **Fontes de dados:** Sensores e dados utilizados

## 📁 Estrutura do Projeto

```
software-iniciativas/
├── app.py                    # Aplicativo principal Streamlit
├── generate_dataset.py       # Gerador do dataset CSV
├── generate_metadata.py      # Gerador dos metadados JSON
├── setup_dependencies.py     # Configuração de dependências
├── create_installers.py      # Criação dos scripts de instalação
├── initiatives_comparison.csv # Dataset das iniciativas
├── initiatives_metadata.json # Metadados detalhados
├── requirements.txt          # Dependências Python
├── install.bat              # Instalador Windows
├── install.sh               # Instalador Linux/Mac
├── run_app.bat              # Executor Windows
├── run_app.sh               # Executor Linux/Mac
└── README.md                # Este arquivo
```

## 🛠️ Dependências

- **streamlit** - Framework web para aplicações de dados
- **plotly** - Visualizações interativas
- **pandas** - Manipulação de dados
- **numpy** - Computação numérica
- **scikit-learn** - Normalização e análises

## 🔧 Regeneração dos Dados

Para regenerar os arquivos de dados:

```bash
# Gerar dataset CSV
python generate_dataset.py

# Gerar metadados JSON
python generate_metadata.py

# Configurar dependências
python setup_dependencies.py

# Criar instaladores
python create_installers.py
```

## 🌐 Acesso ao Aplicativo

Após executar `streamlit run app.py`, o aplicativo estará disponível em:
- **URL local:** http://localhost:8501
- **URL de rede:** http://[seu-ip]:8501

## 📧 Suporte

Para dúvidas ou problemas:
1. Verifique se todas as dependências estão instaladas
2. Confirme se o Python 3.8+ está sendo usado
3. Verifique se os arquivos CSV e JSON estão presentes

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos e de pesquisa.

---

🌍 **Desenvolvido para análise comparativa de sistemas de mapeamento LULC**
'''
    
    try:
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("✅ Arquivo README.md atualizado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar README.md: {e}")
        return False

def main():
    """Função principal para criar os scripts de instalação."""
    print("🛠️ Criador de Scripts de Instalação - Iniciativas LULC")
    print("=" * 60)
    
    success_count = 0
    
    # Criar instalador Windows
    print("\\n🪟 Criando instalador para Windows...")
    if create_windows_installer():
        success_count += 1
    
    # Criar instalador Linux/Mac
    print("\\n🐧 Criando instalador para Linux/Mac...")
    if create_linux_installer():
        success_count += 1
    
    # Criar README atualizado
    print("\\n📝 Criando documentação...")
    if create_readme_file():
        success_count += 1
    
    print(f"\\n✨ Processo concluído! {success_count}/3 arquivos criados com sucesso.")
    
    if success_count == 3:
        print("\\n🎉 Todos os scripts de instalação foram criados!")
        print("\\n📋 Arquivos disponíveis:")
        print("   • install.bat - Instalador para Windows")
        print("   • install.sh - Instalador para Linux/Mac") 
        print("   • README.md - Documentação completa")
        
        print("\\n🚀 Próximos passos:")
        print("   1. Execute o instalador apropriado para seu sistema")
        print("   2. Ou siga as instruções no README.md")
    
    return success_count == 3

if __name__ == "__main__":
    main()
