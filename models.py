from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for players and admins."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active_user = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    has_paid = db.Column(db.Boolean, default=False)

    # Relationships
    group_match_predictions = db.relationship('GroupMatchPrediction', backref='user', lazy='dynamic')
    group_standing_predictions = db.relationship('GroupStandingPrediction', backref='user', lazy='dynamic')
    knockout_predictions = db.relationship('KnockoutPrediction', backref='user', lazy='dynamic')
    final_predictions = db.relationship('FinalPrediction', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return self.is_active_user

    def __repr__(self):
        return f'<User {self.username}>'


class Team(db.Model):
    """Team participating in the World Cup."""
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(5), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    group_letter = db.Column(db.String(1), nullable=False)
    flag_emoji = db.Column(db.String(10), default='🏳️')

    def __repr__(self):
        return f'<Team {self.code} ({self.name})>'


class GroupMatch(db.Model):
    """A group stage match between two teams."""
    __tablename__ = 'group_matches'

    id = db.Column(db.Integer, primary_key=True)
    group_letter = db.Column(db.String(1), nullable=False)
    matchday = db.Column(db.Integer, nullable=False)  # 1, 2, or 3
    match_number = db.Column(db.Integer, nullable=False)  # sequential within matchday
    team1_code = db.Column(db.String(5), db.ForeignKey('teams.code'), nullable=False)
    team2_code = db.Column(db.String(5), db.ForeignKey('teams.code'), nullable=False)
    match_date = db.Column(db.String(50), nullable=False)
    venue = db.Column(db.String(100), nullable=False)

    # Actual result (set by admin)
    result = db.Column(db.String(1), nullable=True)  # '1' = team1 wins, '2' = team2 wins, 'X' = draw

    team1 = db.relationship('Team', foreign_keys=[team1_code])
    team2 = db.relationship('Team', foreign_keys=[team2_code])

    def __repr__(self):
        return f'<GroupMatch {self.team1_code} vs {self.team2_code}>'


class GroupMatchPrediction(db.Model):
    """User's prediction for a group stage match."""
    __tablename__ = 'group_match_predictions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('group_matches.id'), nullable=False)
    prediction = db.Column(db.String(1), nullable=False)  # '1', '2', 'X'

    match = db.relationship('GroupMatch')

    __table_args__ = (db.UniqueConstraint('user_id', 'match_id'),)


class GroupStandingPrediction(db.Model):
    """User's prediction for final group standings (1st and 2nd place)."""
    __tablename__ = 'group_standing_predictions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_letter = db.Column(db.String(1), nullable=False)
    first_team_code = db.Column(db.String(5), db.ForeignKey('teams.code'), nullable=False)
    second_team_code = db.Column(db.String(5), db.ForeignKey('teams.code'), nullable=False)
    third_team_code = db.Column(db.String(5), db.ForeignKey('teams.code'), nullable=True)

    __table_args__ = (db.UniqueConstraint('user_id', 'group_letter'),)


class GroupStandingResult(db.Model):
    """Actual group standings (set by admin)."""
    __tablename__ = 'group_standing_results'

    id = db.Column(db.Integer, primary_key=True)
    group_letter = db.Column(db.String(1), unique=True, nullable=False)
    first_team_code = db.Column(db.String(5), db.ForeignKey('teams.code'), nullable=False)
    second_team_code = db.Column(db.String(5), db.ForeignKey('teams.code'), nullable=False)
    third_team_code = db.Column(db.String(5), db.ForeignKey('teams.code'), nullable=True)


class KnockoutMatch(db.Model):
    """A knockout stage match."""
    __tablename__ = 'knockout_matches'

    id = db.Column(db.Integer, primary_key=True)
    round_name = db.Column(db.String(30), nullable=False)  # 'R32', 'R16', 'QF', 'SF', 'THIRD', 'FINAL'
    position = db.Column(db.Integer, nullable=False)  # position in the bracket
    label = db.Column(db.String(10), nullable=False)  # e.g., 'G73', 'G89'
    team1_source = db.Column(db.String(30), nullable=False)  # e.g., '1E', '3ABCDF', 'G73'
    team2_source = db.Column(db.String(30), nullable=False)
    match_date = db.Column(db.String(50), nullable=True)
    venue = db.Column(db.String(100), nullable=True)

    # Actual result (set by admin)
    team1_code = db.Column(db.String(5), db.ForeignKey('teams.code'), nullable=True)
    team2_code = db.Column(db.String(5), db.ForeignKey('teams.code'), nullable=True)
    winner_code = db.Column(db.String(5), db.ForeignKey('teams.code'), nullable=True)


class KnockoutPrediction(db.Model):
    """User's prediction for a knockout match."""
    __tablename__ = 'knockout_predictions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('knockout_matches.id'), nullable=False)
    team1_code = db.Column(db.String(5), db.ForeignKey('teams.code'), nullable=True)
    team2_code = db.Column(db.String(5), db.ForeignKey('teams.code'), nullable=True)
    winner_code = db.Column(db.String(5), db.ForeignKey('teams.code'), nullable=True)

    match = db.relationship('KnockoutMatch')

    __table_args__ = (db.UniqueConstraint('user_id', 'match_id'),)


class FinalPrediction(db.Model):
    """User's prediction for champion, runner-up, third, and fourth place."""
    __tablename__ = 'final_predictions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    champion_code = db.Column(db.String(5), db.ForeignKey('teams.code'), nullable=True)
    runner_up_code = db.Column(db.String(5), db.ForeignKey('teams.code'), nullable=True)
    third_code = db.Column(db.String(5), db.ForeignKey('teams.code'), nullable=True)
    fourth_code = db.Column(db.String(5), db.ForeignKey('teams.code'), nullable=True)


class FinalResult(db.Model):
    """Actual final results (set by admin)."""
    __tablename__ = 'final_results'

    id = db.Column(db.Integer, primary_key=True)
    champion_code = db.Column(db.String(5), db.ForeignKey('teams.code'), nullable=True)
    runner_up_code = db.Column(db.String(5), db.ForeignKey('teams.code'), nullable=True)
    third_code = db.Column(db.String(5), db.ForeignKey('teams.code'), nullable=True)
    fourth_code = db.Column(db.String(5), db.ForeignKey('teams.code'), nullable=True)


class AppSetting(db.Model):
    """Application settings manageable by admin."""
    __tablename__ = 'app_settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(255), nullable=False)
