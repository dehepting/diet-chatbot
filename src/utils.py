import re
from typing import Dict, List, Optional, Tuple
from config.nutrition_data import BMR_FORMULAS, ACTIVITY_MULTIPLIERS, WEIGHT_GOALS, COMMON_FOODS

def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
    """
    Calculate Basal Metabolic Rate using Mifflin-St Jeor equation.

    Args:
        weight: Weight in kg
        height: Height in cm
        age: Age in years
        gender: 'male' or 'female'

    Returns:
        BMR in calories per day
    """
    if gender.lower() not in ['male', 'female']:
        raise ValueError("Gender must be 'male' or 'female'")

    formula = BMR_FORMULAS["mifflin_st_jeor"][gender.lower()]
    return formula(weight, height, age)

def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    Calculate Total Daily Energy Expenditure.

    Args:
        bmr: Basal Metabolic Rate
        activity_level: One of 'sedentary', 'lightly_active', 'moderately_active',
                       'very_active', 'extremely_active'

    Returns:
        TDEE in calories per day
    """
    if activity_level not in ACTIVITY_MULTIPLIERS:
        raise ValueError(f"Activity level must be one of: {list(ACTIVITY_MULTIPLIERS.keys())}")

    return bmr * ACTIVITY_MULTIPLIERS[activity_level]

def calculate_target_calories(tdee: float, goal: str) -> float:
    """
    Calculate target daily calories based on weight goal.

    Args:
        tdee: Total Daily Energy Expenditure
        goal: 'lose_weight', 'maintain_weight', or 'gain_weight'

    Returns:
        Target calories per day
    """
    if goal not in WEIGHT_GOALS:
        raise ValueError(f"Goal must be one of: {list(WEIGHT_GOALS.keys())}")

    return tdee + WEIGHT_GOALS[goal]

def calculate_macros(calories: float, macro_ratio: Dict[str, float]) -> Dict[str, float]:
    """
    Calculate macro distribution in grams based on calories and ratios.

    Args:
        calories: Total daily calories
        macro_ratio: Dict with 'protein', 'carbs', 'fat' ratios (should sum to 1.0)

    Returns:
        Dict with macro amounts in grams
    """
    # Calories per gram: protein=4, carbs=4, fat=9
    protein_calories = calories * macro_ratio['protein']
    carb_calories = calories * macro_ratio['carbs']
    fat_calories = calories * macro_ratio['fat']

    return {
        'protein': protein_calories / 4,
        'carbs': carb_calories / 4,
        'fat': fat_calories / 9,
        'calories': calories
    }

def extract_user_info(text: str) -> Dict[str, Optional[str]]:
    """
    Extract user information from natural language text.

    Args:
        text: User input text

    Returns:
        Dict with extracted information
    """
    info = {}

    # Extract weight (kg or lbs)
    weight_match = re.search(r'(\d+(?:\.\d+)?)\s*(kg|pounds?|lbs?)', text.lower())
    if weight_match:
        weight_value = float(weight_match.group(1))
        unit = weight_match.group(2)
        if 'lb' in unit or 'pound' in unit:
            weight_value = weight_value * 0.453592  # Convert to kg
        info['weight'] = weight_value

    # Extract height (cm or feet/inches)
    height_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:cm|centimeters?)', text.lower())
    if height_match:
        info['height'] = float(height_match.group(1))
    else:
        # Try feet and inches format
        feet_inches = re.search(r'(\d+)\s*(?:feet?|ft|\')\s*(\d+)\s*(?:inches?|in|")', text.lower())
        if feet_inches:
            feet = int(feet_inches.group(1))
            inches = int(feet_inches.group(2))
            info['height'] = (feet * 12 + inches) * 2.54  # Convert to cm

    # Extract age
    age_match = re.search(r'(\d+)\s*(?:years?\s*old|yr|age)', text.lower())
    if age_match:
        info['age'] = int(age_match.group(1))

    # Extract gender
    if re.search(r'\b(?:male|man|guy)\b', text.lower()):
        info['gender'] = 'male'
    elif re.search(r'\b(?:female|woman|girl)\b', text.lower()):
        info['gender'] = 'female'

    # Extract activity level
    if re.search(r'\b(?:sedentary|desk job|no exercise)\b', text.lower()):
        info['activity'] = 'sedentary'
    elif re.search(r'\b(?:lightly active|light exercise)\b', text.lower()):
        info['activity'] = 'lightly_active'
    elif re.search(r'\b(?:moderately active|moderate exercise)\b', text.lower()):
        info['activity'] = 'moderately_active'
    elif re.search(r'\b(?:very active|heavy exercise)\b', text.lower()):
        info['activity'] = 'very_active'
    elif re.search(r'\b(?:extremely active|athlete)\b', text.lower()):
        info['activity'] = 'extremely_active'

    # Extract goals
    if re.search(r'\b(?:lose weight|weight loss|cut|cutting)\b', text.lower()):
        info['goal'] = 'lose_weight'
    elif re.search(r'\b(?:gain weight|bulk|bulking|gain muscle)\b', text.lower()):
        info['goal'] = 'gain_weight'
    elif re.search(r'\b(?:maintain|maintenance)\b', text.lower()):
        info['goal'] = 'maintain_weight'

    return info

def format_nutrition_info(food_name: str) -> str:
    """
    Format nutrition information for a specific food.

    Args:
        food_name: Name of the food (key in COMMON_FOODS)

    Returns:
        Formatted nutrition information string
    """
    if food_name not in COMMON_FOODS:
        return f"Sorry, I don't have nutrition information for {food_name}."

    food = COMMON_FOODS[food_name]
    formatted_name = food_name.replace('_', ' ').title()

    return f"""**{formatted_name}** (per 100g):
• Calories: {food['calories']}
• Protein: {food['protein']}g
• Carbs: {food['carbs']}g
• Fat: {food['fat']}g
• Fiber: {food['fiber']}g"""

def validate_user_input(text: str) -> bool:
    """
    Basic validation for user input to ensure it's appropriate for nutrition advice.

    Args:
        text: User input text

    Returns:
        True if input seems valid, False otherwise
    """
    if not text or len(text.strip()) < 3:
        return False

    # Check for inappropriate content (basic filtering)
    inappropriate_terms = ['medication', 'drug', 'prescription', 'diagnose', 'cure', 'treat']
    text_lower = text.lower()

    for term in inappropriate_terms:
        if term in text_lower:
            return False

    return True