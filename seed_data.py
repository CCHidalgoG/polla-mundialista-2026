"""Seed data for the Polla del Mundial 2026 application.
Contains all teams, groups, and match data extracted from the Excel file.
"""
from models import db, Team, GroupMatch, KnockoutMatch, User, AppSetting


def seed_teams():
    """Seed all 48 teams organized by groups."""
    teams_data = [
        # Group A
        ('MEX', 'México', 'A', '🇲🇽'),
        ('SAF', 'Sudáfrica', 'A', '🇿🇦'),
        ('RCS', 'Corea del Sur', 'A', '🇰🇷'),
        ('RCH', 'República Checa', 'A', '🇨🇿'),
        # Group B
        ('SUI', 'Suiza', 'B', '🇨🇭'),
        ('CAN', 'Canadá', 'B', '🇨🇦'),
        ('CAT', 'Catar', 'B', '🇶🇦'),
        ('BOS', 'Bosnia', 'B', '🇧🇦'),
        # Group C
        ('BRA', 'Brasil', 'C', '🇧🇷'),
        ('MAR', 'Marruecos', 'C', '🇲🇦'),
        ('ESC', 'Escocia', 'C', '🏴󠁧󠁢󠁳󠁣󠁴󠁿'),
        ('HAI', 'Haití', 'C', '🇭🇹'),
        # Group D
        ('USA', 'Estados Unidos', 'D', '🇺🇸'),
        ('PAR', 'Paraguay', 'D', '🇵🇾'),
        ('ATL', 'Australia', 'D', '🇦🇺'),
        ('TUR', 'Turquía', 'D', '🇹🇷'),
        # Group E
        ('ALE', 'Alemania', 'E', '🇩🇪'),
        ('ECU', 'Ecuador', 'E', '🇪🇨'),
        ('CDM', 'Costa de Marfil', 'E', '🇨🇮'),
        ('CUR', 'Curazao', 'E', '🇨🇼'),
        # Group F
        ('HOL', 'Holanda', 'F', '🇳🇱'),
        ('JAP', 'Japón', 'F', '🇯🇵'),
        ('TUN', 'Túnez', 'F', '🇹🇳'),
        ('SUE', 'Suecia', 'F', '🇸🇪'),
        # Group G
        ('BEL', 'Bélgica', 'G', '🇧🇪'),
        ('EGI', 'Egipto', 'G', '🇪🇬'),
        ('IRN', 'Irán', 'G', '🇮🇷'),
        ('NZL', 'Nueva Zelanda', 'G', '🇳🇿'),
        # Group H
        ('ESP', 'España', 'H', '🇪🇸'),
        ('URU', 'Uruguay', 'H', '🇺🇾'),
        ('ARS', 'Arabia Saudí', 'H', '🇸🇦'),
        ('CAV', 'Cabo Verde', 'H', '🇨🇻'),
        # Group I
        ('FRA', 'Francia', 'I', '🇫🇷'),
        ('NOR', 'Noruega', 'I', '🇳🇴'),
        ('SEN', 'Senegal', 'I', '🇸🇳'),
        ('IRK', 'Irak', 'I', '🇮🇶'),
        # Group J
        ('ARG', 'Argentina', 'J', '🇦🇷'),
        ('AUS', 'Austria', 'J', '🇦🇹'),
        ('ARL', 'Argelia', 'J', '🇩🇿'),
        ('JOR', 'Jordania', 'J', '🇯🇴'),
        # Group K
        ('POR', 'Portugal', 'K', '🇵🇹'),
        ('COL', 'Colombia', 'K', '🇨🇴'),
        ('UZB', 'Uzbekistán', 'K', '🇺🇿'),
        ('CON', 'Congo', 'K', '🇨🇬'),
        # Group L
        ('ING', 'Inglaterra', 'L', '🏴󠁧󠁢󠁥󠁮󠁧󠁿'),
        ('CRO', 'Croacia', 'L', '🇭🇷'),
        ('GHA', 'Ghana', 'L', '🇬🇭'),
        ('PAN', 'Panamá', 'L', '🇵🇦'),
    ]

    for code, name, group, flag in teams_data:
        team = Team.query.filter_by(code=code).first()
        if not team:
            team = Team(code=code, name=name, group_letter=group, flag_emoji=flag)
            db.session.add(team)
    db.session.commit()


def seed_group_matches():
    """Seed all 72 group stage matches (6 per group, 12 groups)."""
    # Each group has 6 matches across 3 matchdays
    # Format: (group, matchday, match_num, team1, team2, date_str, venue)
    matches_data = [
        # Group A
        ('A', 1, 1, 'MEX', 'SAF', 'Jun 11 14:00', 'Ciudad de México'),
        ('A', 1, 2, 'RCS', 'RCH', 'Jun 11 21:00', 'Guadalajara'),
        ('A', 2, 1, 'SAF', 'RCH', 'Jun 18 11:00', 'Atlanta'),
        ('A', 2, 2, 'MEX', 'RCS', 'Jun 18 20:00', 'Guadalajara'),
        ('A', 3, 1, 'MEX', 'RCH', 'Jun 24 20:00', 'Ciudad de México'),
        ('A', 3, 2, 'RCS', 'SAF', 'Jun 24 20:00', 'Monterrey'),
        # Group B
        ('B', 1, 1, 'CAN', 'BOS', 'Jun 12 14:00', 'Toronto'),
        ('B', 1, 2, 'SUI', 'CAT', 'Jun 13 14:00', 'San Francisco'),
        ('B', 2, 1, 'SUI', 'BOS', 'Jun 18 14:00', 'Los Ángeles'),
        ('B', 2, 2, 'CAN', 'CAT', 'Jun 18 17:00', 'Vancouver'),
        ('B', 3, 1, 'SUI', 'CAN', 'Jun 24 14:00', 'Vancouver'),
        ('B', 3, 2, 'CAT', 'BOS', 'Jun 24 14:00', 'Seattle'),
        # Group C
        ('C', 1, 1, 'BRA', 'MAR', 'Jun 13 17:00', 'NY/NJ'),
        ('C', 1, 2, 'ESC', 'HAI', 'Jun 13 17:00', 'Boston'),
        ('C', 2, 1, 'BRA', 'HAI', 'Jun 19 20:00', 'Filadelfia'),
        ('C', 2, 2, 'MAR', 'ESC', 'Jun 19 17:00', 'Boston'),
        ('C', 3, 1, 'BRA', 'ESC', 'Jun 24 17:00', 'Miami'),
        ('C', 3, 2, 'MAR', 'HAI', 'Jun 24 17:00', 'Atlanta'),
        # Group D
        ('D', 1, 1, 'USA', 'PAR', 'Jun 12 20:00', 'Los Ángeles'),
        ('D', 1, 2, 'ATL', 'TUR', 'Jun 13 23:00', 'Vancouver'),
        ('D', 2, 1, 'PAR', 'TUR', 'Jun 19 23:00', 'San Francisco'),
        ('D', 2, 2, 'USA', 'ATL', 'Jun 19 14:00', 'Seattle'),
        ('D', 3, 1, 'USA', 'TUR', 'Jun 25 21:00', 'Los Ángeles'),
        ('D', 3, 2, 'PAR', 'ATL', 'Jun 25 17:00', 'San Francisco'),
        # Group E
        ('E', 1, 1, 'ALE', 'CUR', 'Jun 14 12:00', 'Houston'),
        ('E', 1, 2, 'ECU', 'CDM', 'Jun 14 18:00', 'Filadelfia'),
        ('E', 2, 1, 'ALE', 'CDM', 'Jun 20 15:00', 'Toronto'),
        ('E', 2, 2, 'ECU', 'CUR', 'Jun 20 19:00', 'Kansas City'),
        ('E', 3, 1, 'ALE', 'ECU', 'Jun 26 15:00', 'NY/NJ'),
        ('E', 3, 2, 'CDM', 'CUR', 'Jun 26 15:00', 'Filadelfia'),
        # Group F
        ('F', 1, 1, 'HOL', 'JAP', 'Jun 14 15:00', 'Dallas'),
        ('F', 1, 2, 'TUN', 'SUE', 'Jun 14 21:00', 'Monterrey'),
        ('F', 2, 1, 'HOL', 'SUE', 'Jun 20 12:00', 'Houston'),
        ('F', 2, 2, 'JAP', 'TUN', 'Jun 20 23:00', 'Monterrey'),
        ('F', 3, 1, 'HOL', 'TUN', 'Jun 25 18:00', 'Kansas City'),
        ('F', 3, 2, 'JAP', 'SUE', 'Jun 25 18:00', 'Dallas'),
        # Group G
        ('G', 1, 1, 'BEL', 'EGI', 'Jun 15 14:00', 'Seattle'),
        ('G', 1, 2, 'IRN', 'NZL', 'Jun 15 20:00', 'Los Ángeles'),
        ('G', 2, 1, 'BEL', 'IRN', 'Jun 21 14:00', 'Los Ángeles'),
        ('G', 2, 2, 'EGI', 'NZL', 'Jun 21 20:00', 'Vancouver'),
        ('G', 3, 1, 'BEL', 'NZL', 'Jun 26 22:00', 'Vancouver'),
        ('G', 3, 2, 'EGI', 'IRN', 'Jun 26 22:00', 'Seattle'),
        # Group H
        ('H', 1, 1, 'ESP', 'CAV', 'Jun 15 11:00', 'Atlanta'),
        ('H', 1, 2, 'URU', 'ARS', 'Jun 15 17:00', 'Miami'),
        ('H', 2, 1, 'ESP', 'ARS', 'Jun 21 11:00', 'Atlanta'),
        ('H', 2, 2, 'URU', 'CAV', 'Jun 21 17:00', 'Miami'),
        ('H', 3, 1, 'ESP', 'URU', 'Jun 26 19:00', 'Guadalajara'),
        ('H', 3, 2, 'ARS', 'CAV', 'Jun 26 19:00', 'Houston'),
        # Group I
        ('I', 1, 1, 'FRA', 'SEN', 'Jun 16 14:00', 'NY/NJ'),
        ('I', 1, 2, 'NOR', 'IRK', 'Jun 16 17:00', 'Boston'),
        ('I', 2, 1, 'FRA', 'IRK', 'Jun 22 16:00', 'Filadelfia'),
        ('I', 2, 2, 'NOR', 'SEN', 'Jun 22 19:00', 'NY/NJ'),
        ('I', 3, 1, 'FRA', 'NOR', 'Jun 26 14:00', 'Boston'),
        ('I', 3, 2, 'SEN', 'IRK', 'Jun 26 14:00', 'Toronto'),
        # Group J
        ('J', 1, 1, 'ARG', 'JOR', 'Jun 16 20:00', 'Kansas City'),
        ('J', 1, 2, 'AUS', 'ARL', 'Jun 16 23:00', 'San Francisco'),
        ('J', 2, 1, 'ARG', 'ARL', 'Jun 22 12:00', 'Dallas'),
        ('J', 2, 2, 'ARL', 'JOR', 'Jun 22 23:00', 'San Francisco'),
        ('J', 3, 1, 'ARG', 'AUS', 'Jun 27 22:00', 'Dallas'),
        ('J', 3, 2, 'AUS', 'ARL', 'Jun 27 22:00', 'Kansas City'),
        # Group K
        ('K', 1, 1, 'POR', 'CON', 'Jun 17 12:00', 'Houston'),
        ('K', 1, 2, 'COL', 'UZB', 'Jun 17 21:00', 'Ciudad de México'),
        ('K', 2, 1, 'POR', 'UZB', 'Jun 23 12:00', 'Houston'),
        ('K', 2, 2, 'COL', 'CON', 'Jun 23 21:00', 'Guadalajara'),
        ('K', 3, 1, 'POR', 'COL', 'Jun 27 18:30', 'Miami'),
        ('K', 3, 2, 'UZB', 'CON', 'Jun 27 18:30', 'Atlanta'),
        # Group L
        ('L', 1, 1, 'ING', 'CRO', 'Jun 17 15:00', 'Dallas'),
        ('L', 1, 2, 'GHA', 'PAN', 'Jun 17 18:00', 'Toronto'),
        ('L', 2, 1, 'ING', 'GHA', 'Jun 23 15:00', 'Boston'),
        ('L', 2, 2, 'CRO', 'PAN', 'Jun 23 18:00', 'Toronto'),
        ('L', 3, 1, 'ING', 'PAN', 'Jun 27 16:00', 'NY/NJ'),
        ('L', 3, 2, 'CRO', 'GHA', 'Jun 27 16:00', 'Filadelfia'),
    ]

    for group, matchday, match_num, t1, t2, date_str, venue in matches_data:
        existing = GroupMatch.query.filter_by(
            group_letter=group, matchday=matchday, match_number=match_num
        ).first()
        if not existing:
            match = GroupMatch(
                group_letter=group,
                matchday=matchday,
                match_number=match_num,
                team1_code=t1,
                team2_code=t2,
                match_date=date_str,
                venue=venue
            )
            db.session.add(match)
    db.session.commit()


def seed_knockout_matches():
    """Seed knockout stage matches with bracket structure."""
    # Round of 32 (Dieciseisavos) - 16 matches
    knockout_data = [
        # Dieciseisavos - Block 1
        ('R32', 1, 'G73', '1E', '3ABCDF', 'Jun 29', 'Boston'),
        ('R32', 2, 'G74', '1I', '3CDFGH', 'Jun 30', 'NY/NJ'),
        ('R32', 3, 'G75', '2A', '2B', 'Jun 29', 'Los Ángeles'),
        ('R32', 4, 'G76', '1F', '2C', 'Jun 29', 'Monterrey'),
        # Dieciseisavos - Block 2
        ('R32', 5, 'G77', '2K', '2L', 'Jul 2', 'Toronto'),
        ('R32', 6, 'G78', '1H', '2J', 'Jul 2', 'Los Ángeles'),
        ('R32', 7, 'G79', '1D', '3BEFIJ', 'Jul 1', 'San Francisco'),
        ('R32', 8, 'G80', '1G', '3AEHIJ', 'Jul 1', 'Seattle'),
        # Dieciseisavos - Block 3
        ('R32', 9, 'G81', '1C', '2F', 'Jun 29', 'Houston'),
        ('R32', 10, 'G82', '2E', '2I', 'Jun 30', 'Dallas'),
        ('R32', 11, 'G83', '1A', '3CEFHI', 'Jun 30', 'Ciudad de México'),
        ('R32', 12, 'G84', '1L', '3EHIJKL', 'Jul 1', 'Atlanta'),
        # Dieciseisavos - Block 4
        ('R32', 13, 'G85', '1J', '2H', 'Jul 3', 'Miami'),
        ('R32', 14, 'G86', '2D', '2G', 'Jul 3', 'Dallas'),
        ('R32', 15, 'G87', '1B', '3EFGIJ', 'Jul 2', 'Vancouver'),
        ('R32', 16, 'G88', '1K', '3DEIJL', 'Jul 3', 'Kansas City'),
        # Octavos (Round of 16) - 8 matches
        ('R16', 1, 'G89', 'G73', 'G74', 'Jul 4', 'Filadelfia'),
        ('R16', 2, 'G90', 'G75', 'G76', 'Jul 4', 'Houston'),
        ('R16', 3, 'G91', 'G77', 'G78', 'Jul 6', 'Dallas'),
        ('R16', 4, 'G92', 'G79', 'G80', 'Jul 6', 'Seattle'),
        ('R16', 5, 'G93', 'G81', 'G82', 'Jul 5', 'NY/NJ'),
        ('R16', 6, 'G94', 'G83', 'G84', 'Jul 5', 'Ciudad de México'),
        ('R16', 7, 'G95', 'G85', 'G86', 'Jul 7', 'Atlanta'),
        ('R16', 8, 'G96', 'G87', 'G88', 'Jul 7', 'Vancouver'),
        # Cuartos (Quarter Finals) - 4 matches
        ('QF', 1, 'G101', 'G89', 'G90', 'Jul 9', 'Boston'),
        ('QF', 2, 'G102', 'G91', 'G92', 'Jul 10', 'Los Ángeles'),
        ('QF', 3, 'G103', 'G93', 'G94', 'Jul 11', 'Miami'),
        ('QF', 4, 'G104', 'G95', 'G96', 'Jul 11', 'Kansas City'),
        # Semifinales - 2 matches
        ('SF', 1, 'G105', 'G101', 'G102', 'Jul 14', 'Dallas'),
        ('SF', 2, 'G106', 'G103', 'G104', 'Jul 15', 'Atlanta'),
        # Tercer puesto
        ('THIRD', 1, 'P3RD', 'LG105', 'LG106', 'Jul 18', 'Miami'),
        # Final
        ('FINAL', 1, 'FINAL', 'WG105', 'WG106', 'Jul 19', 'NY/NJ'),
    ]

    for round_name, pos, label, src1, src2, date_str, venue in knockout_data:
        existing = KnockoutMatch.query.filter_by(label=label).first()
        if not existing:
            match = KnockoutMatch(
                round_name=round_name,
                position=pos,
                label=label,
                team1_source=src1,
                team2_source=src2,
                match_date=date_str,
                venue=venue
            )
            db.session.add(match)
    db.session.commit()


def seed_admin():
    """Create default admin user if none exists."""
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@polla2026.com',
            is_admin=True,
            has_paid=True
        )
        admin.set_password('admin2026')
        db.session.add(admin)
        db.session.commit()
        print('✅ Admin user created: admin / admin2026')


def seed_settings():
    """Seed default app settings."""
    defaults = {
        'prediction_deadline': '2026-06-09T23:59:59',
        'registration_open': 'true',
        'bet_amount': '250000',
    }
    for key, value in defaults.items():
        existing = AppSetting.query.filter_by(key=key).first()
        if not existing:
            db.session.add(AppSetting(key=key, value=value))
    db.session.commit()


def seed_all():
    """Run all seed functions."""
    print('🌱 Seeding teams...')
    seed_teams()
    print('🌱 Seeding group matches...')
    seed_group_matches()
    print('🌱 Seeding knockout matches...')
    seed_knockout_matches()
    print('🌱 Seeding admin user...')
    seed_admin()
    print('🌱 Seeding settings...')
    seed_settings()
    print('✅ All data seeded successfully!')
