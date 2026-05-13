import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'polla-mundial-2026-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///polla.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    
    # Deadline for predictions (June 9, 2026 - as specified in Excel)
    PREDICTION_DEADLINE = '2026-06-09T23:59:59'
    
    # App settings
    APP_NAME = 'Polla Mundial 2026'
    BET_AMOUNT = 250000  # COP
    PRIZE_FIRST = 0.80
    PRIZE_SECOND = 0.15
    PRIZE_THIRD = 0.05
