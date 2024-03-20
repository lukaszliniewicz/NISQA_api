@echo off

REM Set the Miniconda installation directory
set MINICONDA_DIR=%UserProfile%\Miniconda3

REM Check if conda is installed
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo Conda not found. Installing Miniconda...
    
    REM Download and install Miniconda silently
    powershell -Command "Invoke-WebRequest -Uri 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe' -OutFile 'Miniconda3-latest-Windows-x86_64.exe'"
    start /wait "" Miniconda3-latest-Windows-x86_64.exe /S /D=%MINICONDA_DIR%
    del Miniconda3-latest-Windows-x86_64.exe
    
    REM Add Miniconda to PATH
    set "PATH=%MINICONDA_DIR%;%MINICONDA_DIR%\Scripts;%MINICONDA_DIR%\Library\bin;%PATH%"
)

REM Activate the base conda environment
call "%MINICONDA_DIR%\Scripts\activate.bat"

REM Check if the nisqa environment exists
conda env list | find /i "nisqa" >nul
if %errorlevel% neq 0 (
    echo Creating nisqa environment...
    conda env create -f env.yml
)

REM Activate the nisqa environment
call conda activate nisqa

REM Install additional requirements for the API
echo Installing API requirements...
pip install -r requirements.txt

REM Start the API
echo Starting the API...
start /b "" uvicorn api:app --host 127.0.0.1 --port 8356

echo API is running on http://127.0.0.1:8356
echo Press any key to stop the API and exit...
pause >nul

REM Deactivate the nisqa environment
call conda deactivate

REM Stop the API process
taskkill /f /im uvicorn.exe >nul 2>&1
