@echo off

echo --------------------------
echo CHECKING FOR PREREQUISITES
echo --------------------------

Rem
Rem Check for python 2
Rem

py -2 --version > .\pythonver.txt 2>&1
find "2.7" pythonver.txt && (
    echo Python 2.7 is installed.
) || (
    Rem python2 --version > .\pythonver.txt 2>&1
    echo You must install Python 2.7 for this script to work correctly. Please install Python 2.7 and then run this script.
    pause
    EXIT
)
if exist pythonver.txt del pythonver.txt

Rem
Rem Check for praw
Rem

if exist C:\Python27\Scripts\pip.exe (
    C:\Python27\Scripts\pip.exe list > .\pippackages.txt
)


if not exist ".\images\" mkdir .\images
Rem py -2 .\fetcher.py

pause
