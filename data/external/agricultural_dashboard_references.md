# Referências de Dashboards Agrícolas
## Inspirações coletadas em 2025-08-01

### USDA - International Production Assessment Division (IPAD)
**URL:** https://ipad.fas.usda.gov/

#### Características principais:
- **World Agricultural Production (WAP) Circular**: Relatórios mensais de produção
- **Commodity Intelligence Reports (CIR)**: Análises específicas por país e cultura
- **Drought and Flood Monitoring**: Monitoramento climático avançado
- **Standardized Precipitation Index (SPI)**: Visualizações de precipitação
- **Percent of Average Seasonal Greenness (PASG)**: Análise de verdor sazonal
- **Tropical Cyclone Monitor**: Monitoramento de ciclones
- **Automated Flooded Cropland Area Maps (AFCAM)**: Mapas de áreas inundadas

#### Estrutura de dados:
- Atualizações mensais de produção por país/região
- Análises específicas por cultura (trigo, soja, milho, algodão, etc.)
- Monitoramento em tempo real de condições climáticas
- Dados de rendimento e área plantada
- Previsões de safra baseadas em sensoriamento remoto

### FAO GIEWS - Global Information and Early Warning System
**URL:** https://www.fao.org/giews/countrybrief/index.jsp

#### Características principais:
- **Country Briefs**: Análises detalhadas por país
- **Cereal Balance Sheet (CCBS)**: Balanças de cereais por país
- **Food Price Monitoring and Analysis (FPMA)**: Monitoramento de preços
- **Earth Observation for Crop Monitoring**: Observação terrestre para culturas
- **Integrated Food Security Phase Classification (IPC)**: Classificação de segurança alimentar

#### Estrutura de dados:
- Análises regionais por continente (África, Ásia, América Latina, etc.)
- Dados de segurança alimentar
- Estimativas de produção e comércio de cereais
- Políticas alimentares e desenvolvimentos de preços
- Situação pecuária

### GEOGLAM Crop Monitor
**URL:** https://www.cropmonitor.org/

#### Características principais:
- **Monthly Crop Monitor Bulletins**: Boletins mensais de condições das culturas
- **Global Crop Conditions**: Condições globais das culturas
- **Crop Monitor Exploring Tool**: Ferramenta interativa de exploração
- **Agro-meteorological Earth Observation Indicators**: Indicadores agrometeorológicos
- **Crop Calendars**: Calendários de culturas sub-nacionais

#### Estrutura de dados:
- Condições atuais e históricas das culturas
- Calendários de culturas por região
- Gráficos de produção de culturas
- Dados de observação terrestre
- Máscaras de extensão de terras cultivadas globais
- Dados de escoamento superficial e indicadores de seca/inundação

## Padrões Identificados para Implementação

### 1. Estrutura de Navegação
- **Abas principais**: Overview, Calendário, Análise Regional, Monitoramento
- **Filtros inteligentes**: Por região, cultura, período temporal
- **Métricas resumidas**: Cards com KPIs principais

### 2. Visualizações Essenciais
- **Mapas interativos**: Distribuição espacial das culturas
- **Heatmaps temporais**: Calendários de plantio/colheita
- **Gráficos de séries temporais**: Produção ao longo do tempo
- **Gráficos de barras/pizza**: Distribuição por região/cultura
- **Indicadores climáticos**: Precipitação, temperatura, índices

### 3. Dados Essenciais
- **Produção por cultura**: Área plantada, rendimento, produção total
- **Cobertura temporal**: Anos disponíveis, frequência de atualização
- **Cobertura espacial**: Estados, regiões, nível sub-nacional
- **Calendário agrícola**: Períodos de plantio e colheita
- **Indicadores climáticos**: Precipitação, temperatura, índices de seca

### 4. Interface e UX
- **Headers visuais**: Gradientes e ícones temáticos
- **Cards de métricas**: Design moderno com cores diferenciadas
- **Filtros contextuais**: Seleção múltipla com valores padrão inteligentes
- **Tooltips informativos**: Ajuda contextual para usuários
- **Responsividade**: Layout adaptável para diferentes telas
