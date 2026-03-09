from flask import Blueprint, render_template
from database import get_db

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    db = get_db()
    categories = db.execute(
        "SELECT c.*, COUNT(s.id) as sentence_count "
        "FROM categories c LEFT JOIN sentences s ON c.id = s.category_id "
        "GROUP BY c.id ORDER BY c.id"
    ).fetchall()

    due_count = db.execute(
        "SELECT COUNT(*) as cnt FROM review_schedule WHERE next_review_date <= DATE('now')"
    ).fetchone()['cnt']

    recent_sessions = db.execute(
        "SELECT ss.*, c.name_ko as category_name "
        "FROM study_sessions ss LEFT JOIN categories c ON ss.category_id = c.id "
        "ORDER BY ss.started_at DESC LIMIT 5"
    ).fetchall()

    db.close()
    return render_template('index.html',
                           categories=categories,
                           due_count=due_count,
                           recent_sessions=recent_sessions)
