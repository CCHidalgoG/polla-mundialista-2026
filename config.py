import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'polla-mundial-2026-secret-key-change-in-production')
    
    # Database: support PostgreSQL (Supabase) and SQLite fallback for local dev
    _db_url = os.environ.get('DATABASE_URL', 'sqlite:///polla.db')
    # Supabase/Heroku use "postgres://" but SQLAlchemy 1.4+ requires "postgresql://"
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
    # Add SSL for remote PostgreSQL (required by Supabase)
    if 'postgresql' in _db_url and 'sslmode' not in _db_url:
        separator = '&' if '?' in _db_url else '?'
        _db_url += f'{separator}sslmode=require'
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
    
    # Tournament format (FIFA 2026 - 48 teams)
    TOTAL_TEAMS = 48
    GROUPS_COUNT = 12            # Groups A-L
    TEAMS_PER_GROUP = 4
    QUALIFIED_TOP2 = 24          # 1st & 2nd from each group
    BEST_THIRD_PLACES = 8        # Best 8 of 12 third-place teams
    TOTAL_KNOCKOUT_TEAMS = 32    # 24 + 8
    START_KNOCKOUT = 'R32'       # Dieciseisavos de final
    TOTAL_MATCHES = 104          # 72 group + 32 knockout
