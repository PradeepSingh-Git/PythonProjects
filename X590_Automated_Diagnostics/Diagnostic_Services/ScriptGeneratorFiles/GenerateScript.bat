@echo off
color 0a
title Testcase Script Generator
echo:
echo:
echo:
echo:
echo              ##################################################
echo              #                                                #
echo              #     Diagnostics Testcase script generation     #
echo              #                                                #
echo              ################################################## 
echo:
echo: 
echo: 
set testcaseFileName=%1
set testcaseFileSheetName=%2
set currentpath=%3
set pythonpath="C:\Python27\python.exe"

cd %currentpath%\ScriptGeneratorFiles
%pythonpath% LatteScriptGenerator.py %1 %2 %3
echo:
echo              ##################################################
echo              #                                                #
echo              #        Diagnostics Testcase execution          #
echo              #            using LATTE framework               #
echo              #                                                #
echo              ################################################## 
echo:
set /p input="Enter Y to start execution of generated script : "
if %input%=="Y" OR %input%=="y" (goto STARTEXECUTION) else COMMONEXIT

:STARTEXECUTION
cd %currentpath%
set tempstr=%testcaseFileName:.xlsm=%
set pyscriptFilename=%tempstr%_%testcaseFileSheetName%.py
%pythonpath% %pyscriptFilename%

:COMMONEXIT
pause
