import gradio as gr
from typing import List, Tuple
from src.chatbot import DietChatbot
from config.prompts import EXAMPLE_PROMPTS, DISCLAIMER_TEXT

class SimpleDietChatbotApp:
    """
    Simplified Gradio application for the Diet Advice Chatbot (text-only for initial testing).
    """

    def __init__(self):
        # Initialize with a simpler model or fallback mode
        try:
            self.chatbot = DietChatbot(model_name="microsoft/DialoGPT-small")  # Smaller model for faster loading
        except:
            # Fallback initialization without AI model
            self.chatbot = DietChatbot()
            print("⚠️ Running in fallback mode without AI model")

    def chat_interface(self, message: str, history: List[List[str]]) -> Tuple[str, List[List[str]]]:
        """
        Handle text-based chat interaction.

        Args:
            message: User's text message
            history: Conversation history

        Returns:
            Tuple of (empty_string, updated_history)
        """
        if not message.strip():
            return "", history

        try:
            # Process message with chatbot
            response, needs_disclaimer = self.chatbot.process_message(message)

            # Add disclaimer if needed
            if needs_disclaimer:
                response += f"\n\n{DISCLAIMER_TEXT}"

            # Update history
            history.append([message, response])

            return "", history

        except Exception as e:
            error_response = f"I apologize, but I encountered an error processing your message. Please try rephrasing your question about nutrition or diet."
            history.append([message, error_response])
            return "", history

    def get_example_response(self, example: str, history: List[List[str]]) -> Tuple[str, List[List[str]]]:
        """
        Handle example prompt clicks.

        Args:
            example: Example prompt text
            history: Current conversation history

        Returns:
            Tuple of (empty_string, updated_history)
        """
        return self.chat_interface(example, history)

    def clear_conversation(self) -> List[List[str]]:
        """
        Clear the conversation history.

        Returns:
            Empty history list
        """
        self.chatbot.reset_conversation()
        return []

    def create_interface(self) -> gr.Blocks:
        """
        Create the Gradio interface.

        Returns:
            Gradio Blocks interface
        """
        with gr.Blocks(
            title="NutriBot - Your AI Nutrition Coach",
            theme=gr.themes.Soft(),
        ) as interface:

            # Header
            gr.HTML("""
            <div style="text-align: center; padding: 20px;">
                <h1>🥗 NutriBot - Your AI Nutrition Coach</h1>
                <p>Get personalized nutrition advice and diet guidance!</p>
            </div>
            """)

            # Main chatbot interface
            chatbot_component = gr.Chatbot(
                value=[[None, self.chatbot.get_welcome_message()]],
                height=500,
                label="Chat with NutriBot",
                show_label=True
            )

            # Text input area
            with gr.Row():
                text_input = gr.Textbox(
                    placeholder="Continue the conversation or ask a new question... (Press Enter to send)",
                    label="💬 Chat with NutriBot",
                    lines=2,
                    max_lines=4,
                    scale=4
                )
                with gr.Column(scale=1):
                    text_submit_btn = gr.Button("Send", variant="primary", size="lg")
                    clear_btn = gr.Button("New Conversation", variant="secondary")

            # Conversation help
            gr.HTML("""
            <div style="background-color: #f0f8ff; padding: 10px; border-radius: 5px; margin: 10px 0;">
                <small><strong>💡 Tip:</strong> Keep chatting! Ask follow-up questions like "What about meal suggestions?" or "Can you adjust for higher activity?"</small>
            </div>
            """)

            # Example prompts
            gr.HTML("<h3>💡 Try these example questions:</h3>")

            with gr.Row():
                example_buttons = []
                for example in EXAMPLE_PROMPTS[:4]:
                    btn = gr.Button(example, size="sm", scale=1)
                    example_buttons.append(btn)

            with gr.Row():
                for example in EXAMPLE_PROMPTS[4:8]:
                    btn = gr.Button(example, size="sm", scale=1)
                    example_buttons.append(btn)

            # Features info
            gr.HTML("""
            <div style="background-color: #e8f5e8; padding: 15px; border-radius: 10px; margin: 20px 0;">
                <h3>🌟 What I can help you with:</h3>
                <ul style="text-align: left;">
                    <li><strong>Calorie Calculations:</strong> BMR, TDEE, and daily calorie needs</li>
                    <li><strong>Macro Planning:</strong> Protein, carbs, and fat distribution</li>
                    <li><strong>Meal Suggestions:</strong> Healthy meal ideas and recipes</li>
                    <li><strong>Nutrition Info:</strong> Vitamins, minerals, and nutrient sources</li>
                    <li><strong>Diet Goals:</strong> Weight loss, gain, or maintenance guidance</li>
                    <li><strong>Special Diets:</strong> Vegetarian, vegan, keto, and other dietary preferences</li>
                </ul>
            </div>
            """)

            # Disclaimer
            gr.HTML(f"""
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin-top: 20px;">
                <p style="margin: 0;"><strong>Important:</strong> {DISCLAIMER_TEXT}</p>
            </div>
            """)

            # Event handlers

            # Text input handlers
            text_submit_btn.click(
                fn=self.chat_interface,
                inputs=[text_input, chatbot_component],
                outputs=[text_input, chatbot_component]
            )

            text_input.submit(
                fn=self.chat_interface,
                inputs=[text_input, chatbot_component],
                outputs=[text_input, chatbot_component]
            )

            # Clear conversation handler
            clear_btn.click(
                fn=self.clear_conversation,
                outputs=[chatbot_component],
                postprocess=lambda: [[None, self.chatbot.get_welcome_message()]]
            )

            # Example button handlers
            for i, btn in enumerate(example_buttons):
                if i < len(EXAMPLE_PROMPTS):
                    example_text = EXAMPLE_PROMPTS[i]
                    # Create a closure to capture the example text
                    def create_example_handler(example):
                        def handler(history):
                            return self.get_example_response(example, history)
                        return handler

                    btn.click(
                        fn=create_example_handler(example_text),
                        inputs=[chatbot_component],
                        outputs=[text_input, chatbot_component]
                    )

        return interface

def main():
    """
    Main function to launch the application.
    """
    print("🚀 Starting NutriBot...")

    # Initialize and launch the app
    try:
        app = SimpleDietChatbotApp()
        interface = app.create_interface()

        print("✅ NutriBot initialized successfully!")

        # Launch with appropriate settings
        interface.launch(
            server_name="0.0.0.0",  # Allow external access
            server_port=7860,       # Default port for Hugging Face Spaces
            share=False,            # Set to True for temporary sharing link
            inbrowser=False,        # Don't auto-open browser in server environment
            show_error=True,        # Show errors in the interface
            quiet=False             # Show startup messages
        )

    except Exception as e:
        print(f"❌ Error launching NutriBot: {e}")
        raise

if __name__ == "__main__":
    main()