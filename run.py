"""Run the World Cup 2026 Betting App."""
import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.models import init_db

if __name__ == '__main__':
    init_db()
    print("=" * 50)
    print("  World Cup 2026 Betting Pool")
    print("  Running on http://localhost:5000")
    print("  Admin login: admin")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
