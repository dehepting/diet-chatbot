#!/usr/bin/env python3
"""
Quick demo of the Diet Chatbot functionality.
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.chatbot import DietChatbot

def run_demo():
    """Run a demonstration of the chatbot."""
    print("🥗 NutriBot Demo")
    print("=" * 30)

    # Initialize chatbot
    chatbot = DietChatbot()

    # Welcome message
    print(f"NutriBot: {chatbot.get_welcome_message()}")
    print()

    # Demo conversation
    demo_queries = [
        "I'm a 25 year old male, 175cm tall, 70kg, moderately active. How many calories should I eat to lose weight?",
        "What's a good high-protein breakfast for someone trying to lose weight?",
        "What foods are rich in vitamin D?",
        "Can you suggest a meal plan for someone on a vegetarian diet?"
    ]

    for query in demo_queries:
        print(f"User: {query}")
        response, needs_disclaimer = chatbot.process_message(query, "demo_user")
        print(f"NutriBot: {response}")

        if needs_disclaimer:
            print("\n⚠️ Note: This is general nutritional information only.")

        print("\n" + "-" * 60 + "\n")

    print("Demo completed! 🎉")

if __name__ == "__main__":
    run_demo()