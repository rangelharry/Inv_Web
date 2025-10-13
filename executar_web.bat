@echo off
REM Sistema de Inventário Web - Script de Execução
REM Autor: Sistema Automatizado
REM Data: 2024

echo ==========================================
echo     SISTEMA DE INVENTÁRIO WEB - EXECUÇÃO
echo ==========================================
echo.

cd /d "%~dp0"

REM Verificar se está na pasta correta
if not exist "app.py" (
    echo ERRO: Arquivo app.py não encontrado!
    echo Certifique-se de estar na pasta Inv_Web
    pause
    exit /b 1
)

REM Verificar se ambiente virtual existe
if exist "venv\Scripts\activate.bat" (
    echo ✅ Ambiente virtual encontrado
    echo 🔄 Ativando ambiente virtual...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  Ambiente virtual não encontrado
    echo 💡 Execute primeiro: instalar_web.bat
    pause
    exit /b 1
)

REM Verificar se Streamlit está instalado
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo ❌ Streamlit não encontrado!
    echo 💡 Execute: instalar_web.bat
    pause
    exit /b 1
)

REM Verificar banco de dados
if not exist "database\inventario.db" (
    echo ⚠️  Banco de dados não encontrado!
    echo.
    echo 💡 Copiando banco da versão desktop...
    if exist "..\inv\inventario.db" (
        copy "..\inv\inventario.db" "database\inventario.db" >nul
        echo ✅ Banco copiado com sucesso!
    ) else (
        echo ❌ Banco da versão desktop não encontrado
        echo    Certifique-se de que a versão desktop está em ..\inv\
        pause
        exit /b 1
    )
)

echo.
echo 🌐 Iniciando servidor web...
echo 📱 O sistema abrirá automaticamente no navegador
echo 🔗 URL: http://localhost:8501
echo.
echo ℹ️  Para parar o servidor: Ctrl+C
echo.

REM Definir variáveis de ambiente
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
set STREAMLIT_SERVER_HEADLESS=false

REM Iniciar Streamlit
streamlit run app.py --server.port=8501

echo.
echo 👋 Servidor encerrado
pause