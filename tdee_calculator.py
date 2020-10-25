def calculate_tdee(gender, height, weight, age, activity_level):
    height = float(height) * 2.54
    weight = float(weight) / 2.2
    age = float(age)
    activity_dictionary = {
        'level1': 1.2,
        'level2': 1.375,
        'level3': 1.55,
        'level4': 1.725,
        'level5': 1.90
    }
    if gender == 'male':
        bmr = ((10 * weight) + (6.25 * height) - (5 * age)+5)
        tdee = round(bmr*activity_dictionary[activity_level])
        return tdee
    elif gender == 'female':
        bmr = ((10 * weight) + (6.25 * height) - (5 * age)-161)
        tdee = round(bmr*activity_dictionary[activity_level])
        return tdee


def calculate_bmi(height, weight):
    height = float(height)
    weight = float(weight)
    bmi = round(703 * weight / (height*height))
    return bmi


def calculate_ideal_weight(height):
    height = float(height)
    ideal_weight = round((24.9*(height*height))/703)
    return ideal_weight


def calculate_pounds_to_lose(current_weight, height):
    current_weight = float(current_weight)
    ideal_weight = calculate_ideal_weight(height)
    need_to_lose = current_weight - ideal_weight
    return need_to_lose


def calculate_ideal_time_frame(tdee, need_to_lose):
    tdee = float(tdee)
    need_to_lose = float(need_to_lose)
    calories_to_lose = need_to_lose*3500
    safe_calorie_loss_zone = tdee - 1200
    days_to_ideal_weight = calories_to_lose/safe_calorie_loss_zone
    return days_to_ideal_weight
