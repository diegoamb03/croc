@echo off
echo Iniciando programador SICOE...
cd /d "C:\Users\Lenovo\Downloads\scripts\Sicoe"
"C:\Users\Lenovo\AppData\Local\Programs\Python\Python313\python.exe" "programador_sicoe.py"
echo Programador finalizado a las %date% %time% >> log_programador.txt
pause