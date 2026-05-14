"""
Scoring engine for the Polla del Mundial 2026.

Scoring rules (FIFA 2026 - 48 teams, 12 groups):
- Group Stage matches: 1 pt for correct winner/draw prediction
- Group Stage classification (1st & 2nd): 2 pts in order, 1 pt out of order
- Group Stage 3rd place: 1 pt for correct 3rd place (8 best 3rds qualify to R32)
- Round of 32 (Dieciseisavos): 4 pts in order, 2 pts out of order
- Round of 16 (Octavos): 8 pts in order, 6 pts out of order
- Quarter Finals (Cuartos): 12 pts in order, 10 pts out of order
- Semi Finals / Final / Third (Semis): 16 pts in order, 14 pts out of order
- Champion: 48 pts
- Runner-up: 38 pts
- Third place: 28 pts
- Fourth place: 18 pts

Tournament format:
- 48 teams in 12 groups (A-L), 4 teams per group
- Top 2 per group qualify (24 teams)
- Best 8 third-place teams qualify (8 teams)
- 32 teams enter knockout stage starting at Round of 32 (Dieciseisavos)
- Knockout: R32 → R16 → QF → SF → Third Place Match → Final
"""
from models import (
    db, User, GroupMatch, GroupMatchPrediction,
    GroupStandingPrediction, GroupStandingResult,
    KnockoutMatch, KnockoutPrediction,
    FinalPrediction, FinalResult
)

# ──────────────────────────────────────────────
# TOURNAMENT PARAMETERS (FIFA 2026 format)
# ──────────────────────────────────────────────
TOTAL_TEAMS = 48
GROUPS_COUNT = 12
TEAMS_PER_GROUP = 4
QUALIFIED_PER_GROUP_TOP2 = 2  # 1st and 2nd qualify directly
BEST_THIRD_PLACES = 8         # 8 of 12 third-place teams also qualify
TOTAL_KNOCKOUT_TEAMS = 32     # 24 (top 2) + 8 (best 3rd) = 32
START_KNOCKOUT_AT = 'R32'     # Dieciseisavos de final
TOTAL_GROUP_MATCHES = 72      # 6 matches per group × 12 groups
TOTAL_KNOCKOUT_MATCHES = 32   # 16 + 8 + 4 + 2 + 1 + 1
TOTAL_MATCHES = 104           # 72 + 32

# Points per round for knockout stage
KNOCKOUT_POINTS = {
    'R32': {'in_order': 4, 'out_of_order': 2},
    'R16': {'in_order': 8, 'out_of_order': 6},
    'QF': {'in_order': 12, 'out_of_order': 10},
    'SF': {'in_order': 16, 'out_of_order': 14},
    'THIRD': {'in_order': 16, 'out_of_order': 14},
    'FINAL': {'in_order': 16, 'out_of_order': 14},
}

FINAL_POINTS = {
    'champion': 48,
    'runner_up': 38,
    'third': 28,
    'fourth': 18,
}

# Group standing points
GROUP_STANDING_IN_ORDER = 2    # Correct team in correct position (1st/2nd)
GROUP_STANDING_OUT_OF_ORDER = 1  # Correct team in wrong position (1st/2nd)
GROUP_THIRD_PLACE = 1          # Correct 3rd place prediction


def calculate_group_match_points(user_id):
    """
    Calculate points from group stage match predictions.
    1 point for each correct prediction (winner or draw).
    """
    points = 0
    details = []

    predictions = GroupMatchPrediction.query.filter_by(user_id=user_id).all()
    for pred in predictions:
        match = pred.match
        if match.result is not None:
            correct = pred.prediction == match.result
            if correct:
                points += 1
            details.append({
                'match': f'{match.team1_code} vs {match.team2_code}',
                'group': match.group_letter,
                'prediction': pred.prediction,
                'result': match.result,
                'correct': correct,
                'points': 1 if correct else 0,
            })

    return points, details


def calculate_group_standing_points(user_id):
    """
    Calculate points from group classification predictions.
    1st & 2nd place:
      - 2 pts for correct team in correct position (in order).
      - 1 pt for correct team in wrong position (out of order).
    3rd place:
      - 1 pt for correctly predicting the 3rd place team.
    """
    points = 0
    details = []

    predictions = GroupStandingPrediction.query.filter_by(user_id=user_id).all()
    for pred in predictions:
        result = GroupStandingResult.query.filter_by(group_letter=pred.group_letter).first()
        if result:
            pred_set = {pred.first_team_code, pred.second_team_code}
            result_set = {result.first_team_code, result.second_team_code}

            group_points = 0

            # 1st place check
            first_correct = pred.first_team_code == result.first_team_code
            if first_correct:
                group_points += GROUP_STANDING_IN_ORDER
            elif pred.first_team_code in result_set:
                group_points += GROUP_STANDING_OUT_OF_ORDER

            # 2nd place check
            second_correct = pred.second_team_code == result.second_team_code
            if second_correct:
                group_points += GROUP_STANDING_IN_ORDER
            elif pred.second_team_code in result_set:
                group_points += GROUP_STANDING_OUT_OF_ORDER

            # 3rd place check (new for FIFA 2026 - 8 best 3rds qualify)
            third_correct = False
            if pred.third_team_code and result.third_team_code:
                third_correct = pred.third_team_code == result.third_team_code
                if third_correct:
                    group_points += GROUP_THIRD_PLACE

            points += group_points
            details.append({
                'group': pred.group_letter,
                'predicted_1st': pred.first_team_code,
                'predicted_2nd': pred.second_team_code,
                'predicted_3rd': pred.third_team_code,
                'actual_1st': result.first_team_code,
                'actual_2nd': result.second_team_code,
                'actual_3rd': result.third_team_code,
                'third_correct': third_correct,
                'points': group_points,
            })

    return points, details


def calculate_knockout_points(user_id):
    """
    Calculate points from knockout stage predictions.
    Points vary by round (see KNOCKOUT_POINTS).
    'in order' = predicted team in correct bracket position.
    'out of order' = team is in the round but different position.
    """
    points = 0
    details = []

    # Get all predictions for this user
    predictions = KnockoutPrediction.query.filter_by(user_id=user_id).all()

    # Group predictions by round for out-of-order checking
    round_predictions = {}
    round_results = {}

    for pred in predictions:
        match = pred.match
        round_name = match.round_name
        if round_name not in round_predictions:
            round_predictions[round_name] = {}
            round_results[round_name] = {}

        if pred.winner_code:
            round_predictions[round_name][match.position] = pred.winner_code
        if match.winner_code:
            round_results[round_name][match.position] = match.winner_code

    # Calculate points per round
    for round_name, preds_by_pos in round_predictions.items():
        results_by_pos = round_results.get(round_name, {})
        if not results_by_pos:
            continue

        pts_config = KNOCKOUT_POINTS.get(round_name, {'in_order': 0, 'out_of_order': 0})
        all_result_winners = set(results_by_pos.values())

        for pos, pred_winner in preds_by_pos.items():
            actual_winner = results_by_pos.get(pos)
            if actual_winner is None:
                continue

            if pred_winner == actual_winner:
                # In order
                pts = pts_config['in_order']
                points += pts
                details.append({
                    'round': round_name,
                    'position': pos,
                    'predicted': pred_winner,
                    'actual': actual_winner,
                    'type': 'in_order',
                    'points': pts,
                })
            elif pred_winner in all_result_winners:
                # Out of order
                pts = pts_config['out_of_order']
                points += pts
                details.append({
                    'round': round_name,
                    'position': pos,
                    'predicted': pred_winner,
                    'actual': actual_winner,
                    'type': 'out_of_order',
                    'points': pts,
                })
            else:
                details.append({
                    'round': round_name,
                    'position': pos,
                    'predicted': pred_winner,
                    'actual': actual_winner,
                    'type': 'wrong',
                    'points': 0,
                })

    return points, details


def calculate_final_points(user_id):
    """
    Calculate points for final position predictions.
    Champion: 48 pts, Runner-up: 38 pts, Third: 28 pts, Fourth: 18 pts.
    """
    points = 0
    details = []

    pred = FinalPrediction.query.filter_by(user_id=user_id).first()
    result = FinalResult.query.first()

    if not pred or not result:
        return points, details

    checks = [
        ('champion', pred.champion_code, result.champion_code),
        ('runner_up', pred.runner_up_code, result.runner_up_code),
        ('third', pred.third_code, result.third_code),
        ('fourth', pred.fourth_code, result.fourth_code),
    ]

    for position, predicted, actual in checks:
        if predicted and actual and predicted == actual:
            pts = FINAL_POINTS[position]
            points += pts
            details.append({
                'position': position,
                'predicted': predicted,
                'actual': actual,
                'correct': True,
                'points': pts,
            })
        else:
            details.append({
                'position': position,
                'predicted': predicted,
                'actual': actual,
                'correct': False,
                'points': 0,
            })

    return points, details


def calculate_total_points(user_id):
    """Calculate total points for a user across all phases."""
    group_match_pts, group_match_details = calculate_group_match_points(user_id)
    group_standing_pts, group_standing_details = calculate_group_standing_points(user_id)
    knockout_pts, knockout_details = calculate_knockout_points(user_id)
    final_pts, final_details = calculate_final_points(user_id)

    total = group_match_pts + group_standing_pts + knockout_pts + final_pts

    return {
        'total': total,
        'group_matches': {'points': group_match_pts, 'details': group_match_details},
        'group_standings': {'points': group_standing_pts, 'details': group_standing_details},
        'knockout': {'points': knockout_pts, 'details': knockout_details},
        'finals': {'points': final_pts, 'details': final_details},
    }


def get_leaderboard():
    """Get sorted leaderboard with all users' total points."""
    users = User.query.filter_by(is_admin=False).all()
    leaderboard = []

    for user in users:
        scores = calculate_total_points(user.id)
        leaderboard.append({
            'user_id': user.id,
            'username': user.username,
            'total': scores['total'],
            'group_matches': scores['group_matches']['points'],
            'group_standings': scores['group_standings']['points'],
            'knockout': scores['knockout']['points'],
            'finals': scores['finals']['points'],
            'has_paid': user.has_paid,
        })

    leaderboard.sort(key=lambda x: x['total'], reverse=True)

    # Add ranking
    for i, entry in enumerate(leaderboard):
        entry['rank'] = i + 1

    return leaderboard
