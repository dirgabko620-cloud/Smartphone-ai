#!/bin/bash

# Smartphone AI - Setup Script for Termux

echo "🤖 Smartphone AI - Termux Installation"
echo "========================================"

# Update packages
echo "📦 Updating packages..."
pkg update -y
pkg upgrade -y

# Install dependencies
echo "📥 Installing dependencies..."
pkg install -y python pip nodejs git build-essential libssl-dev libffi-dev

# Clone repository (if not already in it)
if [ ! -f "README.md" ]; then
    echo "📂 Cloning repository..."
    git clone https://github.com/dirgabko620-cloud/Smartphone-ai.git
    cd Smartphone-ai
fi

# Setup backend
echo "🔧 Setting up backend..."
cd backend
pip install -r requirements.txt
cd ..

# Setup frontend
echo "🎨 Setting up frontend..."
cd frontend
npm install
cd ..

# Create .env file
echo "⚙️ Creating environment file..."
cp backend/.env.example backend/.env

echo ""
echo "✅ Installation complete!"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Open .env file and add your API keys:"
echo "   - OPENAI_API_KEY (optional)"
echo "   - Other configurations"
echo ""
echo "2. Start services in separate terminals:"
echo ""
echo "   Terminal 1 - Backend:"
echo "   cd backend && python main.py"
echo ""
echo "   Terminal 2 - Frontend:"
echo "   cd frontend && npm start"
echo ""
echo "   Terminal 3 - Ollama (optional):"
echo "   ollama serve"
echo ""
echo "3. Open browser and go to: http://localhost:3000"
echo ""
echo "🚀 Happy coding!"