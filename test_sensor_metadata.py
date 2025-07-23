#!/usr/bin/env python3
"""
Teste rápido para verificar se os metadados dos sensores estão funcionando corretamente
"""

import json
import sys
from pathlib import Path

# Adicionar o diretório scripts ao path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / "scripts"))


def test_sensor_metadata():
    """Testa o carregamento e processamento dos metadados dos sensores"""

    # Carregar dados das iniciativas
    # Carregar metadados dos sensores
    from scripts.utilities.json_interpreter import (
        _load_jsonc_file,
        interpret_initiatives_metadata,
    )

    # Carregar dados
    print("🔄 Carregando dados das iniciativas...")
    metadata_file_path = current_dir / "data" / "initiatives_metadata.jsonc"
    df = interpret_initiatives_metadata(metadata_file_path)

    print("🔄 Carregando metadados dos sensores...")
    sensors_file_path = current_dir / "data" / "json" / "sensors_metadata.jsonc"
    sensors_meta = _load_jsonc_file(sensors_file_path)

    print(f"✅ Carregadas {len(df)} iniciativas")
    print(f"✅ Carregados metadados de {len(sensors_meta)} sensores")

    # Testar algumas iniciativas
    test_initiatives = ["CGLS-HRVPP", "Dynamic World V1", "ESRI-10m Annual LULC"]

    for init_name in test_initiatives:
        print(f"\n{'=' * 60}")
        print(f"🧪 TESTANDO: {init_name}")
        print(f"{'=' * 60}")

        # Buscar a iniciativa no DataFrame
        initiative_row = df[df["Name"] == init_name]
        if initiative_row.empty:
            print(f"❌ Iniciativa '{init_name}' não encontrada")
            continue

        init_data = initiative_row.iloc[0]

        # Verificar dados de origem
        source = init_data.get("Source", "")
        sensors_referenced = init_data.get("Sensors_Referenced", "")

        print(f"📡 Source: {source}")
        print(f"🔗 Sensors_Referenced: {sensors_referenced}")

        # Processar sensors_referenced
        if sensors_referenced and str(sensors_referenced).strip().lower() not in [
            "n/a",
            "none",
            "",
            "[]",
        ]:
            try:
                sensors_list = (
                    json.loads(sensors_referenced)
                    if isinstance(sensors_referenced, str)
                    else sensors_referenced
                )
                if sensors_list and isinstance(sensors_list, list):
                    print(f"📊 Sensores encontrados: {len(sensors_list)}")

                    for i, sensor_ref in enumerate(sensors_list, 1):
                        if isinstance(sensor_ref, dict) and "sensor_key" in sensor_ref:
                            sensor_key = sensor_ref["sensor_key"]
                            print(f"  {i}. Sensor Key: {sensor_key}")

                            # Verificar se existe nos metadados
                            if sensor_key in sensors_meta:
                                sensor_info = sensors_meta[sensor_key]
                                print(
                                    f"     ✅ Metadados encontrados: {sensor_info.get('display_name', 'N/A')}"
                                )
                                print(
                                    f"     🛰️  Plataforma: {sensor_info.get('platform_name', 'N/A')}"
                                )
                                print(
                                    f"     🔍 Resolução: {sensor_info.get('spatial_resolutions_m', 'N/A')}"
                                )
                                print(
                                    f"     ⏰ Revisita: {sensor_info.get('revisit_time_days', 'N/A')} dias"
                                )
                            else:
                                print(
                                    f"     ❌ Metadados não encontrados para '{sensor_key}'"
                                )
                        else:
                            print(f"  {i}. ❌ Formato inválido: {sensor_ref}")
                else:
                    print("❌ Formato inválido de sensors_referenced")
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao decodificar JSON: {e}")
            except Exception as e:
                print(f"❌ Erro geral: {e}")
        else:
            print("❌ Nenhum sensor referenciado encontrado")


if __name__ == "__main__":
    test_sensor_metadata()
