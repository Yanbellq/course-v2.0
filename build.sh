# build.sh
set -o errexit

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "📦 Installing Node.js dependencies..."
npm install

echo "🔨 Building frontend assets with Gulp..."
npm run watch

echo "📁 Collecting static files..."
python manage.py collectstatic --no-input --clear

echo "✅ Build completed successfully!"
