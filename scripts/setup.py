import os

if __name__ == "__main__":
    print("🛠 Creating virtual environment...")
    os.system("python -m venv venv")

    print("📦 Installing requirements...")
    os.system(r'venv\Scripts\pip install --upgrade pip')
    os.system(r'venv\Scripts\pip install -r requirements.txt')

    print("📁 Creating required folders...")
    os.makedirs("data/logs", exist_ok=True)

    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("OLLAMA_API_BASE=http://localhost:11434\nOLLAMA_MODEL=llama3.2\n")
        print("✅ .env file created.")
    else:
        print("ℹ️ .env already exists.")

    print("✅ Setup complete. You can now run the app using run_ui.py or run_analysis.py")
