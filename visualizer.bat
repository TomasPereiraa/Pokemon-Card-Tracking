@echo off
setlocal enabledelayedexpansion
title Pokemon Card Price Tracker - Visualizador
color 0B

:: Verificar se o ambiente virtual existe
if not exist "%~dp0venv\Scripts\python.exe" (
    echo.
    echo  [!] Ambiente virtual nao encontrado!
    echo  Corre primeiro o install.bat para instalar o programa.
    echo.
    pause
    exit /b 1
)

:: Verificar se o visualizer.py existe
if not exist "%~dp0visualizer.py" (
    echo.
    echo  [!] Ficheiro visualizer.py nao encontrado!
    echo  Certifica-te que este ficheiro esta na mesma pasta que o visualizer.py
    echo.
    pause
    exit /b 1
)

:: Verificar se existe historico de precos
if not exist "%~dp0data\price_history.json" (
    echo.
    echo  ============================================
    echo   POKEMON CARD PRICE TRACKER - VISUALIZADOR
    echo  ============================================
    echo.
    echo  [!] Ainda nao tens historico de precos!
    echo.
    echo  Tens de correr primeiro o run.bat com o teu
    echo  ficheiro CSV de cartas para gerar dados.
    echo.
    pause
    exit /b 1
)

cls
echo.
echo  ============================================
echo   POKEMON CARD PRICE TRACKER - VISUALIZADOR
echo  ============================================
echo.
echo  Comandos disponiveis:
echo.
echo    list              - Ver todas as cartas no historico
echo    total             - Grafico do valor total da colecao
echo    top [N]           - Top N cartas mais valiosas (ex: top 10)
echo    compare C1 C2     - Comparar precos de cartas
echo    save              - Guardar grafico como imagem PNG
echo    save total        - Guardar grafico do total como PNG
echo    save top [N]      - Guardar top N como PNG
echo    [nome da carta]   - Ver historico de precos de uma carta
echo    help              - Ver todos os comandos
echo    exit              - Sair
echo.
echo  ============================================
echo.

"%~dp0venv\Scripts\python.exe" "%~dp0visualizer.py"

echo.
if errorlevel 1 (
    echo  [!] Ocorreu um erro. Verifica a mensagem acima.
) else (
    echo  Ate a proxima!
)
echo.
pause
exit /b 0
