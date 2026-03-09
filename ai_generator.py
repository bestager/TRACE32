import json
import config

def generate_sentences(category_ko, category_en, count, difficulty=None):
    """
    Generate English learning sentences via Claude API.
    Returns list of {"english": ..., "korean": ..., "difficulty": 1-3}
    """
    if not config.CLAUDE_API_KEY:
        return []

    import anthropic
    client = anthropic.Anthropic(api_key=config.CLAUDE_API_KEY)

    difficulty_desc = ""
    if difficulty:
        levels = {1: "beginner (초급)", 2: "intermediate (중급)", 3: "advanced (고급)"}
        difficulty_desc = f"Difficulty level: {levels.get(difficulty, 'mixed')}."

    prompt = f"""Generate exactly {count} English sentences commonly used in "{category_en}" ({category_ko}).

For each sentence provide:
1. The English sentence (natural, commonly used expression)
2. The Korean translation (natural Korean, not word-for-word)
3. Difficulty level: 1 (beginner), 2 (intermediate), 3 (advanced)

{difficulty_desc}

Rules:
- Sentences should be practical and commonly used in real situations
- Korean translations should sound natural to native Korean speakers
- Include a mix of statements, questions, and polite expressions
- Avoid overly simple sentences like "Hello" or "Thank you"
- Each sentence should teach a useful pattern or expression

Return ONLY a JSON array with objects having keys: "english", "korean", "difficulty"
Do not include any other text, markdown formatting, or code blocks."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    result_text = response.content[0].text.strip()
    if result_text.startswith('```'):
        result_text = result_text.split('\n', 1)[1]
        result_text = result_text.rsplit('```', 1)[0]

    return json.loads(result_text)
