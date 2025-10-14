@echo off 
title Sistema Web - Modo Desenvolvimento 
call venv_web\Scripts\activate.bat 
streamlit run app.py --server.runOnSave true --server.fileWatcherType watchdog 
