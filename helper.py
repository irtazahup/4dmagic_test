def compute_confidence(chunks):
    if not chunks:
        return 0.0

    avg_score = sum(c["score"] for c in chunks) / len(chunks)

    return round(avg_score, 3)