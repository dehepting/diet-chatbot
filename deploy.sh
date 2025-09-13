#!/bin/bash

# Deploy script for NutriBot
# Usage: ./deploy.sh "commit message"

if [ -z "$1" ]; then
    echo "Usage: ./deploy.sh 'commit message'"
    exit 1
fi

COMMIT_MSG="$1"
GITHUB_DIR="/Users/davidhepting/mess_around_2/diet-chatbot"
HF_SPACE_DIR="/Users/davidhepting/diet-chatbot"  # Your HF Space directory

echo "🚀 Deploying NutriBot..."

# 1. Commit to GitHub
echo "📝 Committing to GitHub..."
cd "$GITHUB_DIR"
git add .
git commit -m "$COMMIT_MSG"
git push origin main

# 2. Sync to HuggingFace Space
echo "🤗 Syncing to Hugging Face Space..."
cd "$HF_SPACE_DIR"
cp -r "$GITHUB_DIR"/* .
git add .
git commit -m "Deploy: $COMMIT_MSG"
git push

echo "✅ Deployment complete!"
echo "📱 GitHub: https://github.com/dehepting/diet-chatbot"
echo "🌐 Live App: https://huggingface.co/spaces/dehepting/diet-chatbot"