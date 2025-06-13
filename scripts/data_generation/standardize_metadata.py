# Script para padronizar o arquivo initiatives_metadata.json conforme o modelo CGLS
import json

# Chaves padrão do modelo CGLS
STANDARD_KEYS = [
    "cobertura",
    "sigla",
    "provedor",
    "fonte",
    "resolucao_espacial",
    "intervalo_temporal",
    "frequencia_temporal",
    "sistema_referencia",
    "metodologia",
    "metodo_classificacao",
    "qnt_classes",
    "legenda_classes",
    "acuracia_geral"
]

# Mapeamento de chaves alternativas para as chaves padrão
KEY_MAP = {
    "fonte_dados": "fonte",
    "fonte": "fonte",
    "anos_disponiveis": "intervalo_temporal",
    "intervalo_temporal": "intervalo_temporal",
    "acuracia": "acuracia_geral",
    "acuracia_geral": "acuracia_geral",
    "frequencia_temporal": "frequencia_temporal",
    "sistema_referencia": "sistema_referencia",
    "metodologia": "metodologia",
    "metodo_classificacao": "metodo_classificacao",
    "tipo_metodologia": "metodo_classificacao",
    "qnt_classes": "qnt_classes",
    "classes": "qnt_classes",
    "legenda_classes": "legenda_classes",
    "legends": "legenda_classes",
    "resolucao_espacial": "resolucao_espacial",
    "sigla": "sigla",
    "provedor": "provedor",
    "cobertura": "cobertura"
}

# Função para padronizar um registro
def standardize_entry(entry):
    std = {k: None for k in STANDARD_KEYS}
    for key, value in entry.items():
        std_key = KEY_MAP.get(key)
        if std_key:
            # Ajuste para nomes diferentes
            if std_key == "intervalo_temporal" and not isinstance(value, list):
                std[std_key] = value if isinstance(value, list) else []
            elif std_key == "qnt_classes" and isinstance(value, str) and not value.lower().endswith("classes"):
                std[std_key] = value + " classes"
            else:
                std[std_key] = value
    return std

# Carregar arquivo original
with open("data/raw/initiatives_metadata.json", encoding="utf-8") as f:
    data = json.load(f)

# Padronizar todos os registros
new_data = {}
for k, v in data.items():
    new_data[k] = standardize_entry(v)

# Salvar arquivo padronizado
with open("data/raw/initiatives_metadata.json", "w", encoding="utf-8") as f:
    json.dump(new_data, f, ensure_ascii=False, indent=4)

print("Arquivo initiatives_metadata.json padronizado com sucesso!")
