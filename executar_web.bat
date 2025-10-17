@echo off 
title Sistema de Inventário Web 
echo ============================================================ 
echo              SISTEMA DE INVENTÁRIO WEB v2.0 
echo ============================================================ 
echo. 
echo 🌐 Iniciando servidor web... 
echo    O navegador abrirá automaticamente 
echo    Pressione Ctrl+C para parar o servidor 
echo. 
call venv_web\Scripts\activate.bat 
streamlit run app.py --server.port 8548
