# finalize_setup.ps1

Write-Host "Moving backend files to /backend directory..."
# Suppress errors if files are already moved or missing
Move-Item -Path ai_engine.py,auth.py,database.py,deployment_service.py,github_service.py,main.py,models.py,schemas.py,requirements.txt,routers -Destination backend\ -Force -ErrorAction SilentlyContinue

Write-Host "Initializing Git repository..."
git init
git add .
git commit -m "initial commit: DevFlow CI/CD automation platform"

Write-Host "Creating GitHub repository and pushing..."
gh repo create devflow --public --push --source=.

Write-Host "Done! DevFlow is successfully pushed to GitHub."
