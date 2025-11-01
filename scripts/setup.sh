#!/bin/bash

echo "🚀 Setting up IT Helpdesk Copilot MVP..."

# Create .env file if it doesn't exist
if [ ! -f "infra/.env" ]; then
    echo "📝 Creating .env file..."
    cp infra/env.example infra/.env
    echo "✅ Created infra/.env - Please edit it with your credentials"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd apps/api
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
cd ../..

# Install Node dependencies
echo "📦 Installing Node dependencies..."
cd apps/web
npm install
cd ../..

# Create MongoDB indexes (if needed)
echo "📊 MongoDB will be initialized on first run"

# Create Vector Search index instruction
echo ""
echo "📚 IMPORTANT: Create MongoDB Atlas Vector Search Index:"
echo "   1. Go to MongoDB Atlas > Collections > kb_chunks"
echo "   2. Click 'Create Search Index' > JSON Editor"
echo "   3. Use index from README.md (kb_chunks_vec)"
echo ""

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit infra/.env with your MongoDB URI and OpenAI API key"
echo "2. Run: python apps/api/packages/rag/ingestion.py ../seeds/kb"
echo "3. Start API: cd apps/api && source venv/bin/activate && uvicorn main:app --reload"
echo "4. Start Web: cd apps/web && npm run dev"
echo "5. Access: http://localhost:3000"

