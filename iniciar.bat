@echo off
title Prefinance - Inicializador

echo ======================================================
echo           Prefinance - Inicializando Servicos
echo ======================================================
echo.

echo [+] Iniciando o servidor Backend (FastAPI)...
start cmd /k "title Backend (FastAPI) && cd /d %~dp0 && .venv\Scripts\activate.bat && python main.py"

echo [+] Aguardando 3 segundos para o Backend inicializar...
timeout /t 3 /nobreak > NUL

echo [+] Iniciando o Frontend (Nuxt)...
start cmd /k "title Frontend (Nuxt) && cd /d %~dp0 && npm run dev"

echo.
echo ======================================================
echo Backend e Frontend iniciados em janelas separadas!
echo ======================================================
timeout /t 5
