#!/usr/bin/env python3
"""Load built-in sentence data into the database."""

import json
from database import get_db, init_db


def seed():
    init_db()
    db = get_db()

    with open('data/builtin_sentences.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    for cat in data['categories']:
        existing = db.execute(
            "SELECT id FROM categories WHERE name_ko = ?", (cat['name_ko'],)
        ).fetchone()

        if existing:
            cat_id = existing['id']
        else:
            cursor = db.execute(
                "INSERT INTO categories (name_ko, name_en, description_ko, icon) "
                "VALUES (?, ?, ?, ?)",
                (cat['name_ko'], cat['name_en'], cat['description_ko'], cat['icon'])
            )
            cat_id = cursor.lastrowid

        for s in cat['sentences']:
            exists = db.execute(
                "SELECT id FROM sentences WHERE category_id = ? AND english = ?",
                (cat_id, s['english'])
            ).fetchone()
            if not exists:
                db.execute(
                    "INSERT INTO sentences (category_id, english, korean, difficulty, source) "
                    "VALUES (?, ?, ?, ?, 'builtin')",
                    (cat_id, s['english'], s['korean'], s['difficulty'])
                )

    db.commit()

    # Print summary
    total = db.execute("SELECT COUNT(*) as cnt FROM sentences").fetchone()['cnt']
    cats = db.execute(
        "SELECT c.name_ko, c.icon, COUNT(s.id) as cnt "
        "FROM categories c LEFT JOIN sentences s ON c.id = s.category_id "
        "GROUP BY c.id"
    ).fetchall()

    print(f"\n데이터 로드 완료! 총 {total}개 문장")
    print("-" * 40)
    for c in cats:
        print(f"  {c['icon']} {c['name_ko']}: {c['cnt']}문장")
    print()

    db.close()


if __name__ == '__main__':
    seed()
