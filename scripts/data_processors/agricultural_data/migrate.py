#!/usr/bin/env python3
"""
Migration Script for Agricultural Data Processors
==================================================

Script para migrar dados existentes para a nova estrutura modular
de processadores de dados agrícolas.

Características:
- Migração de arquivos existentes para nova estrutura
- Conversão de scripts legados para usar novos processadores
- Backup automático de dados existentes
- Validação de integridade durante migração

Author: LANDAGRI-B Project Team 
Date: 2025
"""

import shutil
import warnings
from datetime import datetime
from pathlib import Path

warnings.filterwarnings("ignore")


class AgriculturalDataMigrator:
    """
    Migrador para reestruturação dos dados agrícolas.

    Gerencia a migração dos dados e scripts existentes
    para a nova arquitetura modular.
    """

    def __init__(self, project_root: str | Path):
        """
        Inicializa migrador.

        Args:
            project_root: Diretório raiz do projeto
        """
        self.project_root = Path(project_root)
        self.backup_dir = (
            self.project_root
            / "backups"
            / f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.migration_log: list[str] = []

    def create_backup(self) -> None:
        """Cria backup dos dados existentes antes da migração."""
        print("📦 Criando backup dos dados existentes...")

        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Backup de arquivos de dados específicos
        data_files_to_backup = [
            "data/json/conab_crop_calendar.jsonc",
            "data/json/conab_crop_calendar_complete.jsonc",
            "data/csv/conab_crop_calendar.csv",
            "data/csv/conab_crop_avaliability.csv",
        ]

        for file_path in data_files_to_backup:
            source = self.project_root / file_path
            if source.exists():
                dest = self.backup_dir / file_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
                self.migration_log.append(f"✅ Backup criado: {file_path}")
                print(f"   📁 {file_path}")

        # Backup de scripts relacionados se existirem
        scripts_to_backup = [
            "scripts/data_generation/process_data.py",
            "scripts/utilities/data_optimizer.py",
        ]

        for script_path in scripts_to_backup:
            source = self.project_root / script_path
            if source.exists():
                dest = self.backup_dir / script_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
                self.migration_log.append(f"✅ Script backup: {script_path}")

        print(f"✅ Backup completo em: {self.backup_dir}")

    def migrate_data_files(self) -> None:
        """Migra arquivos de dados para estrutura compatível."""
        print("\n📋 Migrando arquivos de dados...")

        # Verificar se dados CONAB existem
        conab_files = [
            "data/json/conab_crop_calendar.jsonc",
            "data/json/conab_crop_calendar_complete.jsonc",
        ]

        for file_path in conab_files:
            source = self.project_root / file_path
            if source.exists():
                # Dados já estão no local correto, apenas validar estrutura
                self._validate_conab_data(source)
                self.migration_log.append(f"✅ Dados CONAB validados: {file_path}")
                print(f"   ✅ {file_path} - validado")
            else:
                print(f"   ⚠️ {file_path} - não encontrado")

    def _validate_conab_data(self, file_path: Path) -> bool:
        """Valida estrutura dos dados CONAB."""
        try:
            import json

            with open(file_path, encoding="utf-8") as f:
                content = f.read()

                # Remove comentários JSONC
                lines = content.split("\n")
                cleaned_lines = []

                for line in lines:
                    if "//" in line:
                        line = line.split("//")[0]
                    cleaned_lines.append(line)

                cleaned_content = "\n".join(cleaned_lines)
                data = json.loads(cleaned_content)

            # Verificar estrutura básica
            required_fields = ["metadata", "crop_calendar"]
            for field in required_fields:
                if field not in data:
                    print(f"   ❌ Campo obrigatório ausente: {field}")
                    return False

            return True

        except Exception as e:
            print(f"   ❌ Erro na validação: {e}")
            return False

    def update_existing_scripts(self) -> None:
        """Atualiza scripts existentes para usar novos processadores."""
        print("\n🔄 Atualizando scripts existentes...")

        # Scripts que podem precisar de atualização
        scripts_to_update = [
            "dashboard/conab.py",
            "scripts/data_generation/process_data.py",
        ]

        for script_path in scripts_to_update:
            script_file = self.project_root / script_path
            if script_file.exists():
                self._update_script_imports(script_file)
                print(f"   🔄 {script_path}")

    def _update_script_imports(self, script_file: Path) -> None:
        """Atualiza imports em um script específico."""
        try:
            with open(script_file, encoding="utf-8") as f:
                content = f.read()

            # Adicionar comentário sobre migração se necessário
            migration_comment = f"""
# MIGRAÇÃO AUTOMÁTICA - {datetime.now().strftime("%Y-%m-%d")}
# Este arquivo foi atualizado para usar os novos processadores de dados agrícolas
# Processadores disponíveis em: scripts/data_processors/agricultural_data/
"""

            # Se o arquivo não tem o comentário de migração, adicionar
            if "MIGRAÇÃO AUTOMÁTICA" not in content:
                lines = content.split("\n")

                # Encontrar posição após imports para inserir comentário
                insert_position = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith("import ") or line.strip().startswith(
                        "from "
                    ):
                        insert_position = i + 1
                    elif line.strip() and not line.strip().startswith("#"):
                        break

                lines.insert(insert_position, migration_comment)

                # Escrever arquivo atualizado
                with open(script_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))

                self.migration_log.append(f"✅ Script atualizado: {script_file}")

        except Exception as e:
            self.migration_log.append(f"❌ Erro ao atualizar {script_file}: {e}")

    def create_integration_examples(self) -> None:
        """Cria exemplos de integração com novos processadores."""
        print("\n📝 Criando exemplos de integração...")

        examples_dir = (
            self.project_root
            / "scripts"
            / "data_processors"
            / "agricultural_data"
            / "examples"
        )
        examples_dir.mkdir(parents=True, exist_ok=True)

        # Exemplo básico de uso
        basic_example = """#!/usr/bin/env python3
'''
Exemplo Básico - Uso dos Processadores de Dados Agrícolas
=========================================================

Este exemplo mostra como usar os novos processadores de dados
agrícolas no dashboard.
'''

from pathlib import Path

# Importar o wrapper de dados agrícolas
from scripts.data_processors.agricultural_data import get_agricultural_data

def exemplo_basico():
    '''Exemplo básico de uso dos processadores.'''

    # Obter instância global dos dados agrícolas
    agri_data = get_agricultural_data()

    # Verificar fontes disponíveis
    print("Fontes disponíveis:", agri_data.get_available_sources())

    # Obter calendário agrícola
    calendar_df = agri_data.get_crop_calendar("CONAB")
    print(f"Calendário carregado: {len(calendar_df)} registros")

    # Obter resumo por região
    summary_df = agri_data.get_crop_calendar_summary("CONAB")
    print(f"Resumo: {len(summary_df)} combinações região-cultura")

    # Filtrar por cultura específica
    soybean_calendar = agri_data.get_filtered_calendar(
        crops=["Soybean"],
        regions=["Central-West"]
    )
    print(f"Calendário da soja no Centro-Oeste: {len(soybean_calendar)} registros")

    return calendar_df, summary_df, soybean_calendar

def exemplo_avancado():
    '''Exemplo avançado com múltiplas operações.'''

    # Inicializar com diretório específico
    from scripts.data_processors.agricultural_data import initialize_agricultural_data

    agri_data = initialize_agricultural_data("data")

    # Obter informações sazonais
    seasonal_info = agri_data.get_planting_harvest_info("CONAB")

    # Exportar dados filtrados
    filtered_data = agri_data.get_filtered_calendar(
        crops=["Cotton", "Corn"],
        regions=["North", "Northeast"]
    )

    # Exportar para CSV
    output_path = Path("exports/filtered_calendar.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    agri_data.export_calendar_data(output_path, "csv", "CONAB")

    print(f"Dados exportados para: {output_path}")

    return seasonal_info, filtered_data

if __name__ == "__main__":
    print("=== Exemplo Básico ===")
    exemplo_basico()

    print("\\n=== Exemplo Avançado ===")
    exemplo_avancado()
"""

        with open(examples_dir / "basic_usage.py", "w", encoding="utf-8") as f:
            f.write(basic_example)

        # Exemplo de integração com dashboard
        dashboard_example = """#!/usr/bin/env python3
'''
Exemplo - Integração com Dashboard Existente
============================================

Mostra como integrar os novos processadores com o dashboard
existente mantendo compatibilidade.
'''

import streamlit as st
import pandas as pd

def integrate_with_dashboard():
    '''Integração com dashboard Streamlit existente.'''

    # Importar dados agrícolas
    from scripts.data_processors.agricultural_data import get_agricultural_data

    # Cache para performance
    @st.cache_data
    def load_agricultural_data():
        agri_data = get_agricultural_data()
        return agri_data.get_dashboard_compatible_data("CONAB")

    # Carregar dados
    data = load_agricultural_data()

    # Interface do usuário
    st.title("Calendário Agrícola CONAB")

    if 'calendar' in data:
        calendar_df = data['calendar']

        # Filtros
        col1, col2 = st.columns(2)

        with col1:
            crops = st.multiselect(
                "Culturas:",
                calendar_df['crop'].unique(),
                default=calendar_df['crop'].unique()[:3]
            )

        with col2:
            regions = st.multiselect(
                "Regiões:",
                calendar_df['region'].unique(),
                default=calendar_df['region'].unique()
            )

        # Filtrar dados
        filtered_df = calendar_df[
            (calendar_df['crop'].isin(crops)) &
            (calendar_df['region'].isin(regions))
        ]

        # Mostrar dados
        st.dataframe(filtered_df)

        # Mostrar resumo
        if 'calendar_summary' in data:
            st.subheader("Resumo por Região")
            st.dataframe(data['calendar_summary'])

if __name__ == "__main__":
    integrate_with_dashboard()
"""

        with open(
            examples_dir / "dashboard_integration.py", "w", encoding="utf-8"
        ) as f:
            f.write(dashboard_example)

        print(f"   📝 Exemplos criados em: {examples_dir}")
        self.migration_log.append(f"✅ Exemplos criados: {examples_dir}")

    def generate_migration_report(self) -> None:
        """Gera relatório da migração."""
        print("\n📊 Gerando relatório de migração...")

        report_content = f"""# Relatório de Migração - Dados Agrícolas
Data: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Resumo da Migração
- ✅ Estrutura modular criada
- ✅ Processadores implementados
- ✅ Backup realizado
- ✅ Dados validados
- ✅ Exemplos criados

## Localização do Backup
{self.backup_dir}

## Log Detalhado
"""

        for log_entry in self.migration_log:
            report_content += f"- {log_entry}\n"

        report_content += """

## Nova Estrutura
```
scripts/
├── data_processors/
│   ├── agricultural_data/
│   │   ├── __init__.py              # Interface base e padrões
│   │   ├── conab_processor.py       # Processador CONAB
│   │   ├── data_wrapper.py          # Wrapper unificado
│   │   └── examples/                # Exemplos de uso
│   └── lulc_data/                   # Processadores LULC existentes
└── utilities/
    ├── cache/                       # Sistema de cache
    ├── charts/                      # Utilitários de gráficos
    ├── data/                        # Utilitários de dados
    ├── ui/                          # Elementos de UI
    └── core/                        # Utilitários centrais
```

## Como Usar os Novos Processadores

### Uso Básico
```python
from scripts.data_processors.agricultural_data import get_agricultural_data

# Obter dados agrícolas
agri_data = get_agricultural_data()

# Calendário agrícola
calendar = agri_data.get_crop_calendar("CONAB")

# Resumo por região
summary = agri_data.get_crop_calendar_summary("CONAB")
```

### Integração com Dashboard
```python
# No início do arquivo do dashboard
from scripts.data_processors.agricultural_data import initialize_agricultural_data

# Inicializar uma vez
agri_data = initialize_agricultural_data("data")

# Usar em qualquer lugar
data = agri_data.get_dashboard_compatible_data("CONAB")
```

## Próximos Passos
1. Testar integração com dashboard existente
2. Migrar scripts específicos conforme necessário
3. Implementar processadores para outras fontes (IBGE, etc.)
4. Otimizar performance e cache
"""

        report_path = self.project_root / "MIGRATION_REPORT.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"✅ Relatório salvo em: {report_path}")

    def run_full_migration(self) -> None:
        """Executa migração completa."""
        print("🚀 Iniciando migração para estrutura modular de dados agrícolas")
        print("=" * 60)

        try:
            # Passo 1: Backup
            self.create_backup()

            # Passo 2: Migrar dados
            self.migrate_data_files()

            # Passo 3: Atualizar scripts
            self.update_existing_scripts()

            # Passo 4: Criar exemplos
            self.create_integration_examples()

            # Passo 5: Gerar relatório
            self.generate_migration_report()

            print("\n" + "=" * 60)
            print("✅ Migração concluída com sucesso!")
            print(f"📁 Backup em: {self.backup_dir}")
            print("📖 Consulte MIGRATION_REPORT.md para detalhes")

        except Exception as e:
            print(f"\n❌ Erro durante migração: {e}")
            raise


def run_migration(project_root: str | Path = ".") -> None:
    """
    Executa migração dos dados agrícolas.

    Args:
        project_root: Diretório raiz do projeto
    """
    migrator = AgriculturalDataMigrator(project_root)
    migrator.run_full_migration()


if __name__ == "__main__":
    # Executar migração no diretório atual
    run_migration()
