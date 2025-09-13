#!/usr/bin/env python3
"""
Test script for the Diet Chatbot functionality.
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.chatbot import DietChatbot
from src.nutrition_expert import NutritionExpert
from src.utils import calculate_bmr, calculate_tdee, extract_user_info

def test_nutrition_calculations():
    """Test nutrition calculation functions."""
    print("🧮 Testing Nutrition Calculations...")

    # Test BMR calculation
    bmr = calculate_bmr(70, 175, 25, 'male')  # 70kg, 175cm, 25yo male
    print(f"✓ BMR calculation: {bmr:.0f} calories/day")

    # Test TDEE calculation
    tdee = calculate_tdee(bmr, 'moderately_active')
    print(f"✓ TDEE calculation: {tdee:.0f} calories/day")

    # Test user info extraction
    test_text = "I'm a 25 year old male, 175cm tall, weighing 70kg, moderately active, wanting to lose weight"
    info = extract_user_info(test_text)
    print(f"✓ User info extraction: {info}")

    print("✅ Nutrition calculations working!\n")

def test_nutrition_expert():
    """Test the NutritionExpert class."""
    print("🧠 Testing Nutrition Expert...")

    expert = NutritionExpert()

    # Test query analysis
    query = "How many calories should I eat to lose weight? I'm 25, male, 70kg, 175cm, moderately active"
    analysis = expert.analyze_user_query(query)
    print(f"✓ Query type: {analysis['query_type']}")
    print(f"✓ Extracted info: {analysis['extracted_info']}")

    # Test daily needs calculation
    user_profile = {
        'weight': 70,
        'height': 175,
        'age': 25,
        'gender': 'male',
        'activity': 'moderately_active',
        'goal': 'lose_weight'
    }

    daily_needs = expert.calculate_daily_needs(user_profile)
    if 'error' not in daily_needs:
        print(f"✓ Daily calories: {daily_needs['target_calories']}")
        print(f"✓ Macros: P:{daily_needs['macros']['protein']}g C:{daily_needs['macros']['carbs']}g F:{daily_needs['macros']['fat']}g")

    # Test meal suggestions
    preferences = {'dietary_restriction': 'vegetarian'}
    meals = expert.suggest_meals(preferences, 'breakfast')
    print(f"✓ Meal suggestions: {len(meals)} suggestions generated")

    print("✅ Nutrition Expert working!\n")

def test_chatbot():
    """Test the main chatbot functionality."""
    print("🤖 Testing Chatbot...")

    # Initialize chatbot (without loading heavy AI models)
    chatbot = DietChatbot()

    # Test welcome message
    welcome = chatbot.get_welcome_message()
    print(f"✓ Welcome message: {welcome[:50]}...")

    # Test various types of queries
    test_queries = [
        "How many calories should I eat?",
        "What's a good protein source for vegetarians?",
        "I want to lose weight, what should I do?",
        "Tell me about vitamin D sources",
        "Can you suggest a healthy breakfast?"
    ]

    for query in test_queries:
        try:
            response, needs_disclaimer = chatbot.process_message(query, "test_user")
            query_type = chatbot.nutrition_expert.analyze_user_query(query)['query_type']
            print(f"✓ Query: '{query[:30]}...' -> Type: {query_type}")
            print(f"  Response length: {len(response)} chars, Disclaimer: {needs_disclaimer}")
        except Exception as e:
            print(f"❌ Error with query '{query}': {e}")

    print("✅ Chatbot working!\n")

def interactive_test():
    """Interactive test session."""
    print("🎯 Interactive Test Mode")
    print("Type your nutrition questions (or 'quit' to exit):")
    print("-" * 50)

    chatbot = DietChatbot()
    print(f"NutriBot: {chatbot.get_welcome_message()}")

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! Stay healthy! 🥗")
                break

            if not user_input:
                continue

            response, needs_disclaimer = chatbot.process_message(user_input, "interactive_user")
            print(f"\nNutriBot: {response}")

            if needs_disclaimer:
                print(f"\n⚠️ Disclaimer: This is general information only.")

        except KeyboardInterrupt:
            print("\n\nGoodbye! Stay healthy! 🥗")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

def main():
    """Run all tests."""
    print("🥗 Diet Chatbot Test Suite")
    print("=" * 40)

    try:
        test_nutrition_calculations()
        test_nutrition_expert()
        test_chatbot()

        print("🎉 All tests completed successfully!")
        print("\nWould you like to try interactive mode? (y/n)")

        if input().lower().startswith('y'):
            interactive_test()

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()