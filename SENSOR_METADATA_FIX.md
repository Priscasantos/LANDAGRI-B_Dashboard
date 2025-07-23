# Correção do Sistema de Metadados dos Sensores

## Problema Identificado

O dashboard estava exibindo a mensagem "📡 Informações de sensor não especificadas para esta iniciativa" para todas as iniciativas. Isso ocorria porque o código estava procurando por uma coluna `"Sensor"` que não existia no DataFrame.

## Análise da Estrutura de Dados

### Dados Disponíveis:
- **"Source"**: Contém descrições textuais simples (ex: "Sentinel-2 MSI", "Landsat series")
- **"Sensors_Referenced"**: Contém dados estruturados em JSON com chaves de sensores que correspondem aos metadados

### Exemplo dos dados reais:
```
Source: "Sentinel-2 MSI"
Sensors_Referenced: [{"sensor_key": "SENTINEL_2_MSI"}]
```

## Solução Implementada

### 1. Mapeamento Correto dos Dados
- Alterado de `init_data.get("Sensor", "")` para `init_data.get("Sensors_Referenced", "")`
- Adicionado fallback para `init_data.get("Source", "")`

### 2. Processamento de Dados Estruturados
- Implementado parsing JSON para processar `Sensors_Referenced`
- Adicionado loop para processar múltiplos sensores por iniciativa
- Mapeamento das chaves dos sensores (`sensor_key`) para os metadados completos

### 3. Mapeamento dos Campos dos Metadados
O sistema agora mapeia corretamente os campos dos metadados dos sensores:

| Campo Original | Campo Usado | Descrição |
|----------------|-------------|-----------|
| `display_name` | Nome do sensor | Nome completo do sensor |
| `platform_name` | Plataforma/Satélite | Nome da plataforma/satélite |
| `spatial_resolutions_m` | Resolução Espacial | Lista de resoluções em metros |
| `revisit_time_days` | Tempo de Revisita | Tempo de revisita em dias |
| `spectral_bands` | Bandas Espectrais | Número ou lista de bandas |
| `swath_width_km` | Largura de Varredura | Largura em quilômetros |
| `sensor_type_description` | Tipo de Sensor | Descrição do tipo |
| `launch_date` | Data de Lançamento | Data de lançamento |
| `status` | Status | Status operacional |
| `agency` | Agência | Agência responsável |
| `data_access_url` | Acesso aos Dados | URL para acesso |

### 4. Tratamento de Erros
- Adicionado try-catch para parsing JSON
- Fallback para dados básicos quando metadados detalhados não estão disponíveis
- Tratamento para múltiplos sensores por iniciativa

## Resultado

O dashboard agora exibe corretamente:
- ✅ Informações detalhadas dos sensores quando disponíveis
- ✅ Dados básicos como fallback
- ✅ Múltiplos sensores por iniciativa
- ✅ Informações técnicas organizadas em layout responsivo

## Sensores Disponíveis nos Metadados

O arquivo `sensors_metadata.jsonc` contém metadados para:
- PROBAV_VEGETATION (PROBA-V)
- SENTINEL_2_MSI (Sentinel-2)
- LANDSAT_LEGACY_TM_ETM_OLI (Landsat)
- MODIS_TERRA_AQUA (MODIS)
- SENTINEL_1_SAR (Sentinel-1)
- LANDSAT_8_OLI_TIRS (Landsat 8)
- IRS_LISS (IRS LISS)
- CBERS_AWFI_MUX_PAN (CBERS)
- AMAZONIA_1_WFI (Amazônia-1)

## Arquivos Alterados

- `dashboard/overview.py`: Corrigido o processamento e exibição dos metadados dos sensores
- Linhas ~850-950: Seção "Informações de Sensores e Satélites" completamente reescrita

## Data da Correção
22 de julho de 2025
