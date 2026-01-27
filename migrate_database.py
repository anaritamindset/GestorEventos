#!/usr/bin/env python3
"""
Script de migração para converter duracao_horas para duracao_minutos
Executar no PythonAnywhere: python migrate_database.py
"""

import sqlite3
import os

def find_database():
    """Encontra a base de dados SQLite"""
    possible_paths = [
        'instance/gestor_eventos.db',
        'gestor_eventos.db',
        'app.db',
        'instance/app.db',
        '../gestor_eventos.db',
    ]

    # Procurar ficheiros .db no diretório atual
    import glob
    db_files = glob.glob('**/*.db', recursive=True)

    if db_files:
        print(f"📂 Bases de dados encontradas: {', '.join(db_files)}")
        possible_paths = db_files + possible_paths

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


def migrate_database():
    """Migra a base de dados de duracao_horas para duracao_minutos"""

    # Procurar a base de dados
    db_path = find_database()

    if not db_path:
        print("❌ Base de dados não encontrada!")
        print("\n🔍 Por favor, execute o seguinte comando para encontrar a base de dados:")
        print("   find . -name '*.db' -type f")
        print("\nDepois edite o script e coloque o caminho correto na variável db_path")
        return False

    print(f"✅ Base de dados encontrada: {db_path}")

    print(f"📂 Conectando à base de dados: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Verificar estrutura atual da tabela
        cursor.execute("PRAGMA table_info(events)")
        columns = {col[1]: col for col in cursor.fetchall()}

        print(f"\n📋 Colunas encontradas: {', '.join(columns.keys())}")

        if 'duracao_minutos' in columns:
            print("✅ Coluna 'duracao_minutos' já existe! Nada a fazer.")
            return True

        if 'duracao_horas' not in columns:
            print("❌ Coluna 'duracao_horas' não encontrada!")
            print("⚠️  A estrutura da tabela não é a esperada.")
            return False

        print("\n🔄 Iniciando migração...")

        # Backup da tabela
        print("1️⃣  Criando backup da tabela events...")
        cursor.execute("CREATE TABLE events_backup AS SELECT * FROM events")

        # Adicionar nova coluna
        print("2️⃣  Adicionando coluna 'duracao_minutos'...")
        cursor.execute("ALTER TABLE events ADD COLUMN duracao_minutos INTEGER")

        # Converter dados (horas * 60 = minutos)
        print("3️⃣  Convertendo horas para minutos...")
        cursor.execute("UPDATE events SET duracao_minutos = duracao_horas * 60")

        # Verificar se há valores NULL
        cursor.execute("SELECT COUNT(*) FROM events WHERE duracao_minutos IS NULL")
        null_count = cursor.fetchone()[0]

        if null_count > 0:
            print(f"⚠️  Encontrados {null_count} registos com duracao_minutos NULL")
            print("   Definindo valor padrão de 60 minutos...")
            cursor.execute("UPDATE events SET duracao_minutos = 60 WHERE duracao_minutos IS NULL")

        # Criar nova tabela sem duracao_horas
        print("4️⃣  Criando nova estrutura da tabela...")
        cursor.execute("""
            CREATE TABLE events_new (
                id INTEGER NOT NULL PRIMARY KEY,
                nome TEXT NOT NULL,
                descricao TEXT,
                data_inicio DATE NOT NULL,
                data_fim DATE,
                duracao_minutos INTEGER NOT NULL,
                local TEXT,
                formadora TEXT,
                tipo_evento TEXT,
                status TEXT,
                capacidade_maxima INTEGER,
                template_id INTEGER,
                google_form_id TEXT,
                google_form_url TEXT,
                google_sheet_id TEXT,
                google_sheet_url TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                deleted_at TIMESTAMP,
                created_by INTEGER
            )
        """)

        # Copiar dados para nova tabela
        print("5️⃣  Copiando dados para nova estrutura...")
        cursor.execute("""
            INSERT INTO events_new
            SELECT id, nome, descricao, data_inicio, data_fim, duracao_minutos,
                   local, formadora, tipo_evento, status, capacidade_maxima,
                   template_id, google_form_id, google_form_url, google_sheet_id,
                   google_sheet_url, created_at, updated_at, deleted_at, created_by
            FROM events
        """)

        # Verificar contagem de registos
        cursor.execute("SELECT COUNT(*) FROM events")
        old_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM events_new")
        new_count = cursor.fetchone()[0]

        if old_count != new_count:
            raise Exception(f"Erro na migração: {old_count} registos originais vs {new_count} novos")

        # Remover tabela antiga e renomear
        print("6️⃣  Substituindo tabela antiga pela nova...")
        cursor.execute("DROP TABLE events")
        cursor.execute("ALTER TABLE events_new RENAME TO events")

        # Commit das alterações
        conn.commit()

        print("\n✅ Migração concluída com sucesso!")
        print(f"   📊 {new_count} eventos migrados")
        print(f"   💾 Backup disponível em: events_backup")

        return True

    except Exception as e:
        print(f"\n❌ Erro durante a migração: {e}")
        print("🔄 Fazendo rollback...")
        conn.rollback()
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("🔧 Script de Migração - duracao_horas → duracao_minutos")
    print("=" * 60)

    success = migrate_database()

    if success:
        print("\n" + "=" * 60)
        print("✅ MIGRAÇÃO CONCLUÍDA!")
        print("=" * 60)
        print("\nPróximos passos:")
        print("1. Recarregue a web app no PythonAnywhere (botão Reload)")
        print("2. Acesse https://ardoterra.pythonanywhere.com/eventos")
        print("3. Verifique se tudo funciona corretamente")
    else:
        print("\n" + "=" * 60)
        print("❌ MIGRAÇÃO FALHOU")
        print("=" * 60)
        print("\nPor favor, verifique os erros acima e tente novamente.")
