@echo off
echo Starting all services...

wt new-tab --title "Ollama" cmd /k "ollama serve" ; new-tab --title "Backend" cmd /k "cd /d %~dp0ScrapperWebApp && uvicorn main:app --reload" ; new-tab --title "Frontend" cmd /k "cd /d %~dp0ScrapperWebApp\frontend && npm run dev"

echo All services launched in Windows Terminal tabs.
