def calculate_penalized_score_with_min(evaluation_score, num_responses, r_threshold=12, p_factor=1.2, miniimum_score=1.0):
    if num_responses >= r_threshold:
        return evaluation_score
    penalty = p_factor * (r_threshold - num_responses) / r_threshold
    penalized_score = max(evaluation_score - penalty, miniimum_score)
    return penalized_score


if __name__ == '__main__':
    pass
