import pandas as pd
import json
import re
import numpy as np
from typing import Tuple, Dict, Any, List, Union
from pathlib import Path

def load_data(csv_path: str = None, json_path: str = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Load and clean the main DataFrame and metadata. Prioritizes new JSONC format."""
    
    # Try to load from new JSONC format first
    try:
        jsonc_path = 'data/raw/initiatives_metadata.jsonc'
        if Path(jsonc_path).exists():
            print(f"🎯 Usando novo formato JSONC: {jsonc_path}")
            return load_data_from_jsonc(jsonc_path)
    except Exception as e:
        print(f"⚠️ Erro ao carregar JSONC: {e}")
    
    # Fallback to old processed files
    if csv_path is None:
        csv_path = 'data/processed/initiatives_processed.csv'
    if json_path is None:
        json_path = 'data/processed/initiative_meta.json'
    
    # Verificar se existe o arquivo processado e usar ele prioritariamente
    try:
        processed_csv = 'data/processed/initiatives_processed.csv'
        df = pd.read_csv(processed_csv)
        print(f"✅ Usando arquivo processado: {processed_csv}")
    except FileNotFoundError:
        # Fallback para o arquivo original se existir
        try:
            dtype_dict = {
                'Nome': 'str',
                'Tipo': 'str',
                'Resolução (m)': 'float64',
                'Acurácia (%)': 'float64',
                'Classes': 'float64',
                'Metodologia': 'str',
                'Frequência Temporal': 'str',
                'Anos Disponíveis': 'str',
                'Escopo': 'str',
                'Score Resolução': 'float64',
                'Score Geral': 'float64',
                'Categoria Acurácia': 'str',
                'Categoria Resolução': 'str'
            }
            df = pd.read_csv(csv_path, dtype=dtype_dict)
            print(f"⚠️ Usando arquivo original: {csv_path}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Nenhum arquivo de dados encontrado. Verifique se existe {processed_csv} ou {csv_path}")
      
    # Carregar metadados
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        print(f"✅ Metadados carregados: {json_path}")
    except FileNotFoundError:
        # Fallback para metadados processados
        try:
            processed_meta = 'data/processed/metadata_processed.json'
            with open(processed_meta, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            print(f"⚠️ Usando metadados processados: {processed_meta}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Nenhum arquivo de metadados encontrado. Verifique se existe {json_path} ou metadata_processed.json")
    
    return df, metadata

def prepare_plot_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare DataFrame for plotting by converting to native Python types and ensuring required columns."""
    
    # Ensure we have all required columns for plotting
    required_columns = [
        'Nome', 'Tipo', 'Resolução (m)', 'Acurácia (%)', 'Classes', 
        'Metodologia', 'Frequência Temporal', 'Anos Disponíveis',
        'Score Resolução', 'Score Geral', 'Categoria Acurácia', 'Categoria Resolução'
    ]
    
    # Add missing columns with default values
    for col in required_columns:
        if col not in df.columns:
            if col in ['Resolução (m)', 'Acurácia (%)', 'Classes', 'Score Resolução', 'Score Geral']:
                df[col] = 0.0
            else:
                df[col] = 'N/A'
    
    # Convert data types for plotting compatibility
    plot_data = {}
    for col in df.columns:
        if df[col].dtype == 'object':
            plot_data[col] = df[col].astype(str).fillna('N/A').tolist()
        elif df[col].dtype in ['float64', 'int64']:
            plot_data[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).tolist()
        else:
            plot_data[col] = df[col].astype(str).tolist()
    
    result_df = pd.DataFrame(plot_data)
    
    # Ensure backward compatibility with old column names if needed
    if 'Escopo' not in result_df.columns and 'Tipo' in result_df.columns:
        result_df['Escopo'] = result_df['Tipo']
    
    print(f"📊 DataFrame preparado para plotting: {len(result_df)} linhas, {len(result_df.columns)} colunas")
    
    return result_df

def parse_resolution(resolution_value: Union[str, List[str]]) -> float:
    """Parse resolution value(s) and return numeric value in meters."""
    if isinstance(resolution_value, list):
        # Take the first (smallest/best) resolution if multiple values
        resolution_value = resolution_value[0] if resolution_value else "30"
    
    if isinstance(resolution_value, str):
        # Extract numeric value, handle formats like "10m", "30", "20-30"
        resolution_str = str(resolution_value).lower().replace('m', '').strip()
        
        # Handle ranges like "20-30" or "56-64"
        if '-' in resolution_str:
            parts = resolution_str.split('-')
            try:
                return float(parts[0])  # Use the better (smaller) resolution
            except:
                return 30.0
        
        # Handle single values
        try:
            return float(resolution_str)
        except:
            return 30.0
    
    return float(resolution_value) if resolution_value else 30.0

def parse_accuracy(accuracy_value: str) -> float:
    """Parse accuracy value and return numeric percentage."""
    if not accuracy_value or accuracy_value in ['Not informed', 'Incomplete', 'N/A']:
        return 0.0
    
    try:
        # Remove any non-numeric characters except decimal point
        accuracy_str = re.sub(r'[^\d.]', '', str(accuracy_value))
        return float(accuracy_str) if accuracy_str else 0.0
    except:
        return 0.0

def categorize_coverage(cobertura: str) -> str:
    """Categorize coverage type for plotting."""
    coverage_map = {
        'Global': 'Global',
        'Continental': 'Continental', 
        'Nacional': 'Nacional',
        'National': 'Nacional',
        'Regional': 'Regional'
    }
    return coverage_map.get(cobertura, 'Regional')

def parse_temporal_span(intervalo_temporal: List[int]) -> Dict[str, Union[int, str, List[int]]]:
    """Parse temporal interval and return comprehensive temporal derivations."""
    if not intervalo_temporal or not isinstance(intervalo_temporal, list):
        return {
            'start_year': 2000, 'end_year': 2024, 'temporal_span': 1, 'total_years': 1,
            'anos_disponiveis': [2000], 'anos_disponiveis_str': '2000', 'gaps_temporais': []
        }
    
    years = sorted([int(y) for y in intervalo_temporal if isinstance(y, (int, str)) and str(y).isdigit()])
    
    if not years:
        return {
            'start_year': 2000, 'end_year': 2024, 'temporal_span': 1, 'total_years': 1,
            'anos_disponiveis': [2000], 'anos_disponiveis_str': '2000', 'gaps_temporais': []
        }
    
    start_year = min(years)
    end_year = max(years)
    temporal_span = end_year - start_year + 1
    total_years = len(years)
    
    # Create anos_disponiveis string (expected format for graphics)
    anos_disponiveis_str = ','.join(map(str, years))
    
    # Calculate gaps
    gaps_temporais = []
    if temporal_span > total_years:
        expected_years = set(range(start_year, end_year + 1))
        missing_years = sorted(expected_years - set(years))
        gaps_temporais = missing_years
    
    return {
        'start_year': start_year,
        'end_year': end_year, 
        'temporal_span': temporal_span,
        'total_years': total_years,
        'anos_disponiveis': years,
        'anos_disponiveis_str': anos_disponiveis_str,
        'gaps_temporais': gaps_temporais
    }

def categorize_provider(provedor: str) -> str:
    """Categorize provider type."""
    provider_lower = provedor.lower()
    
    if any(term in provider_lower for term in ['space', 'esa', 'copernicus', 'nasa', 'inpe']):
        return 'Space Agency'
    elif any(term in provider_lower for term in ['university', 'umd', 'maryland']):
        return 'University'
    elif any(term in provider_lower for term in ['google', 'microsoft', 'esri']):
        return 'Tech Company'
    elif any(term in provider_lower for term in ['government', 'institute', 'ibge', 'conab', 'embrapa']):
        return 'Government'
    elif any(term in provider_lower for term in ['ngo', 'organization']):
        return 'NGO'
    else:
        return 'Other'

def categorize_method(metodo_classificacao: str) -> str:
    """Categorize classification method by technology level."""
    method_lower = metodo_classificacao.lower()
    
    if any(term in method_lower for term in ['deep learning', 'neural network', 'cnn', 'u-net']):
        return 'Deep Learning'
    elif any(term in method_lower for term in ['machine learning', 'random forest', 'gradient boost', 'catboost']):
        return 'Machine Learning'
    elif any(term in method_lower for term in ['visual interpretation', 'visual']):
        return 'Visual Interpretation'
    elif any(term in method_lower for term in ['statistical', 'regression', 'decision tree']):
        return 'Statistical Methods'
    else:
        return 'Combined'

def load_data_from_jsonc(jsonc_path: str = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Load and process data directly from the new JSONC metadata format."""
    
    if jsonc_path is None:
        jsonc_path = 'data/raw/initiatives_metadata.jsonc'
    
    # Load JSONC file (handle comments)
    try:
        with open(jsonc_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Remove comments from JSONC
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            # Remove line comments
            if '//' in line:
                comment_pos = line.find('//')
                line = line[:comment_pos]
            cleaned_lines.append(line)
        
        cleaned_content = '\n'.join(cleaned_lines)
        metadata = json.loads(cleaned_content)
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo de metadados não encontrado: {jsonc_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Erro ao parsear JSON: {e}")
    
    # Convert metadata to DataFrame format expected by plotting functions
    df_data = []
    
    for initiative_name, initiative_data in metadata.items():
        # Parse temporal data with comprehensive derivations
        temporal_info = parse_temporal_span(initiative_data.get('intervalo_temporal', []))
        
        # Handle multiple product versions (e.g., ESRI with qnt_classes and qnt_classes_2)
        classes_main = initiative_data.get('qnt_classes', '1')
        classes_alt = initiative_data.get('qnt_classes_2', None)
        
        # Use primary classes, but note alternative if available
        final_classes = classes_main
        if classes_alt and classes_alt != classes_main:
            print(f"📋 {initiative_name}: Encontradas múltiplas versões de classes ({classes_main}, {classes_alt})")
        
        # Handle multiple legend versions
        legend_main = initiative_data.get('legenda_classes', '')
        legend_alt = initiative_data.get('legenda_classes_2', None)
        final_legend = legend_main
        if legend_alt and legend_alt != legend_main:
            final_legend = f"{legend_main} | ALT: {legend_alt}"
        
        # Create DataFrame row
        row = {
            'Nome': initiative_name,
            'Sigla': initiative_data.get('sigla', ''),
            'Tipo': categorize_coverage(initiative_data.get('cobertura', 'Regional')),
            'Escopo': categorize_coverage(initiative_data.get('cobertura', 'Regional')),  # Backward compatibility
            'Cobertura': initiative_data.get('cobertura', 'Regional'),
            'Provedor': initiative_data.get('provedor', ''),
            'Tipo Provedor': categorize_provider(initiative_data.get('provedor', '')),
            'Fonte': initiative_data.get('fonte', ''),
            'Resolução (m)': parse_resolution(initiative_data.get('resolucao_espacial', '30')),
            'Sistema Referência': initiative_data.get('sistema_referencia', ''),
            'Acurácia (%)': parse_accuracy(initiative_data.get('acuracia_geral', '0')),
            'Classes': int(final_classes) if str(final_classes).isdigit() else 1,
            'Metodologia': initiative_data.get('metodologia', ''),
            'Método Classificação': initiative_data.get('metodo_classificacao', ''),
            'Categoria Método': categorize_method(initiative_data.get('metodo_classificacao', '')),
            'Frequência Temporal': initiative_data.get('frequencia_temporal', ''),
            'Frequência Atualização': initiative_data.get('frequencia_atualizacao', ''),
            'Legenda Classes': final_legend,
            # Temporal derivations (integrated from parse_temporal_span)
            'Ano Inicial': temporal_info['start_year'],
            'Ano Final': temporal_info['end_year'],
            'Span Temporal': temporal_info['temporal_span'],
            'Total Anos': temporal_info['total_years'],
            'Anos Disponíveis': temporal_info['anos_disponiveis_str'],  # Expected format for graphics
            'Gaps Temporais': ','.join(map(str, temporal_info['gaps_temporais'])) if temporal_info['gaps_temporais'] else '',
            # Derived metrics
            'Score Resolução': 100 / (1 + parse_resolution(initiative_data.get('resolucao_espacial', '30')) / 10),
            'Score Geral': (parse_accuracy(initiative_data.get('acuracia_geral', '0')) + 
                          100 / (1 + parse_resolution(initiative_data.get('resolucao_espacial', '30')) / 10)) / 2
        }
        
        # Add resolution and accuracy categories
        resolution = row['Resolução (m)']
        if resolution <= 10:
            row['Categoria Resolução'] = 'Muito Alta'
        elif resolution <= 30:
            row['Categoria Resolução'] = 'Alta'
        elif resolution <= 100:
            row['Categoria Resolução'] = 'Média'
        else:
            row['Categoria Resolução'] = 'Baixa'
            
        accuracy = row['Acurácia (%)']
        if accuracy >= 90:
            row['Categoria Acurácia'] = 'Excelente'
        elif accuracy >= 80:
            row['Categoria Acurácia'] = 'Boa'
        elif accuracy >= 70:
            row['Categoria Acurácia'] = 'Regular'
        else:
            row['Categoria Acurácia'] = 'Baixa'
        
        df_data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(df_data)
    
    # Enhance metadata with temporal derivations for graphics compatibility
    enhanced_metadata = {}
    for initiative_name, initiative_data in metadata.items():
        enhanced_data = initiative_data.copy()
        temporal_info = parse_temporal_span(initiative_data.get('intervalo_temporal', []))
        
        # Add expected temporal fields for graphics functions
        enhanced_data['anos_disponiveis'] = temporal_info['anos_disponiveis']  # List format expected by temporal graphics
        enhanced_data['start_year'] = temporal_info['start_year']
        enhanced_data['end_year'] = temporal_info['end_year']
        enhanced_data['span_temporal'] = temporal_info['temporal_span']
        enhanced_data['gaps_temporais'] = temporal_info['gaps_temporais']
        
        enhanced_metadata[initiative_name] = enhanced_data
    
    print(f"✅ Dados carregados do arquivo JSONC: {len(df)} iniciativas")
    print(f"📊 Colunas criadas: {len(df.columns)}")
    print(f"🎯 Metadados melhorados com derivações temporais para {len(enhanced_metadata)} iniciativas")
    
    return df, enhanced_metadata
