@echo off

echo --------------------------
echo CHECKING FOR PREREQUISITES
echo --------------------------

py -2 --version > .\pythonver.txt 2>&1

find "2.7" pythonver.txt && (
    py -2
) || (
    Rem python2 --version > .\pythonver.txt 2>&1
    echo You must install Python 2.7 for this script to work correctly.
    pause
    EXIT
)



if exist pythonver.txt del pythonver.txt

Rem python .\fetcher.py

pause
