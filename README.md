# 🌍 Comparador de Iniciativas LULC

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
   lulc_env\Scripts\activate
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
lulc_env\Scripts\activate   # Windows

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
