from typing import Dict, List, Optional, Tuple, Any
import random
from config.nutrition_data import (
    COMMON_FOODS, MACRO_RATIOS, DIETARY_RESTRICTIONS,
    VITAMIN_SOURCES, WEIGHT_GOALS
)
from src.utils import (
    calculate_bmr, calculate_tdee, calculate_target_calories,
    calculate_macros, extract_user_info, format_nutrition_info
)

class NutritionExpert:
    """
    Core nutrition expertise module that handles calculations,
    meal planning, and personalized advice.
    """

    def __init__(self):
        self.user_profiles = {}  # Store user information across sessions

    def analyze_user_query(self, query: str, user_id: str = "default") -> Dict[str, Any]:
        """
        Analyze user query and extract relevant information for nutrition advice.

        Args:
            query: User's question or request
            user_id: Unique identifier for the user

        Returns:
            Dict containing analysis results and recommendations
        """
        query_lower = query.lower()

        # Extract user information from query
        user_info = extract_user_info(query)

        # Update user profile if new information is provided
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {}
        self.user_profiles[user_id].update(user_info)

        analysis = {
            "query_type": self._classify_query(query_lower),
            "extracted_info": user_info,
            "user_profile": self.user_profiles[user_id],
            "recommendations": []
        }

        return analysis

    def _classify_query(self, query: str) -> str:
        """Classify the type of nutrition query."""
        if any(word in query for word in ['calorie', 'calories', 'bmr', 'tdee', 'metabolic rate']):
            return "calorie_calculation"
        elif any(word in query for word in ['protein', 'carb', 'fat', 'macro', 'macronutrient']):
            return "macro_advice"
        elif any(word in query for word in ['meal plan', 'diet plan', 'what to eat', 'menu']):
            return "meal_planning"
        elif any(word in query for word in ['vitamin', 'mineral', 'nutrient', 'deficiency']):
            return "nutrient_advice"
        elif any(word in query for word in ['lose weight', 'weight loss', 'diet', 'cutting']):
            return "weight_loss"
        elif any(word in query for word in ['gain weight', 'bulk', 'muscle', 'gain muscle']):
            return "weight_gain"
        elif any(word in query for word in ['recipe', 'cook', 'food', 'ingredient']):
            return "recipe_advice"
        else:
            return "general_nutrition"

    def calculate_daily_needs(self, user_profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Calculate daily caloric and macro needs based on user profile.

        Args:
            user_profile: Dict containing user's physical stats and goals

        Returns:
            Dict with calculated daily needs or None if insufficient info
        """
        required_fields = ['weight', 'height', 'age', 'gender', 'activity', 'goal']

        if not all(field in user_profile for field in required_fields):
            missing = [field for field in required_fields if field not in user_profile]
            return {"error": f"Missing information: {', '.join(missing)}"}

        try:
            # Calculate BMR
            bmr = calculate_bmr(
                user_profile['weight'],
                user_profile['height'],
                user_profile['age'],
                user_profile['gender']
            )

            # Calculate TDEE
            tdee = calculate_tdee(bmr, user_profile['activity'])

            # Calculate target calories
            target_calories = calculate_target_calories(tdee, user_profile['goal'])

            # Choose macro ratio based on goal
            macro_ratio = self._get_macro_ratio(user_profile.get('goal', 'maintain_weight'))

            # Calculate macros
            macros = calculate_macros(target_calories, macro_ratio)

            return {
                "bmr": round(bmr),
                "tdee": round(tdee),
                "target_calories": round(target_calories),
                "macros": {
                    "protein": round(macros['protein']),
                    "carbs": round(macros['carbs']),
                    "fat": round(macros['fat'])
                },
                "macro_ratio": macro_ratio
            }

        except Exception as e:
            return {"error": f"Calculation error: {str(e)}"}

    def _get_macro_ratio(self, goal: str) -> Dict[str, float]:
        """Get appropriate macro ratio based on goal."""
        if goal == 'lose_weight':
            return MACRO_RATIOS['high_protein']
        elif goal == 'gain_weight':
            return MACRO_RATIOS['balanced']
        else:
            return MACRO_RATIOS['balanced']

    def suggest_meals(self, preferences: Dict[str, Any], meal_type: str = "any") -> List[Dict[str, Any]]:
        """
        Suggest meals based on dietary preferences and restrictions.

        Args:
            preferences: Dict with dietary restrictions, calorie targets, etc.
            meal_type: Type of meal (breakfast, lunch, dinner, snack, any)

        Returns:
            List of meal suggestions with nutritional information
        """
        suitable_foods = []
        excluded_foods = set()

        # Apply dietary restrictions
        dietary_restriction = preferences.get('dietary_restriction', '')
        if dietary_restriction in DIETARY_RESTRICTIONS:
            excluded_foods.update(DIETARY_RESTRICTIONS[dietary_restriction]['excluded'])

        # Filter foods based on restrictions
        for food_name, nutrition in COMMON_FOODS.items():
            if food_name not in excluded_foods:
                suitable_foods.append({
                    "name": food_name.replace('_', ' ').title(),
                    "nutrition": nutrition,
                    "food_key": food_name
                })

        # Generate meal suggestions based on meal type
        suggestions = []

        if meal_type in ["breakfast", "any"]:
            suggestions.extend(self._generate_breakfast_suggestions(suitable_foods))

        if meal_type in ["lunch", "dinner", "any"]:
            suggestions.extend(self._generate_main_meal_suggestions(suitable_foods))

        if meal_type in ["snack", "any"]:
            suggestions.extend(self._generate_snack_suggestions(suitable_foods))

        return suggestions[:6]  # Limit to 6 suggestions

    def _generate_breakfast_suggestions(self, foods: List[Dict]) -> List[Dict]:
        """Generate breakfast meal suggestions."""
        breakfast_bases = [f for f in foods if f['food_key'] in ['oats', 'eggs', 'greek_yogurt']]
        toppings = [f for f in foods if f['food_key'] in ['banana', 'almonds', 'spinach']]

        suggestions = []

        if any(f['food_key'] == 'oats' for f in breakfast_bases):
            suggestions.append({
                "meal": "Protein Overnight Oats",
                "ingredients": ["Oats", "Greek Yogurt", "Banana", "Almonds"],
                "description": "High-protein breakfast with complex carbs and healthy fats",
                "prep_time": "5 min prep, overnight rest"
            })

        if any(f['food_key'] == 'eggs' for f in breakfast_bases):
            suggestions.append({
                "meal": "Veggie Scramble",
                "ingredients": ["Eggs", "Spinach", "Avocado"],
                "description": "Protein-rich eggs with nutrient-dense vegetables",
                "prep_time": "10 minutes"
            })

        return suggestions

    def _generate_main_meal_suggestions(self, foods: List[Dict]) -> List[Dict]:
        """Generate lunch/dinner meal suggestions."""
        proteins = [f for f in foods if f['food_key'] in ['chicken_breast', 'salmon', 'quinoa']]
        vegetables = [f for f in foods if f['food_key'] in ['broccoli', 'spinach', 'sweet_potato']]

        suggestions = []

        if any(f['food_key'] == 'salmon' for f in proteins):
            suggestions.append({
                "meal": "Baked Salmon Bowl",
                "ingredients": ["Salmon", "Quinoa", "Broccoli", "Avocado"],
                "description": "Omega-3 rich salmon with complete protein quinoa and fiber-rich vegetables",
                "prep_time": "25 minutes"
            })

        if any(f['food_key'] == 'chicken_breast' for f in proteins):
            suggestions.append({
                "meal": "Chicken Power Bowl",
                "ingredients": ["Chicken Breast", "Brown Rice", "Spinach", "Sweet Potato"],
                "description": "Lean protein with complex carbs and antioxidant-rich vegetables",
                "prep_time": "30 minutes"
            })

        return suggestions

    def _generate_snack_suggestions(self, foods: List[Dict]) -> List[Dict]:
        """Generate healthy snack suggestions."""
        return [
            {
                "meal": "Apple Almond Butter",
                "ingredients": ["Apple", "Almonds"],
                "description": "Balanced snack with fiber and healthy fats",
                "prep_time": "2 minutes"
            },
            {
                "meal": "Greek Yogurt Parfait",
                "ingredients": ["Greek Yogurt", "Banana"],
                "description": "High-protein snack with natural sweetness",
                "prep_time": "3 minutes"
            }
        ]

    def get_nutrient_sources(self, nutrient: str) -> List[str]:
        """
        Get food sources for a specific nutrient.

        Args:
            nutrient: Name of the nutrient

        Returns:
            List of food sources
        """
        nutrient_lower = nutrient.lower().replace(' ', '_')

        if nutrient_lower in VITAMIN_SOURCES:
            sources = VITAMIN_SOURCES[nutrient_lower]
            return [food.replace('_', ' ').title() for food in sources]

        return []

    def generate_personalized_advice(self, user_profile: Dict[str, Any], query_type: str) -> str:
        """
        Generate personalized nutrition advice based on user profile and query type.

        Args:
            user_profile: User's information and preferences
            query_type: Type of query (from _classify_query)

        Returns:
            Personalized advice string
        """
        daily_needs = self.calculate_daily_needs(user_profile)

        if query_type == "calorie_calculation" and daily_needs and "error" not in daily_needs:
            return f"""Based on your profile, here are your daily needs:

🔥 **Daily Calories**: {daily_needs['target_calories']} calories
📊 **Macronutrient Breakdown**:
• Protein: {daily_needs['macros']['protein']}g ({int(daily_needs['macro_ratio']['protein']*100)}%)
• Carbs: {daily_needs['macros']['carbs']}g ({int(daily_needs['macro_ratio']['carbs']*100)}%)
• Fat: {daily_needs['macros']['fat']}g ({int(daily_needs['macro_ratio']['fat']*100)}%)

💡 **Additional Info**:
• BMR (at rest): {daily_needs['bmr']} calories
• TDEE (with activity): {daily_needs['tdee']} calories"""

        elif query_type == "weight_loss":
            return """For healthy weight loss, aim for:

🎯 **Safe Rate**: 1-2 pounds per week
📉 **Calorie Deficit**: 500-750 calories below maintenance
🍽️ **Focus On**:
• High protein to preserve muscle (0.8-1g per lb bodyweight)
• Plenty of vegetables for nutrients and satiety
• Stay hydrated (half your bodyweight in ounces of water)
• Consistent meal timing

⚠️ Avoid extreme restrictions - sustainable habits lead to lasting results!"""

        elif query_type == "weight_gain":
            return """For healthy weight gain, consider:

🎯 **Safe Rate**: 0.5-1 pound per week
📈 **Calorie Surplus**: 300-500 calories above maintenance
🏋️ **Focus On**:
• Adequate protein for muscle building (1-1.2g per lb bodyweight)
• Complex carbs around workouts
• Healthy fats for hormone production
• Consistent strength training

💡 Quality over quantity - choose nutrient-dense foods!"""

        else:
            return """I'm here to help with your nutrition goals! For personalized advice, please share:

📝 **Your Stats**: Age, weight, height, gender
🏃 **Activity Level**: Sedentary to very active
🎯 **Goals**: Weight loss, gain, or maintenance
🚫 **Restrictions**: Any dietary limitations or allergies

The more details you provide, the better I can tailor my recommendations to your needs!"""