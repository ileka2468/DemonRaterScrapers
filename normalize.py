def calculate_weighted_average(responses):
    normalized_responses = {key: round(value / 100, 2) for key, value in responses.items()}
    # print(normalized_responses)
    weights = determine_weights(responses)
    # print(weights)
    weighted_sum = sum(weight * responses[response] for response, weight in weights.items())
    total_responses = sum(responses.values())

    if weighted_sum == 0:
        return 0
    return weighted_sum / total_responses


def determine_weights(responses):
    keys = list(responses.keys())
    first_key = keys[0]

    if first_key == 'Strongly agree':
        return {
            "Strongly agree": 5,
            "Agree": 4,
            "Neither agree nor disagree": 3,
            "Disagree": 2,
            "Strongly disagree": 1
        }
    elif first_key == 'Among the best':
        return {
            "Among the best": 5,
            "Better than average": 4,
            "About average": 3,
            "Worse than average": 2,
            "Among the worst": 1
        }
    elif first_key == 'Too much':
        return {
            "Too much": 5,
            "A little too much": 4,
            "About right": 3,
            "Not quite enough": 2,
            "Not enough": 1
        }
    elif first_key == 'Among the most challenging':
        return {
            "Among the most challenging": 5,
            "More challenging than many courses": 4,
            "About as challenging as other courses": 3,
            "Less challenging than other courses": 2,
            "Among the least challenging": 1
        }


if __name__ == '__main__':
    pass
