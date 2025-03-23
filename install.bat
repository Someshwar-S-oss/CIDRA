@echo off

:: Set the Miniconda path (update this with your Miniconda installation path)
set /p CONDA_PATH=<config.txt

:: Activate Miniconda in a new command window for the frontend
start cmd /k "%CONDA_PATH%\condabin\conda.bat ollama pull llama3.1 && cd frontend && npm install && exit"

:: Activate Miniconda in another new command window for the backend
start cmd /k "%CONDA_PATH%\condabin\conda.bat create -n hackathon_env python=3.9 && exit"

start cmd /k "%CONDA_PATH%\condabin\conda.bat activate hackathon_env && cd backend && pip install -r requirements.txt && exit"

:: Exit the main batch file
exit
