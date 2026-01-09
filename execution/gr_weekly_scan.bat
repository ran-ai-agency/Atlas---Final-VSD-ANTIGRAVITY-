@echo off
REM GR International - Scan hebdomadaire des evenements
REM Execute tous les vendredis a 7h00

cd /d "c:\Users\ranai\Documents\Atlas - Final (VSD AntiGravity)"
python execution/gr_international_scraper.py > ".tmp\gr_scan_log_%date:~-4,4%%date:~-7,2%%date:~-10,2%.txt" 2>&1

REM Ouvrir le rapport si des evenements recommandes sont trouves
if exist ".tmp\gr_events_report_%date:~-4,4%-%date:~-7,2%-%date:~-10,2%.md" (
    start "" ".tmp\gr_events_report_%date:~-4,4%-%date:~-7,2%-%date:~-10,2%.md"
)
