@echo off 
echo Ativando ambiente virtual web... 
call venv_web\Scripts\activate.bat 
echo ✅ Ambiente ativado! 
echo Para iniciar o sistema: streamlit run app.py 
cmd /k 
