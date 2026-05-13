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
        user = conn.execute("SELECT * FROM users WHERE login = ?", (login_name,)).fetchone()
        if not user:
            # Auto-register new users
            conn.execute(
                "INSERT INTO users (login, display_name) VALUES (?, ?)",
                (login_name, login_name.title())
            )
            conn.commit()
            user = conn.execute("SELECT * FROM users WHERE login = ?", (login_name,)).fetchone()
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
    bet = conn.execute("SELECT * FROM bets WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()

    is_submitted = bet and bet['submitted']
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
                           user=session)


@app.route('/bet/save', methods=['POST'])
def save_bet():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    user_id = session['user_id']
    conn = get_db()

    # Check if already submitted
    existing = conn.execute("SELECT * FROM bets WHERE user_id = ?", (user_id,)).fetchone()
    if existing and existing['submitted']:
        conn.close()
        return jsonify({'error': 'Vote already submitted and locked. No changes allowed.'}), 403

    data = request.get_json()
    bet_data = json.dumps(data.get('bet_data', {}))

    if existing:
        conn.execute("UPDATE bets SET bet_data = ? WHERE user_id = ?", (bet_data, user_id))
    else:
        conn.execute("INSERT INTO bets (user_id, bet_data) VALUES (?, ?)", (user_id, bet_data))

    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Vote saved (draft).'})


@app.route('/bet/submit', methods=['POST'])
def submit_bet():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    user_id = session['user_id']
    conn = get_db()

    existing = conn.execute("SELECT * FROM bets WHERE user_id = ?", (user_id,)).fetchone()
    if existing and existing['submitted']:
        conn.close()
        return jsonify({'error': 'Vote already submitted and locked.'}), 403

    data = request.get_json()
    bet_data = data.get('bet_data', {})

    # Validate all group matches have a prediction
    for match in ALL_GROUP_MATCHES:
        if match['id'] not in bet_data.get('matches', {}):
            conn.close()
            return jsonify({'error': f"Missing prediction for {match['home']} vs {match['away']}"}), 400

    # Validate knockout matches
    for match in KNOCKOUT_MATCHES:
        if match['id'] not in bet_data.get('matches', {}):
            conn.close()
            return jsonify({'error': f"Missing prediction for knockout match {match['match_num']}"}), 400

    bet_json = json.dumps(bet_data)
    now = datetime.now().isoformat()

    if existing:
        conn.execute(
            "UPDATE bets SET bet_data = ?, submitted = 1, submitted_at = ? WHERE user_id = ?",
            (bet_json, now, user_id)
        )
    else:
        conn.execute(
            "INSERT INTO bets (user_id, bet_data, submitted, submitted_at) VALUES (?, ?, 1, ?)",
            (user_id, bet_json, now)
        )

    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Vote submitted and locked! Good luck!'})


# ============ ADMIN ROUTES ============

@app.route('/admin')
def admin_panel():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Admin access required.', 'error')
        return redirect(url_for('login'))

    conn = get_db()
    users = conn.execute("""
        SELECT u.login, u.display_name, b.submitted, b.submitted_at
        FROM users u LEFT JOIN bets b ON u.id = b.user_id
        WHERE u.is_admin = 0
        ORDER BY u.login
    """).fetchall()

    # Get admin results
    results = conn.execute("SELECT * FROM admin_results").fetchall()
    results_dict = {r['match_id']: r['result'] for r in results}

    conn.close()

    return render_template('admin.html',
                           users=users,
                           results=results_dict,
                           groups=GROUPS,
                           group_matches=ALL_GROUP_MATCHES,
                           knockout_matches=KNOCKOUT_MATCHES,
                           teams=TEAMS,
                           flags=FLAGS)


@app.route('/admin/enter_result', methods=['POST'])
def enter_result():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()
    match_id = data.get('match_id')
    result = data.get('result')

    if not match_id or not result:
        return jsonify({'error': 'Invalid data'}), 400

    # For regular matches, validate 1/X/2; for awards, accept any text
    if not match_id.startswith('award_'):
        if result not in ['1', 'X', '2']:
            return jsonify({'error': 'Invalid result value'}), 400

    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO admin_results (match_id, result) VALUES (?, ?)",
        (match_id, result)
    )
    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route('/admin/clear_results', methods=['POST'])
def clear_results():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403

    conn = get_db()
    conn.execute("DELETE FROM admin_results")
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'All results cleared.'})


@app.route('/admin/report/<phase>')
def admin_report(phase):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403

    conn = get_db()

    # Get all submitted bets
    bets = conn.execute("""
        SELECT u.login, u.display_name, b.bet_data
        FROM users u JOIN bets b ON u.id = b.user_id
        WHERE b.submitted = 1
    """).fetchall()

    # Get actual results
    results = conn.execute("SELECT * FROM admin_results").fetchall()
    results_dict = {r['match_id']: r['result'] for r in results}
    conn.close()

    # Points per phase
    POINTS_MAP = {
        'group': 1,    # group stage match
        'R32': 4,      # round of 32
        'R16': 6,      # round of 16
        'QF': 10,      # quarter-finals
        'SF': 16,      # semi-finals
        '3rd': 10,     # third place
        'Final': 25,   # final
    }

    # Build match list with weights based on requested phase
    match_list = []  # list of (match_id, weight)
    if phase == 'group':
        match_list = [(m['id'], POINTS_MAP['group']) for m in ALL_GROUP_MATCHES]
    elif phase == 'R32':
        match_list = [(m['id'], POINTS_MAP['R32']) for m in KNOCKOUT_MATCHES if m['phase'] == 'R32']
    elif phase == 'R16':
        match_list = [(m['id'], POINTS_MAP['R16']) for m in KNOCKOUT_MATCHES if m['phase'] == 'R16']
    elif phase == 'QF':
        match_list = [(m['id'], POINTS_MAP['QF']) for m in KNOCKOUT_MATCHES if m['phase'] == 'QF']
    elif phase == 'SF':
        match_list = [(m['id'], POINTS_MAP['SF']) for m in KNOCKOUT_MATCHES if m['phase'] == 'SF']
    elif phase == 'Final':
        match_list = [(m['id'], POINTS_MAP.get(m['phase'], 5)) for m in KNOCKOUT_MATCHES if m['phase'] in ['Final', '3rd']]
    else:
        # All matches
        match_list = [(m['id'], POINTS_MAP['group']) for m in ALL_GROUP_MATCHES]
        match_list += [(m['id'], POINTS_MAP.get(m['phase'], 1)) for m in KNOCKOUT_MATCHES]

    # Calculate scores
    scores = []
    for bet_row in bets:
        bet_data = json.loads(bet_row['bet_data'])
        user_matches = bet_data.get('matches', {})
        points = 0
        correct = 0
        total = 0

        for mid, weight in match_list:
            if mid in results_dict:
                total += 1
                if mid in user_matches and user_matches[mid] == results_dict[mid]:
                    points += weight
                    correct += 1

        # Golden awards scoring (10 pts each, only in 'all' or 'Final' phase)
        awards_correct = 0
        if phase in ('all', 'Final'):
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

    # Sort by points descending
    scores.sort(key=lambda x: x['points'], reverse=True)

    # Return top 10
    return jsonify({'phase': phase, 'rankings': scores[:10], 'total_participants': len(scores)})


# Points per phase (used by report and download)
POINTS_MAP = {
    'group': 1,
    'R32': 4,
    'R16': 6,
    'QF': 10,
    'SF': 16,
    '3rd': 10,
    'Final': 25,
}


def _calc_scores_for_phase(phase, bets, results_dict):
    """Calculate scores for a given phase. Returns list of score dicts."""
    match_list = []
    if phase == 'group':
        match_list = [(m['id'], POINTS_MAP['group']) for m in ALL_GROUP_MATCHES]
    elif phase == 'R32':
        match_list = [(m['id'], POINTS_MAP['R32']) for m in KNOCKOUT_MATCHES if m['phase'] == 'R32']
    elif phase == 'R16':
        match_list = [(m['id'], POINTS_MAP['R16']) for m in KNOCKOUT_MATCHES if m['phase'] == 'R16']
    elif phase == 'QF':
        match_list = [(m['id'], POINTS_MAP['QF']) for m in KNOCKOUT_MATCHES if m['phase'] == 'QF']
    elif phase == 'SF':
        match_list = [(m['id'], POINTS_MAP['SF']) for m in KNOCKOUT_MATCHES if m['phase'] == 'SF']
    elif phase == 'Final':
        match_list = [(m['id'], POINTS_MAP.get(m['phase'], 5)) for m in KNOCKOUT_MATCHES if m['phase'] in ['Final', '3rd']]
    else:
        match_list = [(m['id'], POINTS_MAP['group']) for m in ALL_GROUP_MATCHES]
        match_list += [(m['id'], POINTS_MAP.get(m['phase'], 1)) for m in KNOCKOUT_MATCHES]

    scores = []
    for bet_row in bets:
        bet_data = json.loads(bet_row['bet_data'])
        user_matches = bet_data.get('matches', {})
        points = 0
        correct = 0
        total = 0

        for mid, weight in match_list:
            if mid in results_dict:
                total += 1
                if mid in user_matches and user_matches[mid] == results_dict[mid]:
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


@app.route('/admin/report/general')
def admin_report_general():
    """General ranking: sum of points across all individual phases."""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403

    conn = get_db()
    bets = conn.execute("""
        SELECT u.login, u.display_name, b.bet_data
        FROM users u JOIN bets b ON u.id = b.user_id
        WHERE b.submitted = 1
    """).fetchall()
    results = conn.execute("SELECT * FROM admin_results").fetchall()
    results_dict = {r['match_id']: r['result'] for r in results}
    conn.close()

    phases = ['group', 'R32', 'R16', 'QF', 'SF', 'Final']
    # Calculate per-user totals across all phases
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

    conn = get_db()
    bets = conn.execute("""
        SELECT u.login, u.display_name, b.bet_data
        FROM users u JOIN bets b ON u.id = b.user_id
        WHERE b.submitted = 1
    """).fetchall()
    results = conn.execute("SELECT * FROM admin_results").fetchall()
    results_dict = {r['match_id']: r['result'] for r in results}
    conn.close()

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
    """Download a user's submitted bet as CSV."""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403

    conn = get_db()
    row = conn.execute("""
        SELECT u.display_name, b.bet_data, b.submitted_at
        FROM users u JOIN bets b ON u.id = b.user_id
        WHERE u.login = ? AND b.submitted = 1
    """, (login,)).fetchone()
    conn.close()

    if not row:
        return jsonify({'error': 'Bet not found'}), 404

    bet_data = json.loads(row['bet_data'])
    matches = bet_data.get('matches', {})
    awards = bet_data.get('awards', {})

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Player', row['display_name']])
    writer.writerow(['Submitted', row['submitted_at']])
    writer.writerow([])
    writer.writerow(['Match ID', 'Home', 'Away', 'Prediction'])

    # Group matches
    for m in ALL_GROUP_MATCHES:
        pred = matches.get(m['id'], '')
        writer.writerow([m['id'], m['home'], m['away'], pred])

    # Knockout matches
    for m in KNOCKOUT_MATCHES:
        pred = matches.get(m['id'], '')
        writer.writerow([m['id'], m['home'], m['away'], pred])

    # Awards
    writer.writerow([])
    writer.writerow(['Award', 'Prediction'])
    for key in ['golden_ball', 'golden_boot', 'golden_glove']:
        writer.writerow([key, awards.get(key, '')])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=bet_{login}.csv'}
    )


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
