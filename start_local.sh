#!/bin/bash
# Quick start script for Mindwhile ERP local development

echo "🚀 Starting Mindwhile ERP..."
echo ""

# Add MySQL to PATH
export PATH="/usr/local/mysql/bin:$PATH"

# Activate virtual environment
source venv/bin/activate

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️  Redis is not running. Starting Redis..."
    brew services start redis
    sleep 2
fi

# Check if MySQL is running
if ! mysqladmin ping -h localhost -u root -pSandyvenky@41 > /dev/null 2>&1; then
    echo "⚠️  MySQL is not running. Please start MySQL manually:"
    echo "   sudo /usr/local/mysql/support-files/mysql.server start"
    exit 1
fi

echo "✅ All services ready!"
echo ""
echo "📚 Starting FastAPI application..."
echo "   Docs: http://localhost:8000/docs"
echo "   ReDoc: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
