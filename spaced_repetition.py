def sm2_update(easiness_factor, interval, repetitions, quality):
    """
    SM-2 spaced repetition algorithm.
    quality: 0-5 (0=complete blackout, 5=perfect response)
    Returns: (new_ef, new_interval, new_repetitions)
    """
    if quality < 3:
        return max(1.3, easiness_factor), 1, 0

    new_ef = easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ef = max(1.3, new_ef)

    if repetitions == 0:
        new_interval = 1
    elif repetitions == 1:
        new_interval = 6
    else:
        new_interval = round(interval * new_ef)

    return new_ef, new_interval, repetitions + 1
