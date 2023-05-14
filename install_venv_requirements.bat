
@ECHO OFF
ECHO.
ECHO Checking for Python ...
REG QUERY "hkcu\software\python"
IF ERRORLEVEL 1 GOTO :NOPYTHON
GOTO :HASPYTHON

:NOPYTHON
ECHO.
ECHO Python is not installed on this system.
EXIT /B

:HASPYTHON

ECHO Setting up virtual environment for experiments ...
python -m venv .\experiment-env

ECHO Activating environment ...
CALL experiment-env\Scripts\activate

ECHO Installing requirements ...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

ECHO Done. Environment is ready to use!