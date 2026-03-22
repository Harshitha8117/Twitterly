#!/bin/bash
# ============================================
# TWITTERLY - SETUP AND RUN SCRIPT
# ============================================
set -e

echo "🐦 Setting up Twitterly..."

# 1. Install requirements
echo "📦 Installing dependencies..."
pip install Django scikit-learn nltk pandas numpy Pillow django-crispy-forms crispy-bootstrap5 joblib

# 2. Download NLTK data
echo "📚 Downloading NLTK data..."
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"

# 3. Run migrations
echo "🗄️ Running migrations..."
python manage.py makemigrations
python manage.py migrate

# 4. Create superuser
echo ""
echo "👤 Create admin account:"
python manage.py createsuperuser

# 5. Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null || true

# 6. Train ML model (optional, uses sample data)
echo ""
read -p "🤖 Train ML model now? (y/n): " train_ml
if [ "$train_ml" == "y" ]; then
    python ml_engine/train_model.py
fi

echo ""
echo "✅ Setup complete!"
echo "🚀 Starting server at http://127.0.0.1:8000"
echo "🛡️  Admin portal at http://127.0.0.1:8000/admin-portal/"
echo ""
python manage.py runserver
