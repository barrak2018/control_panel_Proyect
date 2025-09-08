@echo off
echo Deploying application...
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
mkdir .vscode
echo * > .vscode\.gitignore
echo Application deployed successfully.
