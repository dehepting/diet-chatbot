import random
import torch
from typing import Dict, List, Tuple, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from config.prompts import SYSTEM_PROMPT, CONVERSATION_STARTERS, DISCLAIMER_TEXT
from src.nutrition_expert import NutritionExpert
from src.utils import validate_user_input

class DietChatbot:
    """
    Main chatbot class that combines conversational AI with nutrition expertise.
    """

    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        """
        Initialize the chatbot with specified model.

        Args:
            model_name: Hugging Face model name for conversation
        """
        self.model_name = model_name
        self.nutrition_expert = NutritionExpert()
        self.conversation_history = {}
        self.model = None
        self.tokenizer = None
        self._load_model()

    def _load_model(self):
        """Load the conversational AI model."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)

            # Add padding token if it doesn't exist
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            print(f"✅ Model {self.model_name} loaded successfully")
        except Exception as e:
            print(f"⚠️ Error loading model: {e}")
            print("🔄 Falling back to simple response generation")
            self.model = None
            self.tokenizer = None

    def get_welcome_message(self) -> str:
        """Get a random welcome message to start the conversation."""
        return random.choice(CONVERSATION_STARTERS)

    def process_message(self, message: str, user_id: str = "default") -> Tuple[str, bool]:
        """
        Process user message and generate appropriate response with conversation context.

        Args:
            message: User's input message
            user_id: Unique identifier for the user

        Returns:
            Tuple of (response, needs_disclaimer)
        """
        if not validate_user_input(message):
            return ("I'm here to help with nutrition and diet questions. Could you please ask me something about food, nutrition, or healthy eating?", False)

        # Initialize conversation history for user if doesn't exist
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []

        # Add user message to conversation history
        self.conversation_history[user_id].append({"role": "user", "content": message})

        # Analyze the query using nutrition expert
        analysis = self.nutrition_expert.analyze_user_query(message, user_id)

        # Check if we have enough info or need to ask follow-up questions
        response = self._generate_contextual_response(message, analysis, user_id)

        # Add bot response to conversation history
        self.conversation_history[user_id].append({"role": "assistant", "content": response})

        # Keep conversation history manageable (last 10 messages)
        if len(self.conversation_history[user_id]) > 20:
            self.conversation_history[user_id] = self.conversation_history[user_id][-20:]

        # Check if disclaimer is needed
        needs_disclaimer = self._needs_disclaimer(analysis['query_type'])

        return response, needs_disclaimer

    def _generate_contextual_response(self, message: str, analysis: Dict, user_id: str) -> str:
        """
        Generate contextual response that maintains conversation flow.
        """
        query_type = analysis['query_type']
        user_profile = analysis['user_profile']
        conversation = self.conversation_history[user_id]

        # Check if we're in the middle of gathering user info
        if len(conversation) >= 2:  # Has previous conversation
            last_bot_message = conversation[-2]["content"] if len(conversation) >= 2 else ""

            # If bot previously asked for info, and user is providing it
            if any(phrase in last_bot_message.lower() for phrase in ["i need", "please share", "what's your", "tell me about"]):
                # User is responding with their info
                daily_needs = self.nutrition_expert.calculate_daily_needs(user_profile)

                if daily_needs and "error" not in daily_needs:
                    return self._format_complete_advice(daily_needs, query_type, user_profile)
                else:
                    # Still missing info - ask specifically for what's needed
                    missing_info = daily_needs.get("error", "some information")
                    return self._ask_for_specific_info(missing_info, user_profile)

        # First time or general query - use original logic
        return self._generate_response(message, analysis, user_id)

    def _format_complete_advice(self, daily_needs: Dict, query_type: str, user_profile: Dict) -> str:
        """Format complete nutrition advice with all user data."""
        advice = f"""Perfect! Based on your information, here's your personalized nutrition plan:

🔥 **Daily Calories**: {daily_needs['target_calories']} calories
📊 **Macronutrient Breakdown**:
• Protein: {daily_needs['macros']['protein']}g ({int(daily_needs['macro_ratio']['protein']*100)}%)
• Carbs: {daily_needs['macros']['carbs']}g ({int(daily_needs['macro_ratio']['carbs']*100)}%)
• Fat: {daily_needs['macros']['fat']}g ({int(daily_needs['macro_ratio']['fat']*100)}%)

💡 **Your Numbers**:
• BMR (at rest): {daily_needs['bmr']} calories
• TDEE (with activity): {daily_needs['tdee']} calories

🎯 **Next Steps**: Would you like meal suggestions, specific recipes, or have questions about these numbers?"""

        return advice

    def _ask_for_specific_info(self, missing_info: str, current_profile: Dict) -> str:
        """Ask for specific missing information."""
        have_info = []
        need_info = []

        if 'age' in current_profile: have_info.append(f"Age: {current_profile['age']}")
        else: need_info.append("age")

        if 'weight' in current_profile: have_info.append(f"Weight: {current_profile['weight']:.0f} kg")
        else: need_info.append("weight")

        if 'height' in current_profile: have_info.append(f"Height: {current_profile['height']:.0f} cm")
        else: need_info.append("height")

        if 'gender' in current_profile: have_info.append(f"Gender: {current_profile['gender']}")
        else: need_info.append("gender")

        if 'activity' in current_profile: have_info.append(f"Activity: {current_profile['activity']}")
        else: need_info.append("activity level")

        response = "Thanks! I have: " + ", ".join(have_info) if have_info else "I'm gathering your information."
        response += f"\n\n🤔 I still need your **{' and '.join(need_info)}** to calculate your personalized nutrition plan."
        response += f"\n\nCould you tell me your {need_info[0]}?"

        return response

    def _generate_response(self, message: str, analysis: Dict, user_id: str) -> str:
        """
        Generate response based on message analysis.

        Args:
            message: Original user message
            analysis: Analysis results from nutrition expert
            user_id: User identifier

        Returns:
            Generated response string
        """
        query_type = analysis['query_type']
        user_profile = analysis['user_profile']

        # Handle specific nutrition queries with expert knowledge
        if query_type == "calorie_calculation":
            return self._handle_calorie_query(user_profile, analysis)

        elif query_type == "macro_advice":
            return self._handle_macro_query(message, user_profile)

        elif query_type == "meal_planning":
            return self._handle_meal_planning(message, user_profile)

        elif query_type == "nutrient_advice":
            return self._handle_nutrient_query(message)

        elif query_type in ["weight_loss", "weight_gain"]:
            return self._handle_weight_goal_query(query_type, user_profile)

        elif query_type == "recipe_advice":
            return self._handle_recipe_query(message, user_profile)

        else:
            # General nutrition conversation
            return self._generate_conversational_response(message, user_id)

    def _handle_calorie_query(self, user_profile: Dict, analysis: Dict) -> str:
        """Handle calorie calculation queries."""
        return self.nutrition_expert.generate_personalized_advice(user_profile, "calorie_calculation")

    def _handle_macro_query(self, message: str, user_profile: Dict) -> str:
        """Handle macronutrient-related queries."""
        daily_needs = self.nutrition_expert.calculate_daily_needs(user_profile)

        if daily_needs and "error" not in daily_needs:
            macros = daily_needs['macros']
            return f"""Here's your daily macronutrient breakdown:

🥩 **Protein: {macros['protein']}g**
• Builds and repairs muscle tissue
• Aim for 20-30g per meal
• Good sources: chicken, fish, eggs, beans, yogurt

🍞 **Carbohydrates: {macros['carbs']}g**
• Primary energy source for your body
• Focus on complex carbs (oats, quinoa, sweet potato)
• Time around workouts for best utilization

🥑 **Fats: {macros['fat']}g**
• Essential for hormone production and nutrient absorption
• Include healthy fats: nuts, olive oil, avocado, fatty fish
• About 20-35% of total calories

💡 **Pro tip**: Don't stress about hitting exact numbers daily - focus on weekly averages and listen to your body!"""
        else:
            return """To give you personalized macro recommendations, I'd need to know:

📝 Your age, weight, height, and gender
🏃 Your activity level
🎯 Your specific goals (lose weight, gain muscle, maintain)

Generally, a balanced approach includes:
• **Protein**: 0.8-1.2g per lb bodyweight
• **Carbs**: 45-65% of total calories
• **Fat**: 20-35% of total calories"""

    def _handle_meal_planning(self, message: str, user_profile: Dict) -> str:
        """Handle meal planning queries."""
        preferences = {
            'dietary_restriction': user_profile.get('dietary_restriction', ''),
            'calorie_target': user_profile.get('target_calories', 2000)
        }

        # Determine meal type from message
        meal_type = "any"
        if "breakfast" in message.lower():
            meal_type = "breakfast"
        elif "lunch" in message.lower():
            meal_type = "lunch"
        elif "dinner" in message.lower():
            meal_type = "dinner"
        elif "snack" in message.lower():
            meal_type = "snack"

        suggestions = self.nutrition_expert.suggest_meals(preferences, meal_type)

        if not suggestions:
            return "I'd love to help with meal planning! Could you tell me about any dietary restrictions or preferences you have?"

        response = f"🍽️ **Meal Suggestions for {meal_type.title() if meal_type != 'any' else 'You'}:**\n\n"

        for i, suggestion in enumerate(suggestions, 1):
            response += f"**{i}. {suggestion['meal']}**\n"
            response += f"• Ingredients: {', '.join(suggestion['ingredients'])}\n"
            response += f"• {suggestion['description']}\n"
            response += f"• Prep time: {suggestion['prep_time']}\n\n"

        response += "💡 **Tip**: Prepare ingredients in advance for quicker meal assembly during busy days!"

        return response

    def _handle_nutrient_query(self, message: str) -> str:
        """Handle nutrient-specific queries."""
        # Extract nutrient from message
        nutrients = ['vitamin c', 'vitamin d', 'vitamin b12', 'iron', 'calcium', 'omega 3', 'fiber', 'potassium']
        found_nutrient = None

        for nutrient in nutrients:
            if nutrient in message.lower():
                found_nutrient = nutrient
                break

        if found_nutrient:
            sources = self.nutrition_expert.get_nutrient_sources(found_nutrient)
            if sources:
                return f"🌟 **Great sources of {found_nutrient.title()}:**\n\n" + \
                       "\n".join([f"• {source}" for source in sources]) + \
                       f"\n\n💡 **Tip**: Try to get nutrients from whole foods when possible - they're better absorbed than supplements!"
            else:
                return f"I'd be happy to help with {found_nutrient} information! Could you be more specific about what you'd like to know?"

        return """I can help you learn about various nutrients! Some popular ones include:

🌟 **Vitamins**: C, D, B12
⚡ **Minerals**: Iron, Calcium, Potassium
🐟 **Essential Fats**: Omega-3 fatty acids
🌾 **Fiber**: For digestive health

What specific nutrient would you like to know more about?"""

    def _handle_weight_goal_query(self, query_type: str, user_profile: Dict) -> str:
        """Handle weight goal related queries."""
        return self.nutrition_expert.generate_personalized_advice(user_profile, query_type)

    def _handle_recipe_query(self, message: str, user_profile: Dict) -> str:
        """Handle recipe and cooking queries."""
        return """🍳 **Healthy Cooking Tips:**

**Quick & Nutritious Ideas:**
• **Protein + Veggie Bowl**: Any lean protein with roasted vegetables
• **Smoothie**: Protein powder, spinach, berries, almond milk
• **Egg Scramble**: Eggs with whatever vegetables you have on hand

**Cooking Methods for Health:**
• Baking, grilling, or steaming instead of frying
• Use herbs and spices instead of excess salt
• Meal prep 2-3 dishes on Sunday for the week

**Smart Substitutions:**
• Greek yogurt instead of sour cream
• Cauliflower rice instead of regular rice
• Zucchini noodles for pasta

What type of dish or cooking method would you like specific guidance on?"""

    def _generate_conversational_response(self, message: str, user_id: str) -> str:
        """Generate conversational response using AI model or fallback."""
        if self.model and self.tokenizer:
            try:
                return self._generate_ai_response(message, user_id)
            except Exception as e:
                print(f"Error generating AI response: {e}")
                return self._generate_fallback_response(message)
        else:
            return self._generate_fallback_response(message)

    def _generate_ai_response(self, message: str, user_id: str) -> str:
        """Generate response using the AI model."""
        # Prepare conversation context
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []

        # Add system context for nutrition focus
        context = f"{SYSTEM_PROMPT}\n\nUser: {message}\nNutriBot:"

        # Tokenize input
        inputs = self.tokenizer.encode(context, return_tensors='pt', max_length=512, truncation=True)

        # Generate response
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=inputs.shape[1] + 150,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                no_repeat_ngram_size=3
            )

        # Decode response
        response = self.tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)

        # Clean up response
        response = response.split('\n')[0].strip()
        if not response:
            return self._generate_fallback_response(message)

        return response

    def _generate_fallback_response(self, message: str) -> str:
        """Generate fallback response when AI model is not available."""
        fallback_responses = [
            "That's a great nutrition question! Could you provide more details so I can give you the best advice?",
            "I'm here to help with your nutrition goals. What specific aspect would you like to focus on?",
            "Thanks for your question! To give you personalized advice, could you share more about your current situation?",
            "I'd love to help you with that! Could you tell me more about your dietary preferences or goals?",
            "That's an interesting nutrition topic. What would you like to know specifically?"
        ]
        return random.choice(fallback_responses)

    def _needs_disclaimer(self, query_type: str) -> bool:
        """Check if response needs medical disclaimer."""
        medical_topics = ["weight_loss", "weight_gain", "nutrient_advice", "calorie_calculation"]
        return query_type in medical_topics

    def reset_conversation(self, user_id: str = "default"):
        """Reset conversation history for a user."""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]

        # Also reset user profile in nutrition expert
        if hasattr(self.nutrition_expert, 'user_profiles') and user_id in self.nutrition_expert.user_profiles:
            del self.nutrition_expert.user_profiles[user_id]