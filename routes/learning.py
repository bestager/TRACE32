from flask import Blueprint, render_template, request, abort
from database import get_db

bp = Blueprint('learning', __name__)


@bp.route('/sentences/<category_name>')
def sentence_list(category_name):
    db = get_db()
    category = db.execute(
        "SELECT * FROM categories WHERE name_ko = ?", (category_name,)
    ).fetchone()
    if not category:
        db.close()
        abort(404)

    limit = request.args.get('limit', 50, type=int)
    sentences = db.execute(
        "SELECT s.*, COALESCE(up.mastery_level, 0) as mastery_level, "
        "COALESCE(up.times_studied, 0) as times_studied "
        "FROM sentences s LEFT JOIN user_progress up ON s.id = up.sentence_id "
        "WHERE s.category_id = ? ORDER BY s.difficulty, s.id LIMIT ?",
        (category['id'], limit)
    ).fetchall()
    db.close()
    return render_template('sentences.html', category=category, sentences=sentences)


@bp.route('/flashcard/<category_name>')
def flashcard_mode(category_name):
    db = get_db()
    category = db.execute(
        "SELECT * FROM categories WHERE name_ko = ?", (category_name,)
    ).fetchone()
    if not category:
        db.close()
        abort(404)

    limit = request.args.get('limit', 50, type=int)
    sentences = db.execute(
        "SELECT s.*, COALESCE(up.mastery_level, 0) as mastery_level "
        "FROM sentences s LEFT JOIN user_progress up ON s.id = up.sentence_id "
        "WHERE s.category_id = ? ORDER BY RANDOM() LIMIT ?",
        (category['id'], limit)
    ).fetchall()
    db.close()
    return render_template('flashcard.html', category=category,
                           sentences=[dict(s) for s in sentences])


@bp.route('/quiz/<category_name>')
def quiz_mode(category_name):
    db = get_db()
    category = db.execute(
        "SELECT * FROM categories WHERE name_ko = ?", (category_name,)
    ).fetchone()
    if not category:
        db.close()
        abort(404)

    limit = request.args.get('limit', 20, type=int)
    sentences = db.execute(
        "SELECT * FROM sentences WHERE category_id = ? ORDER BY RANDOM() LIMIT ?",
        (category['id'], limit)
    ).fetchall()

    all_sentences = db.execute(
        "SELECT * FROM sentences WHERE category_id = ?", (category['id'],)
    ).fetchall()
    db.close()

    return render_template('quiz.html', category=category,
                           sentences=[dict(s) for s in sentences],
                           all_sentences=[dict(s) for s in all_sentences])


@bp.route('/review')
def review_mode():
    db = get_db()
    due_sentences = db.execute(
        "SELECT s.*, rs.easiness_factor, rs.interval_days, rs.repetition_count, "
        "rs.next_review_date, rs.last_quality, c.name_ko as category_name "
        "FROM review_schedule rs "
        "JOIN sentences s ON rs.sentence_id = s.id "
        "JOIN categories c ON s.category_id = c.id "
        "WHERE rs.next_review_date <= DATE('now') "
        "ORDER BY rs.next_review_date ASC"
    ).fetchall()
    db.close()
    return render_template('review.html',
                           sentences=[dict(s) for s in due_sentences])
