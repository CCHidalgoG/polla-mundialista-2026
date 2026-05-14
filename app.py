"""
Polla del Mundial 2026 - Main Flask Application
"""
import os
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from flask_wtf.csrf import CSRFProtect

from config import Config
from models import (
    db, User, Team, GroupMatch, GroupMatchPrediction,
    GroupStandingPrediction, GroupStandingResult,
    KnockoutMatch, KnockoutPrediction,
    FinalPrediction, FinalResult, AppSetting
)
from scoring import calculate_total_points, get_leaderboard

app = Flask(__name__)
app.config.from_object(Config)

csrf = CSRFProtect(app)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_required(f):
    """Decorator for admin-only routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acceso restringido a administradores.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def get_setting(key, default=None):
    """Get an app setting value."""
    setting = AppSetting.query.filter_by(key=key).first()
    return setting.value if setting else default


def predictions_open():
    """Check if predictions are still open."""
    deadline_str = get_setting('prediction_deadline', '2026-06-09T23:59:59')
    deadline = datetime.fromisoformat(deadline_str)
    return datetime.now() < deadline


# ──────────────────────────────────────────────
# CONTEXT PROCESSORS
# ──────────────────────────────────────────────

@app.context_processor
def inject_globals():
    return {
        'app_name': Config.APP_NAME,
        'predictions_open': predictions_open(),
        'now': datetime.now(),
    }


# ──────────────────────────────────────────────
# AUTH ROUTES
# ──────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            flash(f'¡Bienvenido, {user.username}!', 'success')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos.', 'error')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    reg_open = get_setting('registration_open', 'true')
    if reg_open != 'true':
        flash('El registro está cerrado.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')

        errors = []
        if len(username) < 3:
            errors.append('El nombre de usuario debe tener al menos 3 caracteres.')
        if '@' not in email:
            errors.append('Email inválido.')
        if len(password) < 4:
            errors.append('La contraseña debe tener al menos 4 caracteres.')
        if password != password2:
            errors.append('Las contraseñas no coinciden.')
        if User.query.filter_by(username=username).first():
            errors.append('Ese nombre de usuario ya está en uso.')
        if User.query.filter_by(email=email).first():
            errors.append('Ese email ya está registrado.')

        if errors:
            for error in errors:
                flash(error, 'error')
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            flash('¡Registro exitoso! Ya puedes llenar tus predicciones.', 'success')
            return redirect(url_for('dashboard'))

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('login'))


# ──────────────────────────────────────────────
# MAIN ROUTES
# ──────────────────────────────────────────────

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    leaderboard = get_leaderboard()
    user_scores = calculate_total_points(current_user.id) if not current_user.is_admin else None

    # Count user predictions completion
    total_group_matches = GroupMatch.query.count()
    user_group_preds = GroupMatchPrediction.query.filter_by(user_id=current_user.id).count() if not current_user.is_admin else 0
    total_groups = 12
    user_standing_preds = GroupStandingPrediction.query.filter_by(user_id=current_user.id).count() if not current_user.is_admin else 0
    total_knockout = KnockoutMatch.query.count()
    user_knockout_preds = KnockoutPrediction.query.filter_by(user_id=current_user.id).count() if not current_user.is_admin else 0
    has_final_pred = FinalPrediction.query.filter_by(user_id=current_user.id).first() is not None if not current_user.is_admin else False

    stats = {
        'group_matches': {'done': user_group_preds, 'total': total_group_matches},
        'group_standings': {'done': user_standing_preds, 'total': total_groups},
        'knockout': {'done': user_knockout_preds, 'total': total_knockout},
        'finals': {'done': 1 if has_final_pred else 0, 'total': 1},
    }

    total_users = User.query.filter_by(is_admin=False).count()
    bet_amount = int(get_setting('bet_amount', '250000'))
    prize_pool = total_users * bet_amount

    return render_template('dashboard.html',
                           leaderboard=leaderboard,
                           user_scores=user_scores,
                           stats=stats,
                           total_users=total_users,
                           prize_pool=prize_pool,
                           bet_amount=bet_amount)


# ──────────────────────────────────────────────
# PREDICTION ROUTES
# ──────────────────────────────────────────────

@app.route('/predictions/groups', methods=['GET', 'POST'])
@login_required
def predictions_groups():
    if current_user.is_admin:
        flash('Los administradores no participan en la polla.', 'info')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        if not predictions_open():
            flash('El plazo para predicciones ha cerrado.', 'error')
            return redirect(url_for('predictions_groups'))

        # Save match predictions
        matches = GroupMatch.query.order_by(GroupMatch.group_letter, GroupMatch.matchday, GroupMatch.match_number).all()
        for match in matches:
            pred_value = request.form.get(f'match_{match.id}')
            if pred_value and pred_value in ('1', '2', 'X'):
                pred = GroupMatchPrediction.query.filter_by(
                    user_id=current_user.id, match_id=match.id
                ).first()
                if pred:
                    pred.prediction = pred_value
                else:
                    pred = GroupMatchPrediction(
                        user_id=current_user.id,
                        match_id=match.id,
                        prediction=pred_value
                    )
                    db.session.add(pred)

        # Save group standing predictions (1st, 2nd, and 3rd place)
        groups = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        for group in groups:
            first = request.form.get(f'first_{group}')
            second = request.form.get(f'second_{group}')
            third = request.form.get(f'third_{group}')
            if first and second and first != second:
                standing = GroupStandingPrediction.query.filter_by(
                    user_id=current_user.id, group_letter=group
                ).first()
                if standing:
                    standing.first_team_code = first
                    standing.second_team_code = second
                    standing.third_team_code = third
                else:
                    standing = GroupStandingPrediction(
                        user_id=current_user.id,
                        group_letter=group,
                        first_team_code=first,
                        second_team_code=second,
                        third_team_code=third
                    )
                    db.session.add(standing)

        db.session.commit()
        flash('¡Predicciones de fase de grupos guardadas!', 'success')
        return redirect(url_for('predictions_groups'))

    # Load existing predictions
    matches = GroupMatch.query.order_by(GroupMatch.group_letter, GroupMatch.matchday, GroupMatch.match_number).all()
    existing_preds = {}
    for pred in GroupMatchPrediction.query.filter_by(user_id=current_user.id).all():
        existing_preds[pred.match_id] = pred.prediction

    existing_standings = {}
    for standing in GroupStandingPrediction.query.filter_by(user_id=current_user.id).all():
        existing_standings[standing.group_letter] = {
            'first': standing.first_team_code,
            'second': standing.second_team_code,
            'third': standing.third_team_code
        }

    # Organize matches by group
    groups_data = {}
    teams_by_group = {}
    for match in matches:
        if match.group_letter not in groups_data:
            groups_data[match.group_letter] = []
            teams = Team.query.filter_by(group_letter=match.group_letter).order_by(Team.code).all()
            teams_by_group[match.group_letter] = teams
        groups_data[match.group_letter].append(match)

    return render_template('predictions/groups.html',
                           groups_data=groups_data,
                           teams_by_group=teams_by_group,
                           existing_preds=existing_preds,
                           existing_standings=existing_standings)


@app.route('/predictions/knockout', methods=['GET', 'POST'])
@login_required
def predictions_knockout():
    if current_user.is_admin:
        flash('Los administradores no participan en la polla.', 'info')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        if not predictions_open():
            flash('El plazo para predicciones ha cerrado.', 'error')
            return redirect(url_for('predictions_knockout'))

        knockout_matches = KnockoutMatch.query.order_by(KnockoutMatch.round_name, KnockoutMatch.position).all()
        for match in knockout_matches:
            team1 = request.form.get(f'team1_{match.id}')
            team2 = request.form.get(f'team2_{match.id}')
            winner = request.form.get(f'winner_{match.id}')

            if winner:
                pred = KnockoutPrediction.query.filter_by(
                    user_id=current_user.id, match_id=match.id
                ).first()
                if pred:
                    pred.team1_code = team1
                    pred.team2_code = team2
                    pred.winner_code = winner
                else:
                    pred = KnockoutPrediction(
                        user_id=current_user.id,
                        match_id=match.id,
                        team1_code=team1,
                        team2_code=team2,
                        winner_code=winner
                    )
                    db.session.add(pred)

        db.session.commit()
        flash('¡Predicciones de fase eliminatoria guardadas!', 'success')
        return redirect(url_for('predictions_knockout'))

    # Load data
    knockout_matches = KnockoutMatch.query.order_by(KnockoutMatch.round_name, KnockoutMatch.position).all()
    existing_preds = {}
    for pred in KnockoutPrediction.query.filter_by(user_id=current_user.id).all():
        existing_preds[pred.match_id] = {
            'team1': pred.team1_code,
            'team2': pred.team2_code,
            'winner': pred.winner_code
        }

    teams = Team.query.order_by(Team.name).all()

    # Organize by round
    rounds_data = {}
    round_order = ['R32', 'R16', 'QF', 'SF', 'THIRD', 'FINAL']
    round_names = {
        'R32': 'Dieciseisavos de Final',
        'R16': 'Octavos de Final',
        'QF': 'Cuartos de Final',
        'SF': 'Semifinales',
        'THIRD': 'Tercer Puesto',
        'FINAL': 'Final',
    }

    for match in knockout_matches:
        rn = match.round_name
        if rn not in rounds_data:
            rounds_data[rn] = []
        rounds_data[rn].append(match)

    return render_template('predictions/knockout.html',
                           rounds_data=rounds_data,
                           round_order=round_order,
                           round_names=round_names,
                           existing_preds=existing_preds,
                           teams=teams)


@app.route('/predictions/finals', methods=['GET', 'POST'])
@login_required
def predictions_finals():
    if current_user.is_admin:
        flash('Los administradores no participan en la polla.', 'info')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        if not predictions_open():
            flash('El plazo para predicciones ha cerrado.', 'error')
            return redirect(url_for('predictions_finals'))

        champion = request.form.get('champion')
        runner_up = request.form.get('runner_up')
        third = request.form.get('third')
        fourth = request.form.get('fourth')

        # Validate all different
        selections = [champion, runner_up, third, fourth]
        if len(set(s for s in selections if s)) != len([s for s in selections if s]):
            flash('Todos los equipos deben ser diferentes.', 'error')
            return redirect(url_for('predictions_finals'))

        pred = FinalPrediction.query.filter_by(user_id=current_user.id).first()
        if pred:
            pred.champion_code = champion
            pred.runner_up_code = runner_up
            pred.third_code = third
            pred.fourth_code = fourth
        else:
            pred = FinalPrediction(
                user_id=current_user.id,
                champion_code=champion,
                runner_up_code=runner_up,
                third_code=third,
                fourth_code=fourth
            )
            db.session.add(pred)

        db.session.commit()
        flash('¡Predicciones finales guardadas!', 'success')
        return redirect(url_for('predictions_finals'))

    existing = FinalPrediction.query.filter_by(user_id=current_user.id).first()
    teams = Team.query.order_by(Team.name).all()

    return render_template('predictions/finals.html',
                           existing=existing,
                           teams=teams)


@app.route('/my-predictions')
@login_required
def my_predictions():
    """View all of current user's predictions and scores."""
    if current_user.is_admin:
        flash('Los administradores no participan en la polla.', 'info')
        return redirect(url_for('dashboard'))

    scores = calculate_total_points(current_user.id)

    # Get all predictions organized
    group_match_preds = GroupMatchPrediction.query.filter_by(user_id=current_user.id).all()
    group_standing_preds = GroupStandingPrediction.query.filter_by(user_id=current_user.id).all()
    knockout_preds = KnockoutPrediction.query.filter_by(user_id=current_user.id).all()
    final_pred = FinalPrediction.query.filter_by(user_id=current_user.id).first()

    teams_dict = {t.code: t for t in Team.query.all()}

    return render_template('my_predictions.html',
                           scores=scores,
                           group_match_preds=group_match_preds,
                           group_standing_preds=group_standing_preds,
                           knockout_preds=knockout_preds,
                           final_pred=final_pred,
                           teams=teams_dict)


# ──────────────────────────────────────────────
# ADMIN ROUTES
# ──────────────────────────────────────────────

@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    users = User.query.order_by(User.created_at.desc()).all()
    total_users = User.query.filter_by(is_admin=False).count()
    paid_users = User.query.filter_by(is_admin=False, has_paid=True).count()

    # Count results entered
    group_matches_with_result = GroupMatch.query.filter(GroupMatch.result.isnot(None)).count()
    total_group_matches = GroupMatch.query.count()
    knockout_with_result = KnockoutMatch.query.filter(KnockoutMatch.winner_code.isnot(None)).count()
    total_knockout = KnockoutMatch.query.count()

    return render_template('admin/panel.html',
                           users=users,
                           total_users=total_users,
                           paid_users=paid_users,
                           group_matches_with_result=group_matches_with_result,
                           total_group_matches=total_group_matches,
                           knockout_with_result=knockout_with_result,
                           total_knockout=total_knockout)


@app.route('/admin/results/groups', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_results_groups():
    if request.method == 'POST':
        matches = GroupMatch.query.all()
        for match in matches:
            result = request.form.get(f'result_{match.id}')
            if result in ('1', '2', 'X', ''):
                match.result = result if result else None

        # Save group standings (1st, 2nd, and 3rd place)
        groups = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        for group in groups:
            first = request.form.get(f'standing_first_{group}')
            second = request.form.get(f'standing_second_{group}')
            third = request.form.get(f'standing_third_{group}')
            if first and second:
                standing = GroupStandingResult.query.filter_by(group_letter=group).first()
                if standing:
                    standing.first_team_code = first
                    standing.second_team_code = second
                    standing.third_team_code = third
                else:
                    standing = GroupStandingResult(
                        group_letter=group,
                        first_team_code=first,
                        second_team_code=second,
                        third_team_code=third
                    )
                    db.session.add(standing)

        db.session.commit()
        flash('¡Resultados de fase de grupos actualizados!', 'success')
        return redirect(url_for('admin_results_groups'))

    matches = GroupMatch.query.order_by(GroupMatch.group_letter, GroupMatch.matchday, GroupMatch.match_number).all()
    groups_data = {}
    teams_by_group = {}
    for match in matches:
        if match.group_letter not in groups_data:
            groups_data[match.group_letter] = []
            teams = Team.query.filter_by(group_letter=match.group_letter).order_by(Team.code).all()
            teams_by_group[match.group_letter] = teams
        groups_data[match.group_letter].append(match)

    standing_results = {}
    for sr in GroupStandingResult.query.all():
        standing_results[sr.group_letter] = {
            'first': sr.first_team_code,
            'second': sr.second_team_code,
            'third': sr.third_team_code
        }

    return render_template('admin/results_groups.html',
                           groups_data=groups_data,
                           teams_by_group=teams_by_group,
                           standing_results=standing_results)


@app.route('/admin/results/knockout', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_results_knockout():
    if request.method == 'POST':
        matches = KnockoutMatch.query.all()
        for match in matches:
            team1 = request.form.get(f'team1_{match.id}')
            team2 = request.form.get(f'team2_{match.id}')
            winner = request.form.get(f'winner_{match.id}')
            match.team1_code = team1 if team1 else None
            match.team2_code = team2 if team2 else None
            match.winner_code = winner if winner else None

        db.session.commit()
        flash('¡Resultados de eliminatorias actualizados!', 'success')
        return redirect(url_for('admin_results_knockout'))

    knockout_matches = KnockoutMatch.query.order_by(KnockoutMatch.round_name, KnockoutMatch.position).all()
    teams = Team.query.order_by(Team.name).all()

    rounds_data = {}
    round_order = ['R32', 'R16', 'QF', 'SF', 'THIRD', 'FINAL']
    round_names = {
        'R32': 'Dieciseisavos de Final',
        'R16': 'Octavos de Final',
        'QF': 'Cuartos de Final',
        'SF': 'Semifinales',
        'THIRD': 'Tercer Puesto',
        'FINAL': 'Final',
    }

    for match in knockout_matches:
        rn = match.round_name
        if rn not in rounds_data:
            rounds_data[rn] = []
        rounds_data[rn].append(match)

    return render_template('admin/results_knockout.html',
                           rounds_data=rounds_data,
                           round_order=round_order,
                           round_names=round_names,
                           teams=teams)


@app.route('/admin/results/finals', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_results_finals():
    if request.method == 'POST':
        champion = request.form.get('champion')
        runner_up = request.form.get('runner_up')
        third = request.form.get('third')
        fourth = request.form.get('fourth')

        result = FinalResult.query.first()
        if result:
            result.champion_code = champion if champion else None
            result.runner_up_code = runner_up if runner_up else None
            result.third_code = third if third else None
            result.fourth_code = fourth if fourth else None
        else:
            result = FinalResult(
                champion_code=champion if champion else None,
                runner_up_code=runner_up if runner_up else None,
                third_code=third if third else None,
                fourth_code=fourth if fourth else None
            )
            db.session.add(result)

        db.session.commit()
        flash('¡Resultados finales actualizados!', 'success')
        return redirect(url_for('admin_results_finals'))

    result = FinalResult.query.first()
    teams = Team.query.order_by(Team.name).all()

    return render_template('admin/results_finals.html',
                           result=result,
                           teams=teams)


@app.route('/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('No puedes cambiar tu propio rol.', 'error')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f'Rol de {user.username} actualizado.', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/users/<int:user_id>/toggle-paid', methods=['POST'])
@login_required
@admin_required
def toggle_paid(user_id):
    user = User.query.get_or_404(user_id)
    user.has_paid = not user.has_paid
    db.session.commit()
    flash(f'Estado de pago de {user.username} actualizado.', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('No puedes eliminar un administrador.', 'error')
    else:
        # Delete all related predictions
        GroupMatchPrediction.query.filter_by(user_id=user.id).delete()
        GroupStandingPrediction.query.filter_by(user_id=user.id).delete()
        KnockoutPrediction.query.filter_by(user_id=user.id).delete()
        FinalPrediction.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        flash(f'Usuario {user.username} eliminado.', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/settings', methods=['POST'])
@login_required
@admin_required
def admin_settings():
    deadline = request.form.get('prediction_deadline')
    reg_open = request.form.get('registration_open', 'false')
    bet_amount = request.form.get('bet_amount', '250000')

    for key, value in [('prediction_deadline', deadline), ('registration_open', reg_open), ('bet_amount', bet_amount)]:
        if value:
            setting = AppSetting.query.filter_by(key=key).first()
            if setting:
                setting.value = value
            else:
                db.session.add(AppSetting(key=key, value=value))

    db.session.commit()
    flash('Configuración actualizada.', 'success')
    return redirect(url_for('admin_panel'))


# ──────────────────────────────────────────────
# API ROUTES (for dynamic UI updates)
# ──────────────────────────────────────────────

@app.route('/api/leaderboard')
@login_required
def api_leaderboard():
    return jsonify(get_leaderboard())


@app.route('/api/user/<int:user_id>/predictions')
@login_required
@admin_required
def api_user_predictions(user_id):
    """Admin can view any user's predictions."""
    scores = calculate_total_points(user_id)
    return jsonify(scores)


# ──────────────────────────────────────────────
# INIT & RUN
# ──────────────────────────────────────────────

def init_db():
    """Initialize database and seed data."""
    with app.app_context():
        db.create_all()
        
        # Auto-migrate: add third_team_code if missing (FIFA 2026 format)
        from sqlalchemy import text, inspect
        inspector = inspect(db.engine)
        
        for table_name in ['group_standing_predictions', 'group_standing_results']:
            columns = [col['name'] for col in inspector.get_columns(table_name)]
            if 'third_team_code' not in columns:
                try:
                    db.session.execute(text(
                        f'ALTER TABLE {table_name} ADD COLUMN third_team_code VARCHAR(5)'
                    ))
                    db.session.commit()
                    print(f'✅ Migrated {table_name}: added third_team_code')
                except Exception as e:
                    db.session.rollback()
                    print(f'⚠️ Migration {table_name}: {e}')
        
        from seed_data import seed_all
        seed_all()


# Initialize DB on import (needed for gunicorn on Render)
init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
