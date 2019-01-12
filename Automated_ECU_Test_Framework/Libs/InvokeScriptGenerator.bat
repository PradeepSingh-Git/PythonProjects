@echo off
color 0a
title Testcase Script Generator
echo:
echo:
echo:
echo:
echo              ##################################################
echo              #                                                #
echo              #          Testcase Script generation            #
echo              #                                                #
echo              ################################################## 
echo:
echo: 
echo: 
set testcaseFileName=%1
set testcaseFileSheetName=%2
set currentpath=%3
set pythonpath="C:\Python27\python.exe"

set LOG=CONSOLE_LOG.txt
set WTEE=".\wtee"

echo ###############################################################################
echo Testcase File Name  = %testcaseFileName%
echo Testcase Sheet Name = %testcaseFileSheetName%
echo Testcase File Path  = %currentpath%
echo ###############################################################################
cd %currentpath%
cd ..
%pythonpath% .\Libs\ScriptGenerator.py %1 %2 %3
echo:
echo              ##################################################
echo              #                                                #
echo              #             Testcase Execution                 #
echo              #                                                #
echo              ################################################## 
echo:
set /p input="Enter Y to start execution of generated script : "
if %input%=="Y" OR %input%=="y" (goto STARTEXECUTION) else COMMONEXIT

:STARTEXECUTION
cd %currentpath%
set tempstr=%testcaseFileName:.xlsm=%

echo tempstr = %tempstr%
rem set newcurrentpath=%currentpath%\%tempstr%_%testcaseFileSheetName%
mkdir %tempstr%
cd %currentpath%\%tempstr%

set sheetname=%testcaseFileSheetName%
set currentpath=%currentpath%\%tempstr%
mkdir %sheetname%
set newcurrentpath=%currentpath%\%sheetname%

cd %newcurrentpath%
echo newcurrentpath=%newcurrentpath%
rem set pyscriptFilename=%tempstr%_%testcaseFileSheetName%.py
set pyscriptFilename=%tempstr%_%sheetname%.py
echo pyscriptFilename = %pyscriptFilename%
%pythonpath% -u %pyscriptFilename% | %WTEE% log.txt
echo ########################InvokeScriptGenerator.bat##########################
:COMMONEXIT
pause