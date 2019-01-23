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

set WTEE="..\..\..\Libs\wtee\wtee"

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

set workbookNameFolder=%testcaseFileName:.xlsm=%
set sheetNameFolder=%testcaseFileSheetName%

cd %currentpath%\%workbookNameFolder%\%sheetNameFolder%

%pythonpath% -u %testcaseFileSheetName%.py | %WTEE% %testcaseFileSheetName%_Log_Console.txt

echo ########################InvokeScriptGenerator.bat##########################

:COMMONEXIT
pause