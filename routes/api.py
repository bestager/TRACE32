from flask import Blueprint, request, jsonify
from database import get_db
from command_parser import parse_command
from spaced_repetition import sm2_update
from ai_generator import generate_sentences
from datetime import date, timedelta

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/command', methods=['POST'])
def handle_command():
    data = request.get_json()
    if not data or 'command' not in data:
        return jsonify({"error": "명령어를 입력해주세요."}), 400

    parsed = parse_command(data['command'])
    if not parsed:
        return jsonify({"error": "명령어 형식이 올바르지 않습니다. 예: # 회의 영어 추천 50개#"}), 400

    db = get_db()

    if not parsed['recognized']:
        # Try AI generation for unknown category
        try:
            generated = generate_sentences(
                parsed['raw_category'], parsed['raw_category'], parsed['count']
            )
            if generated:
                cat_id = _get_or_create_category(db, parsed['raw_category'])
                saved = _save_sentences(db, cat_id, generated)
                db.close()
                return jsonify({
                    "category": parsed['raw_category'],
                    "count": len(saved),
                    "sentences": saved,
                    "source": "ai_generated"
                })
        except Exception:
            pass
        db.close()
        return jsonify({
            "error": f"'{parsed['raw_category']}' 카테고리를 찾을 수 없습니다.",
            "available": _get_category_names(db)
        }), 404

    category = db.execute(
        "SELECT * FROM categories WHERE name_ko = ?", (parsed['category_ko'],)
    ).fetchone()

    if not category:
        db.close()
        return jsonify({"error": f"'{parsed['category_ko']}' 카테고리가 없습니다."}), 404

    existing = db.execute(
        "SELECT * FROM sentences WHERE category_id = ? ORDER BY RANDOM() LIMIT ?",
        (category['id'], parsed['count'])
    ).fetchall()
    existing = [dict(s) for s in existing]

    if len(existing) >= parsed['count']:
        db.close()
        return jsonify({
            "category": parsed['category_ko'],
            "count": len(existing),
            "sentences": existing,
            "source": "builtin"
        })

    # Need more - try AI generation
    needed = parsed['count'] - len(existing)
    try:
        generated = generate_sentences(
            parsed['category_ko'], category['name_en'], needed
        )
        saved = _save_sentences(db, category['id'], generated)
        all_sentences = existing + saved
        db.close()
        return jsonify({
            "category": parsed['category_ko'],
            "count": len(all_sentences),
            "sentences": all_sentences,
            "source": "mixed"
        })
    except Exception:
        db.close()
        return jsonify({
            "category": parsed['category_ko'],
            "count": len(existing),
            "sentences": existing,
            "source": "builtin",
            "warning": f"AI 생성 실패. 내장 문장 {len(existing)}개만 표시합니다."
        })


@bp.route('/categories')
def get_categories():
    db = get_db()
    categories = db.execute(
        "SELECT c.*, COUNT(s.id) as sentence_count "
        "FROM categories c LEFT JOIN sentences s ON c.id = s.category_id "
        "GROUP BY c.id ORDER BY c.id"
    ).fetchall()
    db.close()
    return jsonify([dict(c) for c in categories])


@bp.route('/sentences/<category_name>')
def get_sentences(category_name):
    db = get_db()
    category = db.execute(
        "SELECT * FROM categories WHERE name_ko = ?", (category_name,)
    ).fetchone()
    if not category:
        db.close()
        return jsonify({"error": "카테고리를 찾을 수 없습니다."}), 404

    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    sentences = db.execute(
        "SELECT * FROM sentences WHERE category_id = ? LIMIT ? OFFSET ?",
        (category['id'], limit, offset)
    ).fetchall()
    db.close()
    return jsonify([dict(s) for s in sentences])


@bp.route('/progress/update', methods=['POST'])
def update_progress():
    data = request.get_json()
    sentence_id = data.get('sentence_id')
    knew_it = data.get('knew_it', False)

    if not sentence_id:
        return jsonify({"error": "sentence_id 필요"}), 400

    db = get_db()
    progress = db.execute(
        "SELECT * FROM user_progress WHERE sentence_id = ?", (sentence_id,)
    ).fetchone()

    if progress:
        times_studied = progress['times_studied'] + 1
        times_correct = progress['times_correct'] + (1 if knew_it else 0)
        accuracy = times_correct / times_studied if times_studied > 0 else 0

        if accuracy >= 0.9 and times_studied >= 5:
            mastery = 3
        elif accuracy >= 0.6:
            mastery = 2
        elif times_studied > 0:
            mastery = 1
        else:
            mastery = 0

        db.execute(
            "UPDATE user_progress SET times_studied = ?, times_correct = ?, "
            "mastery_level = ?, last_studied_at = CURRENT_TIMESTAMP "
            "WHERE sentence_id = ?",
            (times_studied, times_correct, mastery, sentence_id)
        )
    else:
        mastery = 1
        db.execute(
            "INSERT INTO user_progress (sentence_id, times_studied, times_correct, "
            "mastery_level, last_studied_at) VALUES (?, 1, ?, 1, CURRENT_TIMESTAMP)",
            (sentence_id, 1 if knew_it else 0)
        )

    # Add to review schedule when mastery reaches 2
    if mastery >= 2:
        existing_schedule = db.execute(
            "SELECT id FROM review_schedule WHERE sentence_id = ?", (sentence_id,)
        ).fetchone()
        if not existing_schedule:
            db.execute(
                "INSERT INTO review_schedule (sentence_id, next_review_date) "
                "VALUES (?, DATE('now', '+1 day'))",
                (sentence_id,)
            )

    db.commit()
    db.close()
    return jsonify({"success": True, "mastery_level": mastery})


@bp.route('/quiz/check', methods=['POST'])
def check_answer():
    data = request.get_json()
    sentence_id = data.get('sentence_id')
    user_answer = data.get('answer', '').strip()
    quiz_type = data.get('quiz_type', 'en_to_ko')

    if not sentence_id:
        return jsonify({"error": "sentence_id 필요"}), 400

    db = get_db()
    sentence = db.execute(
        "SELECT * FROM sentences WHERE id = ?", (sentence_id,)
    ).fetchone()
    if not sentence:
        db.close()
        return jsonify({"error": "문장을 찾을 수 없습니다."}), 404

    if quiz_type == 'en_to_ko':
        correct_answer = sentence['korean']
    else:
        correct_answer = sentence['english']

    is_correct = user_answer.lower().strip() == correct_answer.lower().strip()

    # Update progress
    progress = db.execute(
        "SELECT * FROM user_progress WHERE sentence_id = ?", (sentence_id,)
    ).fetchone()
    if progress:
        db.execute(
            "UPDATE user_progress SET times_studied = times_studied + 1, "
            "times_correct = times_correct + ?, last_studied_at = CURRENT_TIMESTAMP "
            "WHERE sentence_id = ?",
            (1 if is_correct else 0, sentence_id)
        )
    else:
        db.execute(
            "INSERT INTO user_progress (sentence_id, times_studied, times_correct, "
            "mastery_level, last_studied_at) VALUES (?, 1, ?, 1, CURRENT_TIMESTAMP)",
            (sentence_id, 1 if is_correct else 0)
        )

    db.commit()
    db.close()
    return jsonify({
        "correct": is_correct,
        "correct_answer": correct_answer,
        "user_answer": user_answer
    })


@bp.route('/review/grade', methods=['POST'])
def grade_review():
    data = request.get_json()
    sentence_id = data.get('sentence_id')
    quality = data.get('quality', 0)

    if not sentence_id or quality not in range(6):
        return jsonify({"error": "sentence_id와 quality(0-5) 필요"}), 400

    db = get_db()
    schedule = db.execute(
        "SELECT * FROM review_schedule WHERE sentence_id = ?", (sentence_id,)
    ).fetchone()

    if not schedule:
        db.close()
        return jsonify({"error": "복습 스케줄을 찾을 수 없습니다."}), 404

    new_ef, new_interval, new_reps = sm2_update(
        schedule['easiness_factor'],
        schedule['interval_days'],
        schedule['repetition_count'],
        quality
    )

    next_date = date.today() + timedelta(days=new_interval)

    db.execute(
        "UPDATE review_schedule SET easiness_factor = ?, interval_days = ?, "
        "repetition_count = ?, next_review_date = ?, last_quality = ? "
        "WHERE sentence_id = ?",
        (new_ef, new_interval, new_reps, next_date.isoformat(), quality, sentence_id)
    )

    # Update progress
    db.execute(
        "UPDATE user_progress SET times_studied = times_studied + 1, "
        "last_studied_at = CURRENT_TIMESTAMP WHERE sentence_id = ?",
        (sentence_id,)
    )

    db.commit()
    db.close()
    return jsonify({
        "success": True,
        "next_review_date": next_date.isoformat(),
        "interval_days": new_interval
    })


@bp.route('/review/due')
def get_due_reviews():
    db = get_db()
    due = db.execute(
        "SELECT s.*, rs.next_review_date, rs.interval_days, c.name_ko as category_name "
        "FROM review_schedule rs "
        "JOIN sentences s ON rs.sentence_id = s.id "
        "JOIN categories c ON s.category_id = c.id "
        "WHERE rs.next_review_date <= DATE('now') "
        "ORDER BY rs.next_review_date ASC"
    ).fetchall()
    db.close()
    return jsonify([dict(d) for d in due])


@bp.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    category_ko = data.get('category_ko', '')
    category_en = data.get('category_en', '')
    count = data.get('count', 10)

    try:
        generated = generate_sentences(category_ko, category_en, count)
        db = get_db()
        category = db.execute(
            "SELECT id FROM categories WHERE name_ko = ?", (category_ko,)
        ).fetchone()
        if category:
            saved = _save_sentences(db, category['id'], generated)
            db.close()
            return jsonify({"sentences": saved, "count": len(saved)})
        db.close()
        return jsonify({"error": "카테고리를 찾을 수 없습니다."}), 404
    except Exception as e:
        return jsonify({"error": f"AI 생성 실패: {str(e)}"}), 500


@bp.route('/stats')
def get_stats():
    db = get_db()

    total = db.execute("SELECT COUNT(*) as cnt FROM sentences").fetchone()['cnt']
    studied = db.execute("SELECT COUNT(*) as cnt FROM user_progress WHERE times_studied > 0").fetchone()['cnt']

    mastery = db.execute(
        "SELECT mastery_level, COUNT(*) as cnt FROM user_progress GROUP BY mastery_level"
    ).fetchall()
    mastery_map = {row['mastery_level']: row['cnt'] for row in mastery}

    by_category = db.execute(
        "SELECT c.name_ko, c.icon, "
        "COUNT(DISTINCT s.id) as total, "
        "COUNT(DISTINCT up.sentence_id) as studied, "
        "SUM(CASE WHEN up.mastery_level = 3 THEN 1 ELSE 0 END) as mastered "
        "FROM categories c "
        "LEFT JOIN sentences s ON c.id = s.category_id "
        "LEFT JOIN user_progress up ON s.id = up.sentence_id "
        "GROUP BY c.id ORDER BY c.id"
    ).fetchall()

    today_studied = db.execute(
        "SELECT COUNT(*) as cnt FROM user_progress "
        "WHERE DATE(last_studied_at) = DATE('now')"
    ).fetchone()['cnt']

    due_count = db.execute(
        "SELECT COUNT(*) as cnt FROM review_schedule "
        "WHERE next_review_date <= DATE('now')"
    ).fetchone()['cnt']

    history = db.execute(
        "SELECT DATE(last_studied_at) as study_date, COUNT(*) as cnt "
        "FROM user_progress WHERE last_studied_at IS NOT NULL "
        "GROUP BY DATE(last_studied_at) "
        "ORDER BY study_date DESC LIMIT 30"
    ).fetchall()

    # Calculate streak
    streak = _calculate_streak(db)

    db.close()
    return jsonify({
        "overview": {
            "total_sentences": total,
            "sentences_studied": studied,
            "mastery_breakdown": {
                "new": total - studied,
                "learning": mastery_map.get(1, 0),
                "reviewing": mastery_map.get(2, 0),
                "mastered": mastery_map.get(3, 0)
            },
            "study_streak_days": streak
        },
        "today": {
            "sentences_studied": today_studied,
            "reviews_remaining": due_count
        },
        "by_category": [dict(c) for c in by_category],
        "history": [dict(h) for h in history]
    })


@bp.route('/session', methods=['POST'])
def create_session():
    data = request.get_json()
    db = get_db()
    cursor = db.execute(
        "INSERT INTO study_sessions (session_type, category_id, sentences_studied, "
        "correct_answers, duration_seconds) VALUES (?, ?, ?, ?, ?)",
        (data.get('session_type', 'flashcard'),
         data.get('category_id'),
         data.get('sentences_studied', 0),
         data.get('correct_answers', 0),
         data.get('duration_seconds', 0))
    )
    db.commit()
    session_id = cursor.lastrowid
    db.close()
    return jsonify({"session_id": session_id})


def _calculate_streak(db):
    rows = db.execute(
        "SELECT DISTINCT DATE(last_studied_at) as study_date "
        "FROM user_progress WHERE last_studied_at IS NOT NULL "
        "ORDER BY study_date DESC"
    ).fetchall()

    if not rows:
        return 0

    today = date.today().isoformat()
    if rows[0]['study_date'] != today:
        return 0

    streak = 1
    for i in range(1, len(rows)):
        expected = (date.today() - timedelta(days=i)).isoformat()
        if rows[i]['study_date'] == expected:
            streak += 1
        else:
            break
    return streak


def _get_category_names(db):
    cats = db.execute("SELECT name_ko FROM categories").fetchall()
    return [c['name_ko'] for c in cats]


def _get_or_create_category(db, name_ko):
    cat = db.execute("SELECT id FROM categories WHERE name_ko = ?", (name_ko,)).fetchone()
    if cat:
        return cat['id']
    cursor = db.execute(
        "INSERT INTO categories (name_ko, name_en, description_ko) VALUES (?, ?, ?)",
        (name_ko, name_ko, f"{name_ko} 관련 영어 표현")
    )
    db.commit()
    return cursor.lastrowid


def _save_sentences(db, category_id, sentences):
    saved = []
    for s in sentences:
        cursor = db.execute(
            "INSERT INTO sentences (category_id, english, korean, difficulty, source) "
            "VALUES (?, ?, ?, ?, 'ai_generated')",
            (category_id, s['english'], s['korean'], s.get('difficulty', 1))
        )
        saved.append({
            "id": cursor.lastrowid,
            "category_id": category_id,
            "english": s['english'],
            "korean": s['korean'],
            "difficulty": s.get('difficulty', 1),
            "source": "ai_generated"
        })
    db.commit()
    return saved
