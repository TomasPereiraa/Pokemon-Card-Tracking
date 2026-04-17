@echo off
setlocal enabledelayedexpansion
title Pokemon Card Price Tracker - Instalador
color 0A

echo.
echo  ============================================
echo   POKEMON CARD PRICE TRACKER - INSTALADOR
echo  ============================================
echo.
echo  Este instalador vai configurar tudo automaticamente.
echo  Nao feches esta janela ate terminar!
echo.
pause

:: ─── Verificar Python ───────────────────────────────────────────────────────
echo.
echo [1/4] A verificar Python...

set PYTHON_CMD=

python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    goto :python_found
)

py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
    goto :python_found
)

python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    goto :python_found
)

:: Procurar nas pastas comuns do Windows
for %%P in (
    "%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "C:\Python314\python.exe"
    "C:\Python313\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
) do (
    if exist %%P (
        set PYTHON_CMD=%%~P
        goto :python_found
    )
)

echo.
echo  [!] Python nao foi encontrado no PATH.
echo.
echo  Vais ser redirecionado para a pagina de download do Python.
echo  - Faz download da versao mais recente (Python 3.x.x)
echo  - IMPORTANTE: Marca a caixa "Add Python to PATH" antes de instalar!
echo.
start https://www.python.org/downloads/
echo  Depois de instalar o Python, executa este instalador novamente.
echo.
pause
exit /b 1

:python_found
for /f "tokens=*" %%v in ('"%PYTHON_CMD%" --version 2^>^&1') do set PYVER=%%v
echo  [OK] %PYVER% encontrado! (comando: %PYTHON_CMD%)

:: ─── Verificar Google Chrome ─────────────────────────────────────────────────
echo.
echo [2/4] A verificar Google Chrome...
set CHROME_FOUND=0

if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" set CHROME_FOUND=1
if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" set CHROME_FOUND=1
if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" set CHROME_FOUND=1

if "%CHROME_FOUND%"=="0" (
    echo.
    echo  [!] Google Chrome nao encontrado!
    echo.
    echo  Vais ser redirecionado para a pagina de download do Chrome.
    echo  Instala o Chrome e executa este instalador novamente.
    echo.
    start https://www.google.com/chrome/
    pause
    exit /b 1
)
echo  [OK] Google Chrome encontrado!

:: ─── Criar ambiente virtual ──────────────────────────────────────────────────
echo.
echo [3/4] A criar ambiente virtual...

if exist "%~dp0venv" (
    echo  [OK] Ambiente virtual ja existe, a reutilizar...
) else (
    "%PYTHON_CMD%" -m venv "%~dp0venv"
    if errorlevel 1 (
        echo.
        echo  [ERRO] Nao foi possivel criar o ambiente virtual.
        echo  Tenta correr este ficheiro como Administrador.
        echo.
        pause
        exit /b 1
    )
    echo  [OK] Ambiente virtual criado!
)

:: ─── Instalar dependencias ───────────────────────────────────────────────────
echo.
echo [4/4] A instalar dependencias (pode demorar alguns minutos)...
echo.

"%~dp0venv\Scripts\python.exe" -m pip install --upgrade pip --quiet

if exist "%~dp0requirements.txt" (
    "%~dp0venv\Scripts\pip.exe" install -r "%~dp0requirements.txt"
) else (
    "%~dp0venv\Scripts\pip.exe" install pandas~=2.2.3 seleniumbase~=4.34.4 matplotlib~=3.10.1
)

if errorlevel 1 (
    echo.
    echo  [ERRO] Falhou a instalacao das dependencias.
    echo  Verifica a tua ligacao a internet e tenta novamente.
    echo.
    pause
    exit /b 1
)

:: ─── Concluido ───────────────────────────────────────────────────────────────
echo.
echo  ============================================
echo   INSTALACAO CONCLUIDA COM SUCESSO!
echo  ============================================
echo.
echo  Para usar o programa, faz duplo-clique em:
echo      run.bat
echo.
echo  Precisas de um ficheiro CSV com os URLs das
echo  cartas do Cardmarket para comecar.
echo.
pause
exit /b 0
