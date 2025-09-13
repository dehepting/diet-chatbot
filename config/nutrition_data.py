COMMON_FOODS = {
    "chicken_breast": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6, "fiber": 0},
    "salmon": {"calories": 208, "protein": 20, "carbs": 0, "fat": 13, "fiber": 0},
    "eggs": {"calories": 155, "protein": 13, "carbs": 1.1, "fat": 11, "fiber": 0},
    "quinoa": {"calories": 222, "protein": 8, "carbs": 39, "fat": 3.6, "fiber": 5.2},
    "brown_rice": {"calories": 216, "protein": 5, "carbs": 45, "fat": 1.8, "fiber": 3.5},
    "broccoli": {"calories": 34, "protein": 2.8, "carbs": 7, "fat": 0.4, "fiber": 2.6},
    "spinach": {"calories": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4, "fiber": 2.2},
    "avocado": {"calories": 160, "protein": 2, "carbs": 9, "fat": 15, "fiber": 7},
    "almonds": {"calories": 579, "protein": 21, "carbs": 22, "fat": 50, "fiber": 12},
    "greek_yogurt": {"calories": 100, "protein": 17, "carbs": 6, "fat": 0.4, "fiber": 0},
    "oats": {"calories": 389, "protein": 17, "carbs": 66, "fat": 7, "fiber": 11},
    "banana": {"calories": 89, "protein": 1.1, "carbs": 23, "fat": 0.3, "fiber": 2.6},
    "apple": {"calories": 52, "protein": 0.3, "carbs": 14, "fat": 0.2, "fiber": 2.4},
    "sweet_potato": {"calories": 86, "protein": 1.6, "carbs": 20, "fat": 0.1, "fiber": 3},
}

MACRO_RATIOS = {
    "balanced": {"protein": 0.25, "carbs": 0.45, "fat": 0.30},
    "high_protein": {"protein": 0.35, "carbs": 0.35, "fat": 0.30},
    "low_carb": {"protein": 0.30, "carbs": 0.20, "fat": 0.50},
    "ketogenic": {"protein": 0.20, "carbs": 0.05, "fat": 0.75},
    "mediterranean": {"protein": 0.20, "carbs": 0.45, "fat": 0.35},
}

DIETARY_RESTRICTIONS = {
    "vegetarian": {
        "excluded": ["chicken_breast", "salmon"],
        "recommended": ["quinoa", "eggs", "greek_yogurt", "almonds", "spinach"]
    },
    "vegan": {
        "excluded": ["chicken_breast", "salmon", "eggs", "greek_yogurt"],
        "recommended": ["quinoa", "almonds", "spinach", "broccoli", "avocado", "oats"]
    },
    "gluten_free": {
        "excluded": ["oats"],  # unless certified gluten-free
        "recommended": ["quinoa", "brown_rice", "chicken_breast", "salmon"]
    },
    "dairy_free": {
        "excluded": ["greek_yogurt"],
        "recommended": ["almonds", "quinoa", "chicken_breast", "salmon", "avocado"]
    }
}

VITAMIN_SOURCES = {
    "vitamin_c": ["broccoli", "spinach"],
    "vitamin_d": ["salmon", "eggs"],
    "vitamin_b12": ["salmon", "chicken_breast", "eggs"],
    "iron": ["spinach", "quinoa", "chicken_breast"],
    "calcium": ["greek_yogurt", "almonds", "broccoli"],
    "omega_3": ["salmon", "almonds"],
    "fiber": ["quinoa", "oats", "avocado", "broccoli"],
    "potassium": ["banana", "sweet_potato", "avocado"]
}

BMR_FORMULAS = {
    "mifflin_st_jeor": {
        "male": lambda weight, height, age: 10 * weight + 6.25 * height - 5 * age + 5,
        "female": lambda weight, height, age: 10 * weight + 6.25 * height - 5 * age - 161
    }
}

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "lightly_active": 1.375,
    "moderately_active": 1.55,
    "very_active": 1.725,
    "extremely_active": 1.9
}

WEIGHT_GOALS = {
    "lose_weight": -500,  # Calorie deficit per day for 1 lb/week loss
    "maintain_weight": 0,
    "gain_weight": 500   # Calorie surplus per day for 1 lb/week gain
}