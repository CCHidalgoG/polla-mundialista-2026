import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'polla-mundial-2026-secret-key-change-in-production')
    
    # Database: support PostgreSQL (Supabase) and SQLite fallback for local dev
    _db_url = os.environ.get('DATABASE_URL', 'sqlite:///polla.db')
    # Supabase/Heroku use "postgres://" but SQLAlchemy 1.4+ requires "postgresql://"
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = _db_url
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,      # verify connections before use
        'pool_recycle': 300,        # recycle connections every 5 min
    }
    WTF_CSRF_ENABLED = True
    
    # Deadline for predictions (June 9, 2026 - as specified in Excel)
    PREDICTION_DEADLINE = '2026-06-09T23:59:59'
    
    # App settings
    APP_NAME = 'Polla Mundial 2026'
    BET_AMOUNT = 250000  # COP
    PRIZE_FIRST = 0.80
    PRIZE_SECOND = 0.15
    PRIZE_THIRD = 0.05
