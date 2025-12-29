"""
Keer AI - Real-Time Web Admin Dashboard
Password protected - Key: Keer

Run: python web_dashboard.py
Open: http://localhost:5000
"""

from flask import Flask, render_template_string, request, redirect, url_for, jsonify, flash, session
import sqlite3
import os
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = 'keer-admin-secret-2024-secure'

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "app.db")
SUPPORT_EMAIL = "ytahmedytjb@gmail.com"
CREATED_BY = "Ahmed Jaballah"
WEB_KEY = "Keer"  # Dashboard access key

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Login page
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>🔐 Keer AI - Admin Login</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1a1b26, #24283b);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-box {
            background: rgba(36, 40, 59, 0.95);
            border: 1px solid rgba(122, 162, 247, 0.3);
            border-radius: 16px;
            padding: 40px;
            width: 100%;
            max-width: 400px;
            text-align: center;
        }
        h1 { color: #7aa2f7; margin-bottom: 30px; font-size: 24px; }
        input {
            width: 100%;
            padding: 15px;
            background: rgba(65, 72, 104, 0.6);
            border: 1px solid rgba(122, 162, 247, 0.3);
            border-radius: 8px;
            color: #c0caf5;
            font-size: 16px;
            margin-bottom: 20px;
        }
        input:focus { outline: none; border-color: #7aa2f7; }
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #7aa2f7, #bb9af7);
            border: none;
            border-radius: 8px;
            color: #1a1b26;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }
        button:hover { opacity: 0.9; }
        .error { color: #f7768e; margin-bottom: 20px; }
        .footer { color: #565f89; margin-top: 30px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>🔐 Keer AI Admin</h1>
        {% if error %}<p class="error">{{ error }}</p>{% endif %}
        <form method="POST">
            <input type="password" name="key" placeholder="Enter Access Key" required autofocus>
            <button type="submit">🔓 Access Dashboard</button>
        </form>
        <p class="footer">Created by {{ created_by }}</p>
    </div>
</body>
</html>
"""



DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="10"> <!-- Refresh every 10s -->
    <title>🛡️ KEER AI - Premium Admin</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0f111a;
            --card-bg: rgba(26, 27, 38, 0.6);
            --card-border: rgba(122, 162, 247, 0.2);
            --text-primary: #c0caf5;
            --text-secondary: #565f89;
            --accent: #7aa2f7;
            --accent-glow: rgba(122, 162, 247, 0.4);
            --success: #9ece6a;
            --error: #f7768e;
            --warning: #e0af68;
            --info: #0db9d7;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-color);
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(122, 162, 247, 0.05) 0%, transparent 20%),
                radial-gradient(circle at 90% 80%, rgba(187, 154, 247, 0.05) 0%, transparent 20%);
            color: var(--text-primary);
            min-height: 100vh;
            padding-bottom: 50px;
        }

        /* Glassmorphism Header */
        .header {
            background: rgba(15, 17, 26, 0.85);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--card-border);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        }

        .header h1 {
            font-weight: 700;
            font-size: 22px;
            background: linear-gradient(90deg, #7aa2f7, #bb9af7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 0.5px;
        }

        .header-right { display: flex; align-items: center; gap: 20px; }

        .status-pill {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            border-radius: 20px;
            background: rgba(26, 27, 38, 0.8);
            border: 1px solid var(--card-border);
            font-size: 13px;
        }

        .dot { width: 8px; height: 8px; border-radius: 50%; }
        .dot.green { background: var(--success); box-shadow: 0 0 8px var(--success); }
        .dot.red { background: var(--error); box-shadow: 0 0 8px var(--error); }
        .dot.pulse { animation: pulse 2s infinite; }

        @keyframes pulse { 0% { opacity: 0.6; transform: scale(0.9); } 50% { opacity: 1; transform: scale(1.1); } 100% { opacity: 0.6; transform: scale(0.9); } }

        .container {
            max-width: 1400px;
            margin: 30px auto;
            padding: 0 20px;
        }

        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 20px;
            text-align: center;
            transition: transform 0.3s ease, border-color 0.3s ease;
            backdrop-filter: blur(5px);
        }
        .stat-card:hover {
            transform: translateY(-5px);
            border-color: var(--accent);
            box-shadow: 0 10px 30px -10px var(--accent-glow);
        }

        .stat-num {
            font-size: 32px;
            font-weight: 700;
            color: #fff;
            margin-bottom: 5px;
        }
        .stat-label {
            font-size: 13px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Sections */
        .card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 25px;
            backdrop-filter: blur(5px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            padding-bottom: 15px;
        }

        .card h2 {
            font-size: 18px;
            color: var(--accent);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        /* Buttons */
        .btn {
            padding: 10px 20px;
            border-radius: 8px;
            border: none;
            font-weight: 600;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            color: #0f111a;
        }
        .btn-primary { background: linear-gradient(135deg, #7aa2f7, #bb9af7); color: #0f111a; }
        .btn-primary:hover { opacity: 0.9; transform: translateY(-2px); box-shadow: 0 4px 15px var(--accent-glow); }
        
        .btn-danger { background: rgba(247, 118, 142, 0.1); border: 1px solid var(--error); color: var(--error); }
        .btn-danger:hover { background: var(--error); color: #fff; }

        .btn-success { background: rgba(158, 206, 106, 0.1); border: 1px solid var(--success); color: var(--success); }
        .btn-success:hover { background: var(--success); color: #fff; }

        .btn-warning { background: rgba(224, 175, 104, 0.1); border: 1px solid var(--warning); color: var(--warning); }
        .btn-warning:hover { background: var(--warning); color: #fff; }

        /* Tables */
        .table-wrapper { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; }
        th { text-align: left; padding: 15px; color: var(--text-secondary); font-size: 12px; font-weight: 600; text-transform: uppercase; }
        td { padding: 15px; border-top: 1px solid rgba(255,255,255,0.05); color: #a9b1d6; font-size: 14px; }
        tr:hover td { background: rgba(255,255,255,0.02); }

        code { background: rgba(0,0,0,0.3); padding: 4px 8px; border-radius: 4px; font-family: monospace; color: var(--accent); }

        /* Forms */
        input, select, textarea {
            background: rgba(0,0,0,0.3);
            border: 1px solid var(--card-border);
            padding: 10px 15px;
            border-radius: 8px;
            color: #fff;
            outline: none;
            font-family: inherit;
        }
        input:focus, select:focus, textarea:focus { border-color: var(--accent); }

        .form-inline { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
        
        /* Badges */
        .badge { padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; white-space: nowrap; }
        .badge.active { background: rgba(158, 206, 106, 0.2); color: var(--success); }
        .badge.banned { background: rgba(247, 118, 142, 0.2); color: var(--error); }
        .badge.info { background: rgba(13, 185, 215, 0.2); color: var(--info); }

        /* Logs specific */
        .log-entry {
            padding: 8px 10px; 
            border-bottom: 1px solid rgba(255,255,255,0.05);
            font-size: 13px;
        }
        .log-entry:last-child { border-bottom: none; }
        .news-item {
            background: rgba(255,255,255,0.03);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 3px solid var(--accent);
            position: relative;
        }
        .news-item .meta { font-size: 11px; color: var(--text-secondary); margin-bottom: 5px; display:flex; justify-content:space-between; }
        .delete-news-btn { position: absolute; top: 10px; right: 10px; color: var(--error); text-decoration: none; font-size: 18px; }

    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ KEER AI <span style="font-size:14px; opacity:0.7; font-weight:400;">// ADMIN</span></h1>
        <div class="header-right">
            <div class="status-pill">
                <div class="dot green pulse"></div>
                Live (10s)
            </div>
            {% if stats.server_running %}
                <div class="status-pill" style="border-color: var(--success);">
                    <div class="dot green"></div> Active
                </div>
            {% else %}
                <div class="status-pill" style="border-color: var(--error);">
                    <div class="dot red"></div> Stopped
                </div>
            {% endif %}
            <a href="{{ url_for('logout') }}" class="btn btn-danger" style="padding:6px 12px;">Logout</a>
        </div>
    </div>

    <div class="container">
        
        <!-- Flash Messages -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for cat, msg in messages %}
                <div style="background: var(--{{ 'success' if cat == 'success' else 'error' }}); color:#000; padding: 15px; border-radius: 10px; margin-bottom: 20px; font-weight: 600;">
                    {{ msg }}
                </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <!-- Stats Grid -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-num">{{ stats.total_users }}</div>
                <div class="stat-label">Total Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-num" style="color: var(--error);">{{ stats.banned_users }}</div>
                <div class="stat-label">Banned Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-num" style="color: var(--accent);">{{ stats.total_chats }}</div>
                <div class="stat-label">Active Chats</div>
            </div>
            <div class="stat-card">
                <div class="stat-num">{{ stats.news_count }}</div>
                <div class="stat-label">News Updates</div>
            </div>
        </div>

        <!-- Server Controls -->
        <div class="card">
            <div class="card-header">
                <h2>⚡ System Controls</h2>
            </div>
            <div class="form-inline">
                {% if stats.server_running %}
                    <a href="{{ url_for('stop_server') }}" class="btn btn-danger" onclick="return confirm('WARNING: Stop Server?')">⏹️ STOP SERVER</a>
                {% else %}
                    <a href="{{ url_for('start_server') }}" class="btn btn-success">▶️ START SERVER</a>
                {% endif %}
                
                <a href="{{ url_for('unban_all') }}" class="btn btn-success" onclick="return confirm('Unban ALL users?')">🔓 UNBAN ALL</a>
                <a href="{{ url_for('clear_chats') }}" class="btn btn-danger" onclick="return confirm('DELETE ALL CHATS?')">🗑️ WIPE DATA</a>
                
                <!-- NEW: Nuclear Button -->
                <a href="{{ url_for('nuke_users') }}" class="btn btn-danger" style="border: 1px solid red; background: rgba(255,0,0,0.1);" onclick="return confirm('DANGER: DELETE ALL USERS? This cannot be undone.')">☢️ NUKE USERS</a>
                
                <a href="{{ url_for('dashboard') }}" class="btn btn-primary" style="margin-left:auto;">🔄 Refresh</a>
            </div>
        </div>

        <div class="grid-2" style="display:grid; grid-template-columns: 1.2fr 0.8fr; gap:25px;">
            
            <!-- LEFT COLUMN -->
            <div>
                <!-- Quick Ban -->
                <div class="card">
                    <div class="card-header">
                        <h2>🚫 Quick Ban / Timeout</h2>
                    </div>
                    <form action="{{ url_for('quick_ban') }}" method="POST" class="form-inline">
                        <input type="text" name="user_code" placeholder="User ID / Code" required style="flex:1; min-width: 150px;">
                        
                        <!-- Custom Timeout Input -->
                        <div style="display:flex; align-items:center; gap:5px; background:rgba(0,0,0,0.2); padding:5px; border-radius:8px;">
                            <span style="font-size:12px; color:var(--text-secondary);">TIMEOUT (MINS):</span>
                            <input type="number" name="custom_timeout" placeholder="0 = Perm" style="width: 80px; border:none; background:transparent;" min="0">
                        </div>

                        <button type="submit" class="btn btn-danger">APPLY</button>
                    </form>
                    <p style="font-size:12px; color:var(--text-secondary); margin_top:10px;">* Leave timeout empty or 0 for permanent ban.</p>
                </div>

                <!-- News Manager -->
                <div class="card">
                    <div class="card-header">
                        <h2>📢 System News & Updates</h2>
                    </div>
                    <form action="{{ url_for('add_news') }}" method="POST" style="margin-bottom: 20px;">
                        <div style="display: flex; gap: 10px;">
                            <textarea name="content" placeholder="Post a news update..." required style="flex:1; height: 60px; resize: none;"></textarea>
                            <button type="submit" class="btn btn-primary" style="height: 60px;">POST</button>
                        </div>
                    </form>

                    <div style="max-height: 300px; overflow-y: auto;">
                        {% for item in news %}
                        <div class="news-item">
                            <div class="meta">
                                <span>{{ item.created_at }}</span>
                                <span class="badge info">NEWS</span>
                            </div>
                            {{ item.content }}
                            <a href="{{ url_for('delete_news', id=item.id) }}" class="delete-news-btn" onclick="return confirm('Delete news?')">&times;</a>
                        </div>
                        {% else %}
                            <div style="text-align:center; padding:20px; color:var(--text-secondary);">No news updates yet.</div>
                        {% endfor %}
                    </div>
                </div>
            </div>

            <!-- RIGHT COLUMN -->
            <div>
                <!-- Recent Activity -->
                <div class="card">
                    <div class="card-header">
                        <h2>📝 Live Chat Stream</h2>
                    </div>
                    <div style="max-height: 400px; overflow-y: auto; font-size: 13px; color: var(--text-secondary);">
                        {% for m in messages %}
                        <div class="log-entry">
                            <span style="color: var(--accent); font-family:monospace;">[{{ m.timestamp[11:19] }}]</span>
                            <strong>{{ 'USER' if m.role == 'user' else 'AI' }}</strong>: 
                            <span style="color: {{ '#fff' if m.role == 'user' else '#9ece6a' }};">
                                {{ m.content[:100] }}{{ '...' if m.content|length > 100 }}
                            </span>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>

        <!-- Users Table -->
        <div class="card">
            <div class="card-header">
                <h2>👥 User Management</h2>
            </div>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>User Code</th>
                            <th>IP Address</th>
                            <th>Mode</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for u in users %}
                        <tr>
                            <td><code>{{ u.user_code }}</code></td>
                            <td>{{ u.ip_address }}</td>
                            <td>{{ u.behavior }}</td>
                            <td>
                                {% if u.is_banned %}
                                    <span class="badge banned">BANNED</span>
                                {% else %}
                                    <span class="badge active">ACTIVE</span>
                                {% endif %}
                            </td>
                            <td>
                                {% if u.is_banned %}
                                    <a href="{{ url_for('unban', code=u.user_code) }}" class="btn btn-success" style="padding: 4px 10px; font-size: 11px;">UNBAN</a>
                                {% else %}
                                    <div class="form-inline" style="gap:5px;">
                                        <!-- Quick buttons -->
                                        <a href="{{ url_for('ban', code=u.user_code) }}" class="btn btn-danger" style="padding: 4px 10px; font-size: 11px;">BAN</a>
                                        <a href="{{ url_for('timeout', code=u.user_code, mins=60) }}" class="btn btn-warning" style="padding: 4px 10px; font-size: 11px;">1H</a>
                                    </div>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

    </div>
</body>
</html>
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('key') == WEB_KEY:
            session['authenticated'] = True
            return redirect(url_for('dashboard'))
        error = "Invalid access key!"
    return render_template_string(LOGIN_HTML, error=error, created_by=CREATED_BY)

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    conn = get_db()
    
    # Stats
    stats = {
        'total_users': conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        'banned_users': conn.execute("SELECT COUNT(*) FROM users WHERE is_banned = 1").fetchone()[0],
        'total_chats': conn.execute("SELECT COUNT(*) FROM chats").fetchone()[0],
        'total_messages': conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0],
        'news_count': conn.execute("SELECT COUNT(*) FROM system_news").fetchone()[0]
    }
    
    state = conn.execute("SELECT * FROM server_state WHERE id = 1").fetchone()
    stats['server_running'] = state['is_running'] == 1 if state else True
    stats['stop_reason'] = state['stop_reason'] if state else None
    
    users = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    bans = conn.execute("SELECT * FROM bans ORDER BY banned_at DESC LIMIT 10").fetchall()
    messages = conn.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 20").fetchall()
    news = conn.execute("SELECT * FROM system_news ORDER BY created_at DESC LIMIT 20").fetchall()
    
    conn.close()
    
    return render_template_string(DASHBOARD_HTML,
        stats=stats, users=users, bans=bans, messages=messages, news=news,
        created_by=CREATED_BY, support_email=SUPPORT_EMAIL)

# ... (Existing routes stop/start/unban-all/clear-bans/clear-chats/ban/unban/timeout/kick/remove-ban remain unchanged) ...

@app.route('/nuke-users')
@login_required
def nuke_users():
    conn = get_db()
    conn.execute("DELETE FROM users")
    conn.execute("DELETE FROM bans")
    # Optional: Delete all chats too? No, keep chats for record usually, or user can click 'Wipe Data'
    conn.commit()
    conn.close()
    flash("☢️ NUKE EXECUTED: All users deleted.", "success")
    return redirect(url_for('dashboard'))

@app.route('/add-news', methods=['POST'])
@login_required
def add_news():
    content = request.form.get('content', '').strip()
    if content:
        conn = get_db()
        conn.execute("INSERT INTO system_news (content) VALUES (?)", (content,))
        conn.commit()
        conn.close()
        flash("News posted!", "success")
    return redirect(url_for('dashboard'))

@app.route('/delete-news/<int:id>')
@login_required
def delete_news(id):
    conn = get_db()
    conn.execute("DELETE FROM system_news WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("News item deleted!", "success")
    return redirect(url_for('dashboard'))

@app.route('/quick-ban', methods=['POST'])
@login_required
def quick_ban():
    code = request.form.get('user_code', '').strip()
    reason = request.form.get('reason', 'Admin action')
    
    # Check custom first
    custom_tm = request.form.get('custom_timeout', '')
    if custom_tm and custom_tm.isdigit() and int(custom_tm) > 0:
        timeout_mins = int(custom_tm)
    else:
        # Fallback to select dropdown (which might be 0)
        timeout_mins = int(request.form.get('timeout', 0))
    
    if not code:
        flash("User code required!", "error")
        return redirect(url_for('dashboard'))
    
    conn = get_db()
    expires = None
    if timeout_mins > 0:
        expires = (datetime.now() + timedelta(minutes=timeout_mins)).isoformat()
    
    user = conn.execute("SELECT * FROM users WHERE user_code = ?", (code,)).fetchone()
    if user:
        conn.execute("UPDATE users SET is_banned = 1 WHERE user_code = ?", (code,))
        conn.execute("INSERT INTO bans (user_code, ip_address, reason, expires_at) VALUES (?, ?, ?, ?)",
            (code, user['ip_address'], reason, expires))
    else:
        conn.execute("INSERT INTO bans (user_code, reason, expires_at) VALUES (?, ?, ?)",
            (code, reason, expires))
    
    conn.commit()
    conn.close()
    
    if timeout_mins > 0:
        flash(f"{code} timed out for {timeout_mins} min!", "success")
    else:
        flash(f"{code} permanently banned!", "success")
    return redirect(url_for('dashboard'))

@app.route('/api/stats')
def api_stats():
    conn = get_db()
    stats = {
        'users': conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        'banned': conn.execute("SELECT COUNT(*) FROM users WHERE is_banned = 1").fetchone()[0],
    }
    state = conn.execute("SELECT is_running FROM server_state WHERE id = 1").fetchone()
    stats['server'] = 'on' if state and state[0] == 1 else 'off'
    conn.close()
    return jsonify(stats)

if __name__ == '__main__':
    print("=" * 50)
    print("🛡️  KEER AI - WEB ADMIN DASHBOARD")
    print("=" * 50)
    print(f"🔐 Access Key: {WEB_KEY}")
    print(f"📂 Database: {DB_PATH}")
    print(f"👤 Created by: {CREATED_BY}")
    print("=" * 50)
    print("🌐 Open: http://localhost:5000")
    print("=" * 50)
    print("\n📦 TO HOST THIS DASHBOARD:")
    print("   1. Render.com - Free tier, easy deploy")
    print("   2. Railway.app - Free tier available")
    print("   3. VPS - Use: gunicorn web_dashboard:app")
    print("=" * 50)
    app.run(debug=True, port=5000, threaded=True)
