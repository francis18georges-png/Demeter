@echo off
if "%~1"=="" (
  echo Usage: Restore.cmd snapshots\snapshot_YYYYMMDD_HHMMSS.tar.gz
  exit /b 2
)
python tools\restore.py %1
