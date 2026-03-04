# 🦐 PrawnKing Discord Bot

> A fully functional, AI-powered Discord chatbot built with Python and the Groq Cloud API, serving as both a working bot and an educational guide.

![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)
![Python](https://img.shields.io/badge/python-3.9%2B-3776AB?style=flat-square&logo=python)

<p align="center">
  <img src="architecture_diagram.png" alt="PrawnKing Bot Architecture Diagram" width="800">
</p>

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running](#running)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Features

- **AI Conversation API:** Integrates with the blazingly fast Groq API (using Llama 3.3 70B by default).
- **Educational Guide:** Includes a comprehensive companion guide (`chatbot_guide.md`) explaining LLMs and bot architecture.
- **Model Fallback System:** Automatically switches to backup models if rate limits are hit.
- **Contextual Memory:** Maintains a 60-second rolling per-channel conversation history.
- **Smart Replies:** Understands who is talking and reads user replies for context.
- **Interactive UI Components:** Includes a fully functional Discord calculator with clickable buttons inside the chat.
- **Fun Commands:** Includes a dedicated LLM-powered roasting command (`>>>roast @User`).

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3 |
| Framework | discord.py |
| AI API | Groq API (Llama 3 models) |
| HTTP Client | requests |
| Configuration | python-dotenv |

## Getting Started

### Prerequisites

- Python 3.9 or higher
- A registered Discord Bot App (get your Bot Token from the [Discord Developer Portal](https://discord.com/developers/applications))
- A free Groq API key (get one from the [GroqCloud Console](https://console.groq.com/))

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/dbot_project.git
cd dbot_project

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create a .env file and add your tokens
echo 'DISCORD_BOT_TOKEN="your_discord_bot_token_here"' > .env
echo 'GROQ_API_KEY="your_groq_api_key_here"' >> .env
```

### Running

```bash
# Start the bot
python bot.py
```

You should see logs in your terminal indicating the bot is ready and logged in.

## Usage

Once the bot is running and invited to your Discord server, you can interact with it in any of the allowed channels.

| Command | Description |
|---|---|
| `@PrawnKing [message]` | Chat with the bot naturally — it remembers context! |
| `>>>help` | Show the help menu with all available commands |
| `>>>calculator` | Open an interactive calculator right in the chat |
| `>>>roast @User` | Generate a brutal (but clean) AI roast of the tagged user |
| `>>>stop` | Shut down the bot *(Owner Only)* |
| `>>>restart` | Restart the bot process *(Owner Only)* |

## Configuration

You can customize the bot's behavior by modifying properties in `config.py`:

- **Channels:** Add or remove Discord channel IDs from `ALLOWED_CHANNEL_IDS` where the bot is permitted to respond.
- **Owner ID:** Change `BOT_OWNER_ID` to your Discord User ID.
- **Personality:** Edit `GROQ_SYSTEM_PROMPT` to change how the bot behaves and speaks.
- **Memory Rules:** Adjust `MEMORY_MAX_MESSAGES` and `MEMORY_IDLE_TIMEOUT` to tweak the bot's context retention.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/your-feature`)
3. Commit your changes (`git commit -m 'feat: add your feature'`)
4. Push to the branch (`git push origin feat/your-feature`)
5. Open a Pull Request

Please make sure to test your code before submitting a Pull Request.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
