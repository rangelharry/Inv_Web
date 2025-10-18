@echo off
chcp 65001 >nul
title Sistema de Inventário Web - Instalação Completa
color 0A

echo.
echo ===============================================================================
echo                     SISTEMA DE INVENTÁRIO WEB - v2.0
echo                         Instalação Completa do Zero
echo ===============================================================================
echo.
echo Este script irá instalar todos os componentes necessários:
echo • Python 3.11+ (se não estiver instalado)
echo • Ambiente virtual Python
echo • Todas as dependências do projeto
echo • Banco de dados SQLite com dados de exemplo
echo • Configurações iniciais do sistema
echo.
echo Pressione qualquer tecla para continuar ou Ctrl+C para cancelar...
pause >nul

echo.
echo [1/8] Verificando Python...
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYVER_RAW=%%i
if "%PYVER_RAW%"=="" (
    echo ❌ Python não encontrado! 
    echo.
    echo Por favor, instale o Python 3.11.x primeiro:
    echo https://www.python.org/downloads/
    pause
    exit /b 1
) else (
    for /f "tokens=2 delims= " %%i in ("%PYVER_RAW%") do set PYVER=%%i
    for /f "tokens=1,2 delims=." %%a in ("%PYVER%") do (
        set PY_MAJOR=%%a
        set PY_MINOR=%%b
    )
    echo ✅ Python encontrado: %PYVER%
    if not "%PY_MAJOR%"=="3" (
        echo Versao do Python (%PYVER%) nao suportada. Instale Python 3.11.x.
        pause
        exit /b 1
    )
    if not "%PY_MINOR%"=="11" (
        echo Versao do Python (%PYVER%) nao suportada por este instalador. E obrigatorio o Python 3.11.x.
        pause
        exit /b 1
    )
)

echo.
echo [2/8] Verificando pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip não encontrado!
    echo Instalando pip...
    python -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo ❌ Erro ao instalar pip
        pause
        exit /b 1
    )
) else (
    echo ✅ pip encontrado
)

echo.
echo [3/8] Atualizando pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ⚠️  Aviso: Não foi possível atualizar o pip
) else (
    echo ✅ pip atualizado
)

echo.
echo [4/8] Criando ambiente virtual...
if exist "venv_web" (
    echo ⚠️  Ambiente virtual já existe. Removendo...
    rmdir /s /q "venv_web"
)

python -m venv venv_web
if %errorlevel% neq 0 (
    echo ❌ Erro ao criar ambiente virtual
    pause
    exit /b 1
) else (
    echo ✅ Ambiente virtual criado
)

echo.
echo [5/8] Ativando ambiente virtual...
call venv_web\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ Erro ao ativar ambiente virtual
    pause
    exit /b 1
) else (
    echo ✅ Ambiente virtual ativado
)

echo.
echo [6/8] Instalando dependências Python...
echo Instalando pacotes essenciais...

echo • Streamlit (framework web)...
pip install streamlit==1.28.0
if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar Streamlit
    pause
    exit /b 1
)

echo • Pandas (manipulação de dados)...
pip install pandas==2.1.3
if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar Pandas
    pause
    exit /b 1
)

echo • Plotly (gráficos)...
pip install plotly==5.17.0
if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar Plotly
    pause
    exit /b 1
)

echo • Outras dependências...
pip install python-dateutil==2.8.2
pip install pytz==2023.3
pip install bcrypt==4.1.2

echo ✅ Todas as dependências instaladas

echo.
echo [7/8] Criando estrutura de diretórios...
if not exist "database" mkdir database
if not exist "static" mkdir static
if not exist "pages" (
    echo ❌ Pasta pages não encontrada!
    echo Certifique-se de executar este script na pasta raiz do projeto
    pause
    exit /b 1
)
if not exist "utils" (
    echo ❌ Pasta utils não encontrada!
    echo Certifique-se de executar este script na pasta raiz do projeto
    pause
    exit /b 1
)
echo ✅ Estrutura de diretórios verificada

echo.
echo [8/8] Inicializando banco de dados...
python -c "
import sqlite3
import os
from datetime import datetime

# Criar banco de dados se não existir
db_path = 'database/inventario.db'
if not os.path.exists('database'):
    os.makedirs('database')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print('Criando tabelas...')

# Tabela usuários
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    nome TEXT,
    email TEXT,
    ativo INTEGER DEFAULT 1,
    data_criacao TEXT DEFAULT CURRENT_TIMESTAMP
)
''')

# Tabela equipamentos elétricos
cursor.execute('''
CREATE TABLE IF NOT EXISTS equipamentos_eletricos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    descricao TEXT NOT NULL,
    categoria TEXT,
    status TEXT DEFAULT 'Disponível',
    localizacao TEXT,
    responsavel TEXT,
    data_entrada TEXT,
    observacoes TEXT
)
''')

# Tabela equipamentos manuais
cursor.execute('''
CREATE TABLE IF NOT EXISTS equipamentos_manuais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    tipo TEXT NOT NULL,
    marca TEXT,
    modelo TEXT,
    status TEXT DEFAULT 'Disponível',
    estado TEXT DEFAULT 'Novo',
    localizacao TEXT,
    responsavel TEXT,
    data_entrada TEXT,
    observacoes TEXT
)
''')

# Tabela insumos
cursor.execute('''
CREATE TABLE IF NOT EXISTS insumos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    descricao TEXT NOT NULL,
    categoria TEXT,
    unidade TEXT,
    quantidade_atual REAL DEFAULT 0,
    quantidade_minima REAL DEFAULT 1,
    preco_unitario REAL DEFAULT 0,
    localizacao TEXT,
    observacoes TEXT
)
''')

# Tabela obras
cursor.execute('''
CREATE TABLE IF NOT EXISTS obras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    status TEXT DEFAULT 'ativa',
    data_inicio TEXT,
    data_termino TEXT,
    responsavel TEXT
)
''')

# Tabela movimentações
cursor.execute('''
CREATE TABLE IF NOT EXISTS movimentacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL,
    origem TEXT,
    destino TEXT,
    data TEXT,
    responsavel TEXT,
    status TEXT DEFAULT 'concluida',
    quantidade REAL DEFAULT 1,
    tabela_origem TEXT
)
''')

print('Inserindo dados de exemplo...')

# Usuário administrador padrão
cursor.execute('''
INSERT OR IGNORE INTO usuarios (usuario, senha_hash, nome, email, ativo) 
VALUES ('admin', 'bf83d08b6d9797f3dd2e2d4a348b35733cb993d0a767617e2c19755a90c77bfd', 'Administrador', 'admin@inventario.com', 1)
''')

# Equipamentos elétricos de exemplo
equipamentos_eletricos = [
    ('FUR001', 'Furadeira Elétrica Bosch GSB 13 RE', 'Furadeira', 'Disponível', 'Almoxarifado Central', 'João Silva', '01/10/2024', 'Furadeira com mandril de 13mm'),
    ('SER001', 'Serra Circular Makita 5007MG', 'Serra', 'Disponível', 'Oficina Principal', 'Maria Santos', '15/09/2024', 'Serra circular 7.1/4'),
    ('PAR001', 'Parafusadeira Dewalt DCD771C2', 'Parafusadeira', 'Em Uso', 'Residencial Vista Alegre', 'Pedro Costa', '10/08/2024', 'Parafusadeira com bateria 20V'),
    ('ESM001', 'Esmerilhadeira Bosch GWS 700', 'Esmerilhadeira', 'Disponível', 'Oficina Principal', 'Ana Lima', '20/07/2024', 'Esmerilhadeira angular 4.1/2'),
    ('SOL001', 'Máquina de Solda Inversora 200A', 'Soldadora', 'Manutenção', 'Manutenção', 'Carlos Ferreira', '05/06/2024', 'Soldadora inversora para eletrodo'),
]

for equip in equipamentos_eletricos:
    cursor.execute('''
    INSERT OR IGNORE INTO equipamentos_eletricos 
    (codigo, descricao, categoria, status, localizacao, responsavel, data_entrada, observacoes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', equip)

# Equipamentos manuais de exemplo
equipamentos_manuais = [
    ('MAR001', 'Martelo', 'Stanley', 'FatMax 20oz', 'Disponível', 'Novo', 'Almoxarifado Central', 'João Silva', '01/10/2024', 'Martelo unha 20oz'),
    ('CHA001', 'Chave de Fenda', 'Tramontina', '1/4 x 6', 'Disponível', 'Usado', 'Oficina Principal', 'Maria Santos', '15/09/2024', 'Chave fenda cabo isolado'),
    ('ALI001', 'Alicate Universal', 'Gedore', '8 pol', 'Em Uso', 'Novo', 'Edifício Comercial Centro', 'Pedro Costa', '10/08/2024', 'Alicate universal 8 polegadas'),
    ('NIN001', 'Nível de Alumínio', 'Vonder', '40cm', 'Disponível', 'Usado', 'Almoxarifado Central', 'Ana Lima', '20/07/2024', 'Nível de bolha 40cm'),
    ('TRA001', 'Trena', 'Stanley', '5m', 'Disponível', 'Novo', 'Oficina Principal', 'Carlos Ferreira', '05/06/2024', 'Trena 5 metros'),
]

for equip in equipamentos_manuais:
    cursor.execute('''
    INSERT OR IGNORE INTO equipamentos_manuais 
    (codigo, tipo, marca, modelo, status, estado, localizacao, responsavel, data_entrada, observacoes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', equip)

# Insumos de exemplo
insumos = [
    ('PAR001', 'Parafuso Phillips 3,5x25mm', 'Parafusos', 'UN', 500, 100, 0.15, 'Almoxarifado Central', 'Parafuso para drywall'),
    ('FIT001', 'Fita Isolante Preta 19mm', 'Material Elétrico', 'PC', 25, 10, 3.50, 'Almoxarifado Central', 'Fita isolante 3M'),
    ('CAB001', 'Cabo Flexível 2,5mm² Azul', 'Material Elétrico', 'M', 100, 20, 4.80, 'Almoxarifado Central', 'Cabo flexível por metro'),
    ('TIN001', 'Tinta Acrílica Branca 18L', 'Tintas', 'L', 5, 2, 85.00, 'Depósito A', 'Tinta acrílica premium'),
    ('LIX001', 'Lixa Madeira Grão 120', 'Abrasivos', 'UN', 50, 20, 2.30, 'Oficina Principal', 'Lixa para madeira'),
]

for insumo in insumos:
    cursor.execute('''
    INSERT OR IGNORE INTO insumos 
    (codigo, descricao, categoria, unidade, quantidade_atual, quantidade_minima, preco_unitario, localizacao, observacoes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', insumo)

# Obras de exemplo
obras = [
    ('Obra - Residencial Vista Alegre', 'Construção de condomínio residencial com 200 unidades', 'ativa', '2024-01-15', '2025-06-30', 'João Silva'),
    ('Obra - Edifício Comercial Centro', 'Construção de edifício comercial de 20 andares', 'ativa', '2024-03-01', '2025-12-15', 'Maria Santos'),
    ('Obra - Shopping Mall Norte', 'Construção de shopping center na zona norte', 'pausada', '2024-02-10', '2026-01-20', 'Pedro Costa'),
    ('Departamento - Almoxarifado Central', 'Controle e gestão do estoque principal', 'ativa', '2023-01-01', '2025-12-31', 'Ana Lima'),
    ('Departamento - Manutenção', 'Setor responsável por manutenção de equipamentos', 'ativa', '2023-01-01', '2025-12-31', 'Carlos Ferreira'),
]

for obra in obras:
    cursor.execute('''
    INSERT OR IGNORE INTO obras 
    (nome, descricao, status, data_inicio, data_termino, responsavel)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', obra)

conn.commit()
conn.close()

print('✅ Banco de dados inicializado com sucesso!')
print('✅ Usuário admin criado')
print('✅ Dados de exemplo inseridos')
"

if %errorlevel% neq 0 (
    echo ❌ Erro ao inicializar banco de dados
    pause
    exit /b 1
) else (
    echo ✅ Banco de dados inicializado
)

echo.
echo ===============================================================================
echo                         INSTALAÇÃO CONCLUÍDA! ✅
echo ===============================================================================
echo.
echo O Sistema de Inventário Web foi instalado com sucesso!
echo.
echo PRÓXIMOS PASSOS:
echo.
echo 1. Para iniciar o sistema:
echo    executar_sistema.bat
echo.
echo 2. Para acessar o sistema:
echo    Abra seu navegador em: http://localhost:8501
echo.
echo 3. Login padrão:
echo    Usuário: admin
echo    Senha: admin123
echo.
echo FUNCIONALIDADES DISPONÍVEIS:
echo • ⚡ Equipamentos Elétricos (8 exemplos)
echo • 🔧 Equipamentos Manuais (5 exemplos) 
echo • 📦 Insumos e Materiais (5 exemplos)
echo • 🏗️ Obras/Departamentos (5 exemplos)
echo • 📊 Movimentações com quantidade
echo • 🔄 Movimentação rápida integrada
echo • 📈 Relatórios completos
echo • 👥 Gestão de usuários
echo.
echo ARQUIVOS CRIADOS:
echo • venv_web/ - Ambiente virtual Python
echo • database/inventario.db - Banco de dados SQLite
echo • requirements.txt - Dependências (atualizado)
echo.
echo ===============================================================================
echo.
echo Pressione qualquer tecla para finalizar...
pause >nul

echo.
echo Criando arquivo executar_sistema.bat...
(
echo @echo off
echo chcp 65001 ^>nul
echo title Sistema de Inventário Web - Servidor
echo color 0B
echo.
echo echo ===============================================================================
echo echo                     SISTEMA DE INVENTÁRIO WEB - v2.0
echo echo                          Iniciando Servidor...
echo echo ===============================================================================
echo echo.
echo echo Ativando ambiente virtual...
echo call venv_web\Scripts\activate.bat
echo.
echo echo Iniciando servidor Streamlit...
echo echo Acesse: http://localhost:8501
echo echo.
echo echo Para parar o servidor, pressione Ctrl+C
echo echo.
echo streamlit run app.py --server.port 8501
echo.
echo echo.
echo echo Servidor finalizado.
echo pause
) > executar_sistema.bat

echo ✅ Arquivo executar_sistema.bat criado

echo.
echo Atualizando requirements.txt...
(
echo streamlit==1.28.0
echo pandas==2.1.3
echo plotly==5.17.0
echo python-dateutil==2.8.2
echo pytz==2023.3
echo bcrypt==4.1.2
) > requirements.txt

echo ✅ requirements.txt atualizado

echo.
echo ===============================================================================
echo                    INSTALAÇÃO 100%% COMPLETA! 🎉
echo ===============================================================================
echo.
echo O sistema está pronto para uso!
echo Execute: executar_sistema.bat para iniciar
echo.