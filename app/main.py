"""World Cup 2026 Betting App - Main Flask Application."""
import os
import io
import csv
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, Response
from app.models import get_db, init_db
from app.game_data import TEAMS, GROUPS, FLAGS
from app.game_data2 import GROUP_MATCHES
from app.game_data3 import GROUP_MATCHES_2, KNOCKOUT_MATCHES
from app.third_place_data import THIRD_PLACE_TABLE
import psycopg2.extras

ALL_GROUP_MATCHES = GROUP_MATCHES + GROUP_MATCHES_2

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.environ.get('SECRET_KEY', 'worldcup2026-secret-key-change-in-prod')


@app.before_request
def before_request():
    init_db()


@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('bet_form'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_name = request.form.get('login', '').strip().lower()
        password = request.form.get('password', '').strip()
        if not login_name:
            flash('Please enter your login name.', 'error')
            return render_template('login.html')

        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM users WHERE login = %s", (login_name,))
        user = cur.fetchone()
        if not user:
            cur.execute(
                "INSERT INTO users (login, display_name) VALUES (%s, %s)",
                (login_name, login_name.title())
            )
            conn.commit()
            cur.execute("SELECT * FROM users WHERE login = %s", (login_name,))
            user = cur.fetchone()
        cur.close()
        conn.close()

        # Admin requires password
        if user['is_admin']:
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin2026')
            if password != admin_password:
                flash('Invalid admin password.', 'error')
                return render_template('login.html')

        session['user_id'] = user['id']
        session['login'] = user['login']
        session['display_name'] = user['display_name']
        session['is_admin'] = bool(user['is_admin'])

        if user['is_admin']:
            return redirect(url_for('admin_panel'))
        return redirect(url_for('bet_form'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/bet', methods=['GET'])
def bet_form():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM bets WHERE user_id = %s", (user_id,))
    bet = cur.fetchone()
    cur.close()
    conn.close()

    # Submitted AND no resubmit allowed = locked
    is_submitted = bet and bet['submitted'] and not bet.get('resubmit_allowed')
    is_resubmit = bet and bet['submitted'] and bet.get('resubmit_allowed')
    bet_data = json.loads(bet['bet_data']) if bet else {}

    return render_template('bet.html',
                           groups=GROUPS,
                           group_matches=ALL_GROUP_MATCHES,
                           knockout_matches=KNOCKOUT_MATCHES,
                           teams=TEAMS,
                           flags=FLAGS,
                           third_place_table=THIRD_PLACE_TABLE,
                           bet_data=bet_data,
                           is_submitted=is_submitted,
                           is_resubmit=is_resubmit,
                           user=session)


@app.route('/bet/save', methods=['POST'])
def save_bet():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    user_id = session['user_id']
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("SELECT * FROM bets WHERE user_id = %s", (user_id,))
    existing = cur.fetchone()
    if existing and existing['submitted'] and not existing.get('resubmit_allowed'):
        cur.close()
        conn.close()
        return jsonify({'error': 'Vote already submitted and locked. No changes allowed.'}), 403

    data = request.get_json()
    bet_data = json.dumps(data.get('bet_data', {}))

    if existing:
        cur.execute("UPDATE bets SET bet_data = %s WHERE user_id = %s", (bet_data, user_id))
    else:
        cur.execute("INSERT INTO bets (user_id, bet_data) VALUES (%s, %s)", (user_id, bet_data))

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'success': True, 'message': 'Vote saved (draft).'})


@app.route('/bet/submit', methods=['POST'])
def submit_bet():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    user_id = session['user_id']
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("SELECT * FROM bets WHERE user_id = %s", (user_id,))
    existing = cur.fetchone()
    if existing and existing['submitted'] and not existing.get('resubmit_allowed'):
        cur.close()
        conn.close()
        return jsonify({'error': 'Vote already submitted and locked.'}), 403

    data = request.get_json()
    bet_data = data.get('bet_data', {})

    # Validate all group matches have a prediction
    for match in ALL_GROUP_MATCHES:
        if match['id'] not in bet_data.get('matches', {}):
            cur.close()
            conn.close()
            return jsonify({'error': f"Missing prediction for {match['home']} vs {match['away']}"}), 400

    # Validate knockout matches
    for match in KNOCKOUT_MATCHES:
        if match['id'] not in bet_data.get('matches', {}):
            cur.close()
            conn.close()
            return jsonify({'error': f"Missing prediction for knockout match {match['match_num']}"}), 400

    bet_json = json.dumps(bet_data)
    now = datetime.now().isoformat()

    if existing:
        cur.execute(
            "UPDATE bets SET bet_data = %s, submitted = 1, submitted_at = %s, resubmit_allowed = 0 WHERE user_id = %s",
            (bet_json, now, user_id)
        )
    else:
        cur.execute(
            "INSERT INTO bets (user_id, bet_data, submitted, submitted_at, resubmit_allowed) VALUES (%s, %s, 1, %s, 0)",
            (user_id, bet_json, now)
        )

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'success': True, 'message': 'Vote submitted and locked! Good luck!'})


# ============ ADMIN ROUTES ============

@app.route('/admin')
def admin_panel():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Admin access required.', 'error')
        return redirect(url_for('login'))

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT u.login, u.display_name, b.submitted, b.submitted_at
        FROM users u LEFT JOIN bets b ON u.id = b.user_id
        WHERE u.is_admin = 0
        ORDER BY u.login
    """)
    users = cur.fetchall()

    cur.execute("SELECT * FROM admin_results")
    results = cur.fetchall()
    results_dict = {r['match_id']: r['result'] for r in results}

    cur.close()
    conn.close()

    return render_template('admin.html',
                           users=users,
                           results=results_dict,
                           groups=GROUPS,
                           group_matches=ALL_GROUP_MATCHES,
                           knockout_matches=KNOCKOUT_MATCHES,
                           teams=TEAMS,
                           flags=FLAGS,
                           third_place_table=THIRD_PLACE_TABLE)


@app.route('/admin/enter_result', methods=['POST'])
def enter_result():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()
    match_id = data.get('match_id')
    result = data.get('result')

    if not match_id or not result:
        return jsonify({'error': 'Invalid data'}), 400

    if not match_id.startswith('award_') and not match_id.startswith('tiebreaker_'):
        if result not in ['1', 'X', '2']:
            return jsonify({'error': 'Invalid result value'}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO admin_results (match_id, result) VALUES (%s, %s) ON CONFLICT (match_id) DO UPDATE SET result = %s",
        (match_id, result, result)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'success': True})


@app.route('/admin/clear_results', methods=['POST'])
def clear_results():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403

    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM admin_results")
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'success': True, 'message': 'All results cleared.'})


def _get_bets_and_results():
    """Helper to fetch all submitted bets and admin results."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT u.login, u.display_name, b.bet_data
        FROM users u JOIN bets b ON u.id = b.user_id
        WHERE b.submitted = 1
    """)
    bets = cur.fetchall()
    cur.execute("SELECT * FROM admin_results")
    results = cur.fetchall()
    results_dict = {r['match_id']: r['result'] for r in results}
    cur.close()
    conn.close()
    return bets, results_dict


# Points per phase
POINTS_MAP = {
    'group': 1,
    'R32': 4,
    'R16': 6,
    'QF': 10,
    'SF': 16,
    '3rd': 10,
    'Final': 25,
}


def _resolve_user_ko_winner(match, user_matches):
    """Resolve which team a user predicted to advance in a knockout match."""
    pred = user_matches.get(match['id'])
    if not pred:
        return None
    winner_code = match['home'] if pred == '1' else match['away']
    return _resolve_team_from_user(winner_code, user_matches)


def _resolve_team_from_user(code, user_matches):
    """Recursively resolve a bracket code to a team name based on user's predictions."""
    if not code:
        return None
    if code in FLAGS:
        return code
    import re
    # Group position: "1A", "2B"
    pos_match = re.match(r'^([12])([A-L])$', code)
    if pos_match:
        pos = int(pos_match.group(1))
        group = pos_match.group(2)
        return _calc_group_position_from_user(group, pos, user_matches)
    # 3rd place — too complex, skip
    if code.startswith('3'):
        return None
    # Winner of previous match
    win_match = re.match(r'^W(\d+)$', code)
    if win_match:
        match_num = int(win_match.group(1))
        m = next((x for x in KNOCKOUT_MATCHES if x['match_num'] == match_num), None)
        if m:
            return _resolve_user_ko_winner(m, user_matches)
    # Loser of previous match
    lose_match = re.match(r'^L(\d+)$', code)
    if lose_match:
        match_num = int(lose_match.group(1))
        m = next((x for x in KNOCKOUT_MATCHES if x['match_num'] == match_num), None)
        if m:
            pred = user_matches.get(m['id'])
            if not pred:
                return None
            loser_code = m['away'] if pred == '1' else m['home']
            return _resolve_team_from_user(loser_code, user_matches)
    return None


def _calc_group_position_from_user(group_letter, position, user_matches):
    """Calculate group standings from a user's predictions."""
    teams = GROUPS[group_letter]
    stats = {t: {'pts': 0, 'gd': 0, 'gf': 0, 'name': t} for t in teams}
    for m in ALL_GROUP_MATCHES:
        if m['group'] != group_letter:
            continue
        pred = user_matches.get(m['id'])
        if not pred:
            continue
        if pred == '1':
            stats[m['home']]['pts'] += 3; stats[m['home']]['gd'] += 1; stats[m['home']]['gf'] += 1; stats[m['away']]['gd'] -= 1
        elif pred == '2':
            stats[m['away']]['pts'] += 3; stats[m['away']]['gd'] += 1; stats[m['away']]['gf'] += 1; stats[m['home']]['gd'] -= 1
        else:
            stats[m['home']]['pts'] += 1; stats[m['away']]['pts'] += 1
    sorted_teams = sorted(stats.values(), key=lambda x: (x['pts'], x['gd'], x['gf']), reverse=True)
    if position <= len(sorted_teams):
        return sorted_teams[position - 1]['name']
    return None


def _resolve_actual_ko_winner(match, results_dict):
    """Resolve which team actually advanced in a knockout match based on admin results."""
    result = results_dict.get(match['id'])
    if not result:
        return None
    winner_code = match['home'] if result == '1' else match['away']
    return _resolve_team_from_admin(winner_code, results_dict)


def _resolve_team_from_admin(code, results_dict):
    """Recursively resolve a bracket code to a team name based on admin results."""
    if not code:
        return None
    if code in FLAGS:
        return code
    import re
    pos_match = re.match(r'^([12])([A-L])$', code)
    if pos_match:
        pos = int(pos_match.group(1))
        group = pos_match.group(2)
        # Use admin results for group standings
        teams = GROUPS[group]
        stats = {t: {'pts': 0, 'gd': 0, 'gf': 0, 'name': t} for t in teams}
        for m in ALL_GROUP_MATCHES:
            if m['group'] != group:
                continue
            r = results_dict.get(m['id'])
            if not r:
                continue
            if r == '1':
                stats[m['home']]['pts'] += 3; stats[m['home']]['gd'] += 1; stats[m['home']]['gf'] += 1; stats[m['away']]['gd'] -= 1
            elif r == '2':
                stats[m['away']]['pts'] += 3; stats[m['away']]['gd'] += 1; stats[m['away']]['gf'] += 1; stats[m['home']]['gd'] -= 1
            else:
                stats[m['home']]['pts'] += 1; stats[m['away']]['pts'] += 1
        # Check if admin set a tiebreaker order
        tb_key = f'tiebreaker_{group}'
        if tb_key in results_dict:
            order = results_dict[tb_key].split(',')
            if len(order) == 4 and pos <= 4:
                return order[pos - 1]
        sorted_teams = sorted(stats.values(), key=lambda x: (x['pts'], x['gd'], x['gf']), reverse=True)
        if pos <= len(sorted_teams):
            return sorted_teams[pos - 1]['name']
        return None
    if code.startswith('3'):
        return None  # 3rd place resolution too complex for scoring
    win_match = re.match(r'^W(\d+)$', code)
    if win_match:
        match_num = int(win_match.group(1))
        m = next((x for x in KNOCKOUT_MATCHES if x['match_num'] == match_num), None)
        if m:
            return _resolve_actual_ko_winner(m, results_dict)
    lose_match = re.match(r'^L(\d+)$', code)
    if lose_match:
        match_num = int(lose_match.group(1))
        m = next((x for x in KNOCKOUT_MATCHES if x['match_num'] == match_num), None)
        if m:
            result = results_dict.get(m['id'])
            if not result:
                return None
            loser_code = m['away'] if result == '1' else m['home']
            return _resolve_team_from_admin(loser_code, results_dict)
    return None


def _calc_scores_for_phase(phase, bets, results_dict):
    """Calculate scores for a given phase."""
    match_list = []
    if phase == 'group':
        match_list = [(m['id'], POINTS_MAP['group'], 'group') for m in ALL_GROUP_MATCHES]
    elif phase == 'R32':
        match_list = [(m['id'], POINTS_MAP['R32'], 'ko') for m in KNOCKOUT_MATCHES if m['phase'] == 'R32']
    elif phase == 'R16':
        match_list = [(m['id'], POINTS_MAP['R16'], 'ko') for m in KNOCKOUT_MATCHES if m['phase'] == 'R16']
    elif phase == 'QF':
        match_list = [(m['id'], POINTS_MAP['QF'], 'ko') for m in KNOCKOUT_MATCHES if m['phase'] == 'QF']
    elif phase == 'SF':
        match_list = [(m['id'], POINTS_MAP['SF'], 'ko') for m in KNOCKOUT_MATCHES if m['phase'] == 'SF']
    elif phase == 'Final':
        match_list = [(m['id'], POINTS_MAP.get(m['phase'], 5), 'ko') for m in KNOCKOUT_MATCHES if m['phase'] in ['Final', '3rd']]
    else:
        match_list = [(m['id'], POINTS_MAP['group'], 'group') for m in ALL_GROUP_MATCHES]
        match_list += [(m['id'], POINTS_MAP.get(m['phase'], 1), 'ko') for m in KNOCKOUT_MATCHES]

    # Pre-resolve actual KO winners from admin results
    actual_ko_winners = {}
    for m in KNOCKOUT_MATCHES:
        if m['id'] in results_dict:
            winner = _resolve_actual_ko_winner(m, results_dict)
            if winner:
                actual_ko_winners[m['id']] = winner

    scores = []
    for bet_row in bets:
        bet_data = json.loads(bet_row['bet_data'])
        user_matches = bet_data.get('matches', {})
        points = 0
        correct = 0
        total = 0

        for mid, weight, match_type in match_list:
            if mid not in results_dict:
                continue
            total += 1

            if match_type == 'group':
                # Group: simple 1/X/2 comparison
                if mid in user_matches and user_matches[mid] == results_dict[mid]:
                    points += weight
                    correct += 1
            else:
                # Knockout: compare which TEAM advances
                actual_winner = actual_ko_winners.get(mid)
                if not actual_winner:
                    continue
                # Resolve user's predicted winner for this match
                ko_match = next((m for m in KNOCKOUT_MATCHES if m['id'] == mid), None)
                if ko_match:
                    user_winner = _resolve_user_ko_winner(ko_match, user_matches)
                    if user_winner and user_winner == actual_winner:
                        points += weight
                        correct += 1

        awards_correct = 0
        if phase in ('all', 'Final', 'general'):
            user_awards = bet_data.get('awards', {})
            for award_key in ['golden_ball', 'golden_boot', 'golden_glove']:
                actual = results_dict.get(f'award_{award_key}')
                if actual and user_awards.get(award_key, '').strip().lower() == actual.strip().lower():
                    points += 10
                    awards_correct += 1

        scores.append({
            'login': bet_row['login'],
            'display_name': bet_row['display_name'],
            'points': points,
            'correct': correct,
            'total': total,
            'awards_correct': awards_correct,
            'pct': round(correct / total * 100, 1) if total > 0 else 0
        })

    scores.sort(key=lambda x: x['points'], reverse=True)
    return scores


@app.route('/admin/report/<phase>')
def admin_report(phase):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403

    bets, results_dict = _get_bets_and_results()
    scores = _calc_scores_for_phase(phase, bets, results_dict)
    return jsonify({'phase': phase, 'rankings': scores[:10], 'total_participants': len(scores)})


@app.route('/admin/report/general')
def admin_report_general():
    """General ranking: sum of points across all individual phases."""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403

    bets, results_dict = _get_bets_and_results()

    phases = ['group', 'R32', 'R16', 'QF', 'SF', 'Final']
    user_totals = {}
    for phase in phases:
        phase_scores = _calc_scores_for_phase(phase, bets, results_dict)
        for s in phase_scores:
            login = s['login']
            if login not in user_totals:
                user_totals[login] = {
                    'login': s['login'],
                    'display_name': s['display_name'],
                    'points': 0, 'correct': 0, 'total': 0
                }
            user_totals[login]['points'] += s['points']
            user_totals[login]['correct'] += s['correct']
            user_totals[login]['total'] += s['total']

    scores = list(user_totals.values())
    for s in scores:
        s['pct'] = round(s['correct'] / s['total'] * 100, 1) if s['total'] > 0 else 0
        s['awards_correct'] = 0

    scores.sort(key=lambda x: x['points'], reverse=True)
    return jsonify({'phase': 'general', 'rankings': scores[:10], 'total_participants': len(scores)})


@app.route('/admin/download/report/<phase>')
def download_report(phase):
    """Download report as CSV."""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403

    bets, results_dict = _get_bets_and_results()

    if phase == 'general':
        phases = ['group', 'R32', 'R16', 'QF', 'SF', 'Final']
        user_totals = {}
        for p in phases:
            phase_scores = _calc_scores_for_phase(p, bets, results_dict)
            for s in phase_scores:
                login = s['login']
                if login not in user_totals:
                    user_totals[login] = {
                        'login': s['login'], 'display_name': s['display_name'],
                        'points': 0, 'correct': 0, 'total': 0
                    }
                user_totals[login]['points'] += s['points']
                user_totals[login]['correct'] += s['correct']
                user_totals[login]['total'] += s['total']
        scores = list(user_totals.values())
        for s in scores:
            s['pct'] = round(s['correct'] / s['total'] * 100, 1) if s['total'] > 0 else 0
        scores.sort(key=lambda x: x['points'], reverse=True)
    else:
        scores = _calc_scores_for_phase(phase, bets, results_dict)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Rank', 'Player', 'Points', 'Correct', 'Total', 'Accuracy %'])
    for i, s in enumerate(scores):
        writer.writerow([i + 1, s['display_name'], s['points'], s['correct'], s['total'], s['pct']])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=report_{phase}.csv'}
    )


@app.route('/admin/download/bet/<login>')
def download_bet(login):
    """Download a user's submitted vote as CSV with resolved team names."""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT u.display_name, b.bet_data, b.submitted_at
        FROM users u JOIN bets b ON u.id = b.user_id
        WHERE u.login = %s AND b.submitted = 1
    """, (login,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return jsonify({'error': 'Vote not found'}), 404

    bet_data = json.loads(row['bet_data'])
    user_matches = bet_data.get('matches', {})
    awards = bet_data.get('awards', {})

    # Build a resolver for this user's predictions
    def resolve_team(code):
        """Resolve a bracket code to a team name based on user's predictions."""
        if not code:
            return code
        # Direct team name
        if code in FLAGS:
            return code
        # Group position: "1A", "2B"
        import re
        pos_match = re.match(r'^([12])([A-L])$', code)
        if pos_match:
            pos = int(pos_match.group(1))
            group = pos_match.group(2)
            return _calc_group_position(group, pos, user_matches)
        # 3rd place codes
        if code.startswith('3'):
            return code  # Too complex to resolve without full bracket, keep code
        # Winner/Loser of previous match
        win_match = re.match(r'^W(\d+)$', code)
        if win_match:
            match_num = int(win_match.group(1))
            return _get_user_match_winner(match_num, user_matches)
        lose_match = re.match(r'^L(\d+)$', code)
        if lose_match:
            match_num = int(lose_match.group(1))
            return _get_user_match_loser(match_num, user_matches)
        return code

    def _calc_group_position(group_letter, position, user_preds):
        """Calculate group standings from user's predictions."""
        teams = GROUPS[group_letter]
        stats = {t: {'pts': 0, 'gd': 0, 'gf': 0, 'name': t} for t in teams}
        for m in ALL_GROUP_MATCHES:
            if m['group'] != group_letter:
                continue
            pred = user_preds.get(m['id'])
            if not pred:
                continue
            if pred == '1':
                stats[m['home']]['pts'] += 3; stats[m['home']]['gd'] += 1; stats[m['home']]['gf'] += 1; stats[m['away']]['gd'] -= 1
            elif pred == '2':
                stats[m['away']]['pts'] += 3; stats[m['away']]['gd'] += 1; stats[m['away']]['gf'] += 1; stats[m['home']]['gd'] -= 1
            else:
                stats[m['home']]['pts'] += 1; stats[m['away']]['pts'] += 1
        sorted_teams = sorted(stats.values(), key=lambda x: (x['pts'], x['gd'], x['gf']), reverse=True)
        if position <= len(sorted_teams):
            return sorted_teams[position - 1]['name']
        return None

    def _get_user_match_winner(match_num, user_preds):
        """Get the winner of a knockout match based on user's prediction."""
        match = next((m for m in KNOCKOUT_MATCHES if m['match_num'] == match_num), None)
        if not match:
            return None
        pred = user_preds.get(match['id'])
        if not pred:
            return None
        winner_code = match['home'] if pred == '1' else match['away']
        return resolve_team(winner_code)

    def _get_user_match_loser(match_num, user_preds):
        """Get the loser of a knockout match based on user's prediction."""
        match = next((m for m in KNOCKOUT_MATCHES if m['match_num'] == match_num), None)
        if not match:
            return None
        pred = user_preds.get(match['id'])
        if not pred:
            return None
        loser_code = match['away'] if pred == '1' else match['home']
        return resolve_team(loser_code)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Player', row['display_name']])
    writer.writerow(['Submitted', row['submitted_at']])
    writer.writerow([])

    # Group matches
    writer.writerow(['Match ID', 'Home', 'Away', 'Prediction', 'Winner'])
    for m in ALL_GROUP_MATCHES:
        pred = user_matches.get(m['id'], '')
        if pred == '1':
            winner = m['home']
        elif pred == '2':
            winner = m['away']
        elif pred == 'X':
            winner = 'Draw'
        else:
            winner = ''
        writer.writerow([m['id'], m['home'], m['away'], pred, winner])

    # Knockout matches — resolve team names
    writer.writerow([])
    writer.writerow(['Match ID', 'Phase', 'Home', 'Away', 'Prediction', 'Advances'])
    for m in KNOCKOUT_MATCHES:
        pred = user_matches.get(m['id'], '')
        home_name = resolve_team(m['home']) or m['home']
        away_name = resolve_team(m['away']) or m['away']
        if pred == '1':
            advances = home_name
        elif pred == '2':
            advances = away_name
        else:
            advances = ''
        writer.writerow([m['id'], m['phase'], home_name, away_name, pred, advances])

    # Awards
    writer.writerow([])
    writer.writerow(['Award', 'Prediction'])
    for key in ['golden_ball', 'golden_boot', 'golden_glove']:
        writer.writerow([key, awards.get(key, '')])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=vote_{login}.csv'}
    )


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
