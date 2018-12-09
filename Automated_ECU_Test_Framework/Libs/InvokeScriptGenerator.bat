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
set pyscriptFilename=%tempstr%_%testcaseFileSheetName%.py
%pythonpath% %pyscriptFilename%

:COMMONEXIT
pause
