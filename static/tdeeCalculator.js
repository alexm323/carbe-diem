function calculateTDEE(gender, height, weight, age, activityLevel) {
    let activityMultiplier
    height = height * 2.54
    weight = weight / 2.2
    switch (activityLevel) {
        case "level1":
            activityMultiplier = 1.2;
            break;
        case "level2":
            activityMultiplier = 1.375;
            break;
        case "level3":
            activityMultiplier = 1.55;
            break;
        case "level4":
            activityMultiplier = 1.725;
            break;
        case "level5":
            activityMultiplier = 1.9;
            break;

    }
    if (gender === 'male') {
        // basal metabolic rate

        // convert height and weight to metric units (cm and kg)

        let bmr = (66 + (13.7 * weight) + (5 * height) - (6.8 * age))

        console.log(`Your Total Daily Energy Expenditure is ${Math.round(bmr * activityMultiplier)}`)

    }
    else if (gender === 'female') {
        // basal metabolic rate

        // convert height and weight to metric units (cm and kg)

        let bmr = (655 + (9.6 * weight) + (1.8 * height) - (4.7 * age))
        switch (activityLevel) {
            case "level1":
                activityMultiplier = 1.2;
                break;
            case "level2":
                activityMultiplier = 1.375;
                break;
            case "level3":
                activityMultiplier = 1.55;
                break;
            case "level4":
                activityMultiplier = 1.725;
                break;
            case "level5":
                activityMultiplier = 1.9;
                break;

        }
        console.log(`Your Total Daily Energy Expenditure is ${Math.round(bmr * activityMultiplier)}`)

    }
}