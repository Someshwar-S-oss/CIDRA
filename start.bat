@echo off

:: Read the Miniconda path from the config.txt file
set /p CONDA_PATH=<config.txt

:: Activate Miniconda in a new command window for the frontend
start cmd /k "%CONDA_PATH%\condabin\conda.bat activate base && cd frontend && npm run dev"

:: Activate Miniconda in another new command window for the backend
start cmd /k "%CONDA_PATH%\condabin\conda.bat activate base && cd backend && python app.py"

:: Open localhost:3000 in the default web browser
start http://localhost:3000

:: Exit the main batch file
exit
