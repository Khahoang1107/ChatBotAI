@echo off
REM Script to setup and run Rasa chatbot on Windows

echo 🤖 Setting up Rasa Chatbot for Invoice Processing...

REM Create virtual environment if not exists
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📥 Installing Rasa dependencies...
pip install -r requirements.txt

REM Download Vietnamese spaCy model
echo 🌍 Downloading Vietnamese language model for spaCy...
python -m spacy download vi_core_news_lg

echo ✅ Setup completed!
echo.
echo 🚀 To start the Rasa server:
echo 1. Run 'rasa train' to train the model
echo 2. Run 'rasa run --enable-api --cors "*"' to start the server
echo 3. In another terminal, run 'rasa run actions' to start action server
echo.
echo 📋 Available commands:
echo - rasa train: Train the NLU and Core models
echo - rasa shell: Test the bot in command line
echo - rasa run: Start the Rasa server
echo - rasa run actions: Start the action server
echo - rasa interactive: Interactive learning mode

pause