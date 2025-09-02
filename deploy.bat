@echo off
echo Deploying application...
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
echo Application deployed successfully.
