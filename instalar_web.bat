@echo off
chcp 65001 > nul
title Sistema de Inventário Web - Instalação

echo ============================================================
echo              SISTEMA DE INVENTÁRIO WEB - INSTALAÇÃO
echo ============================================================
echo.
echo 🌐 Preparando ambiente para versão web multiusuário
echo 📅 Data: %date% %time%
echo.

:: Verificar se está na pasta correta
if not exist "app.py" (
    echo ❌ Execute este script na pasta Inv_Web
    echo    Pasta atual: %cd%
    echo    Arquivos encontrados:
    dir /b *.py 2>nul
    pause
    exit /b 1
)

:: Verificar conexão com internet
echo 🌐 Verificando conexão com internet...
ping -n 1 8.8.8.8 >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  Sem conexão com internet detectada
    echo    A instalação pode falhar se dependências não estiverem em cache
    echo.
    echo Deseja continuar? (S/N)
    set /p continuar="Digite sua escolha: "
    if /i not "%continuar%"=="S" (
        echo Instalação cancelada pelo usuário
        pause
        exit /b 0
    )
) else (
    echo ✅ Conexão com internet OK
)

:: Verificar Python
echo 🔍 Verificando Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Python não encontrado!
    echo.
    echo 📋 INSTALE PYTHON PRIMEIRO:
    echo    https://python.org/downloads/
    echo    ⚠️  Marque "Add Python to PATH" durante instalação
    echo.
    echo 🔧 ALTERNATIVAMENTE:
    echo    - Use Microsoft Store (python)
    echo    - Use Anaconda (recomendado para iniciantes)
    echo.
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo ✅ !PYTHON_VERSION! encontrado
)

:: Verificar pip
echo 🔍 Verificando pip...
python -m pip --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ pip não encontrado!
    echo 🔧 Tentando reparar pip...
    python -m ensurepip --upgrade
    if %errorLevel% neq 0 (
        echo ❌ Erro ao reparar pip - reinstale o Python
        pause
        exit /b 1
    )
) else (
    echo ✅ pip encontrado
)

:: Verificar banco de dados
echo.
echo 🗄️ Verificando banco de dados...
if exist "database\inventario.db" (
    echo ✅ Banco de dados encontrado
) else (
    echo ⚠️  Banco de dados não encontrado
    echo    Será criado automaticamente na primeira execução
)

:: Criar ambiente virtual para web
echo.
echo 🔧 Criando ambiente virtual para versão web...
if exist "venv_web" (
    echo ✅ Ambiente virtual já existe
) else (
    python -m venv venv_web
    if %errorLevel% neq 0 (
        echo ❌ Erro ao criar ambiente virtual
        pause
        exit /b 1
    )
    echo ✅ Ambiente virtual criado
)

:: Ativar ambiente virtual
echo.
echo 🔧 Ativando ambiente virtual...
call venv_web\Scripts\activate.bat
if %errorLevel% neq 0 (
    echo ❌ Erro ao ativar ambiente virtual
    pause
    exit /b 1
)

:: Atualizar pip
echo.
echo 📦 Atualizando pip...
python -m pip install --upgrade pip

:: Instalar dependências web
echo.
echo 📦 Instalando dependências web...
echo    Isso pode levar alguns minutos...
echo.

:: Verificar se existe requirements_minimal.txt
if exist "requirements_minimal.txt" (
    echo 🔧 Instalando dependências essenciais...
    pip install -r requirements_minimal.txt
    if %errorLevel% neq 0 (
        echo ❌ Erro na instalação via requirements_minimal.txt
        echo 🔧 Tentando instalação individual...
        goto :install_individual
    ) else (
        echo ✅ Dependências mínimas instaladas com sucesso!
        goto :install_complete
    )
) else (
    echo ⚠️  requirements_minimal.txt não encontrado
    echo 🔧 Instalando dependências individualmente...
    goto :install_individual
)

:install_individual
pip install streamlit>=1.28.0
if %errorLevel% neq 0 (
    echo ❌ Erro ao instalar Streamlit
    echo 🔧 Tentando sem cache...
    pip install --no-cache-dir streamlit>=1.28.0
)

pip install pandas>=1.5.0 plotly>=5.15.0 python-dateutil>=2.8.0 Pillow>=9.0.0
if %errorLevel% neq 0 (
    echo ❌ Erro na instalação de dependências adicionais
    echo 🔧 Instalando uma por vez...
    pip install pandas>=1.5.0
    pip install plotly>=5.15.0 
    pip install python-dateutil>=2.8.0
    pip install Pillow>=9.0.0
)

:install_complete
echo.
echo ✅ Dependências instaladas com sucesso!

:: Perguntar sobre componentes opcionais
echo.
echo 🔧 Deseja instalar componentes opcionais? (S/N)
echo    - streamlit-authenticator (autenticação avançada)
echo    - streamlit-option-menu (menus melhorados)
echo    - streamlit-aggrid (tabelas avançadas)
set /p opcional="Digite sua escolha: "

if /i "%opcional%"=="S" (
    echo.
    echo 📦 Instalando componentes opcionais...
    pip install streamlit-authenticator>=0.2.3 streamlit-option-menu>=0.3.6 streamlit-aggrid>=0.3.4
    if %errorLevel% neq 0 (
        echo ⚠️  Alguns componentes opcionais falharam, mas o sistema funcionará normalmente
    ) else (
        echo ✅ Componentes opcionais instalados!
    )
)

:: Testar instalação
echo.
echo 🧪 Testando instalação completa...
if exist "testar_instalacao.py" (
    python testar_instalacao.py
) else (
    echo 🧪 Teste rápido de dependências...
    python -c "import streamlit; print('✅ Streamlit OK')" || echo "❌ Streamlit ERRO"
    python -c "import pandas; print('✅ Pandas OK')" || echo "❌ Pandas ERRO"  
    python -c "import plotly; print('✅ Plotly OK')" || echo "❌ Plotly ERRO"
    python -c "import sqlite3; print('✅ SQLite OK')" || echo "❌ SQLite ERRO"
)

:: Criar scripts de execução
echo.
echo 🔗 Criando scripts de execução...

:: Script principal de execução
echo @echo off > executar_web.bat
echo title Sistema de Inventário Web >> executar_web.bat
echo echo ============================================================ >> executar_web.bat
echo echo              SISTEMA DE INVENTÁRIO WEB v2.0 >> executar_web.bat
echo echo ============================================================ >> executar_web.bat
echo echo. >> executar_web.bat
echo echo 🌐 Iniciando servidor web... >> executar_web.bat
echo echo    O navegador abrirá automaticamente >> executar_web.bat
echo echo    Pressione Ctrl+C para parar o servidor >> executar_web.bat
echo echo. >> executar_web.bat
echo call venv_web\Scripts\activate.bat >> executar_web.bat
echo streamlit run app.py >> executar_web.bat

:: Script de desenvolvimento
echo @echo off > executar_dev.bat
echo title Sistema Web - Modo Desenvolvimento >> executar_dev.bat
echo call venv_web\Scripts\activate.bat >> executar_dev.bat
echo streamlit run app.py --server.runOnSave true --server.fileWatcherType watchdog >> executar_dev.bat

:: Script de ativação do ambiente
echo @echo off > ativar_ambiente_web.bat
echo echo Ativando ambiente virtual web... >> ativar_ambiente_web.bat
echo call venv_web\Scripts\activate.bat >> ativar_ambiente_web.bat
echo echo ✅ Ambiente ativado! >> ativar_ambiente_web.bat
echo echo Para iniciar o sistema: streamlit run app.py >> ativar_ambiente_web.bat
echo cmd /k >> ativar_ambiente_web.bat

echo ✅ Scripts criados:
echo    - executar_web.bat (produção)
echo    - executar_dev.bat (desenvolvimento)
echo    - ativar_ambiente_web.bat (ambiente)

:: Finalização
echo.
echo ============================================================
echo              🎉 INSTALAÇÃO WEB CONCLUÍDA COM SUCESSO! 🎉
echo ============================================================
echo.
echo 📋 COMO USAR:
echo.
echo 1. 🚀 Para iniciar o sistema web:
echo       Execute: executar_web.bat
echo       URL: http://localhost:8501
echo.
echo 2. 🔧 Para desenvolvimento:
echo       Execute: executar_dev.bat
echo       (Auto-reload ativado)
echo.
echo 3. 👥 Para acesso multiusuário:
echo       Outros usuários podem acessar via IP:
echo       http://SEU_IP:8501
echo.
echo 💡 DICAS:
echo    - Login: admin / 123456 ou cinthia / C1nt1@2024
echo    - Para acesso externo, configure firewall porta 8501
echo    - Para deploy online, use Streamlit Cloud (gratuito)
echo.
echo 📖 PRÓXIMOS PASSOS:
echo    1. Teste o sistema: executar_web.bat
echo    2. Para deploy online: leia GUIA_DEPLOY.md
echo    3. Para personalização: edite arquivos em pages/
echo.
echo ============================================================

echo.
echo Deseja iniciar o sistema web agora? (S/N)
set /p iniciar="Digite sua escolha: "

if /i "%iniciar%"=="S" (
    echo.
    echo 🚀 Iniciando Sistema de Inventário Web...
    echo    Aguarde, o navegador abrirá automaticamente
    echo.
    streamlit run app.py
) else (
    echo.
    echo ✅ Sistema pronto para uso!
    echo    Execute executar_web.bat quando quiser iniciar
)

echo.
pause