# AI Integration Setup

## Overview

Your PrivateGPT backend now includes AI integration capabilities using OpenAI's API. The system can operate in two modes:

1. **Test Mode** (Current): Uses predefined responses for testing
2. **Production Mode**: Uses OpenAI API for real AI responses

## Current Status: Test Mode

The system is currently running in **Test Mode** with intelligent fallback responses. This allows you to test the chat functionality without requiring an OpenAI API key.

## Setting Up OpenAI API (Production Mode)

To enable real AI responses, follow these steps:

### 1. Get OpenAI API Key

1. Go to [OpenAI's website](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to the API keys section
4. Create a new API key
5. Copy the key (it starts with `sk-`)

### 2. Update Environment Variables

Edit the `.env` file in the backend directory:

```bash
# Replace this line:
OPENAI_API_KEY=sk-placeholder-replace-with-your-real-api-key

# With your actual API key:
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Configure AI Settings (Optional)

You can customize the AI behavior by modifying these settings in `.env`:

```bash
OPENAI_MODEL=gpt-4o-mini          # AI model to use
OPENAI_MAX_TOKENS=1000            # Maximum response length
OPENAI_TEMPERATURE=0.7            # Response creativity (0-1)
```

### 4. Restart Backend Server

After updating the API key, restart your backend server:

```bash
# Stop the current server (Ctrl+C) and restart:
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Legal Professional Features

The AI integration includes:

- **Legal-focused prompts**: Responses tailored for legal professionals
- **Professional disclaimers**: Always reminds users that AI supplements, not replaces, professional judgment
- **Contextual responses**: Understands legal terminology and concepts
- **Privacy considerations**: Built with confidentiality in mind

## Cost Considerations

- OpenAI API usage is pay-per-token
- Current settings limit responses to 1000 tokens to control costs
- Monitor your usage at [OpenAI's usage dashboard](https://platform.openai.com/usage)

## Testing

Test your AI integration with these sample queries:

1. "What is a legal contract?"
2. "Hello, I need help with compliance"
3. "What can you help me with?"

## Troubleshooting

- **"Technical difficulties" message**: Check your API key and internet connection
- **Test mode responses**: Ensure your API key doesn't start with `sk-placeholder`
- **Server errors**: Check the console logs for detailed error messages

## Security Notes

- Never commit your actual API key to version control
- Keep the `.env` file secure and private
- Consider using environment variables in production deployments
