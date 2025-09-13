# Diet Chatbot - Deployment Guide

## 🚀 Hugging Face Spaces Deployment

### Prerequisites
- Hugging Face account
- Git installed locally

### Step-by-Step Deployment

1. **Create a new Hugging Face Space:**
   - Go to https://huggingface.co/spaces
   - Click "Create new Space"
   - Name: `diet-chatbot` (or your preferred name)
   - License: Apache 2.0
   - SDK: Gradio
   - Hardware: CPU Basic (free tier)

2. **Clone the Space repository:**
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/diet-chatbot
   cd diet-chatbot
   ```

3. **Copy project files:**
   Copy all files from this project to the Space repository:
   ```bash
   cp -r ../diet-chatbot/* .
   ```

4. **Ensure correct file structure:**
   ```
   diet-chatbot/
   ├── app.py              # Main Gradio application
   ├── requirements.txt    # Dependencies
   ├── README.md          # Space description
   ├── config/
   │   ├── prompts.py
   │   └── nutrition_data.py
   └── src/
       ├── chatbot.py
       ├── nutrition_expert.py
       ├── voice_handler.py
       └── utils.py
   ```

5. **Commit and push to deploy:**
   ```bash
   git add .
   git commit -m "Initial deployment of NutriBot diet chatbot"
   git push
   ```

6. **Wait for build and deployment:**
   - Hugging Face will automatically build and deploy your Space
   - Check the logs for any build errors
   - The app will be available at: `https://huggingface.co/spaces/YOUR_USERNAME/diet-chatbot`

### Troubleshooting

**If deployment fails:**

1. **Model loading issues:** The app will automatically fall back to simpler response generation if models fail to load
2. **Memory issues:** The current setup uses efficient models that should work on free tier
3. **Dependency issues:** All dependencies are tested and minimal

**Common fixes:**
- Reduce model size by changing `DialoGPT-small` to `DialoGPT-medium` in `src/chatbot.py`
- Remove optional dependencies from `requirements.txt` if needed
- Check Hugging Face Spaces logs for specific error messages

### Performance Optimization

For better performance:
1. **Upgrade to GPU:** Consider upgrading to GPU Basic for faster model inference
2. **Model caching:** Models are automatically cached after first load
3. **Enable persistent storage:** For conversation history persistence

### Features Available

✅ **Core Features (Working):**
- Text-based nutrition advice
- Calorie and macro calculations
- Meal planning suggestions
- Dietary restriction support
- Interactive Gradio interface

🚧 **Advanced Features (Optional):**
- Voice input/output (requires additional setup)
- Persistent user profiles
- Advanced AI model integration

### Security Considerations

- No user data is stored permanently
- All nutrition advice includes appropriate disclaimers
- Input validation prevents inappropriate queries

### Monitoring and Updates

- Monitor Space usage via Hugging Face dashboard
- Update by pushing to the Git repository
- Check logs for user feedback and error patterns

## 🧪 Local Testing

Before deployment, test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run demo
python demo.py

# Run tests
python test_chatbot.py

# Launch Gradio app
python app.py
```

## 🎯 Success Criteria

Your deployment is successful when:
- ✅ Space builds without errors
- ✅ Gradio interface loads properly
- ✅ Chatbot responds to nutrition queries
- ✅ Calorie calculations work correctly
- ✅ Example prompts function properly
- ✅ Error handling works gracefully

---

Happy deploying! 🥗🤖