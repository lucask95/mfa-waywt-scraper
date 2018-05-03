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
Rem Check for praw and BeautifulSoup
Rem

if exist C:\Python27\Scripts\pip.exe (

    C:\Python27\Scripts\pip.exe list > .\pippackages.txt

    find "praw" pippackages.txt && (
        echo praw is installed
    ) || (
        echo you must install praw to continue. to do this, type "pip2.7 install --user praw".
    )

    find "beautifulsoup4" pippackages.txt && (
        echo BeautifulSoup is installed
    ) || (
        echo you must install praw to continue. to do this, type "pip2.7 install --user beautifulsoup4".
        pause
        EXIT
    )

)
if exist pippackages.txt del pippackages.txt

py -2 .\fetcher.py
