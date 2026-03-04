"""
Bot Configuration

Secrets are loaded from .env file.
All other settings are configured here.
"""
import os
from typing import List
from dotenv import load_dotenv

# Load secrets from .env
load_dotenv()

# =============================================================================
# SECRETS (from .env - do not hardcode!)
# =============================================================================
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# =============================================================================
# BOT SETTINGS
# =============================================================================
BOT_PREFIX = ">>>"
BOT_OWNER_ID = 543649762000371713

# Channel IDs where the bot will respond to mentions
ALLOWED_CHANNEL_IDS: List[int] = [
    1332317261213466705,
    1333745401408393236,
    1336264642313453610,
    1470384208504553615,
    1477537115297550492
]

# =============================================================================
# GROQ API SETTINGS
# =============================================================================
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_TEMPERATURE = 0.7  # 0.0 = focused, 1.0 = creative
GROQ_MAX_TOKENS = 1000  # Max response length

# Model hierarchy - fallback to next model if rate limited (429 error)
# Ordered by quality (best first)
GROQ_MODEL_HIERARCHY: List[str] = [
    "llama-3.3-70b-versatile",              # Best quality, 100K TPD
    "meta-llama/llama-4-scout-17b-16e-instruct",  # Llama 4, 500K TPD
    "openai/gpt-oss-120b",                  # 120B params, 200K TPD
    "qwen/qwen3-32b",                       # Good quality, 500K TPD
    "llama-3.1-8b-instant",                 # Fast, 500K TPD
]

# System prompt - defines the bot's personality and behavior
GROQ_SYSTEM_PROMPT = """You are PrawnKing, a Discord bot with a humorous personality.

Personality:
- Friendly and genuinely helpful
- Keep responses SHORT - maximum 5 sentences

Rules:
- ALWAYS respond in the same language the user is using
- Answer any questions helpfully, but avoid sensitive topics
- NEVER make up facts - if you're unsure about something, say so honestly
- Use Discord formatting when helpful (bold, code blocks, etc.)
- Messages show usernames in [brackets] for context - do NOT copy this format in your responses
"""

# =============================================================================
# CONVERSATION MEMORY SETTINGS
# =============================================================================
MEMORY_MAX_MESSAGES = 50       # Max messages to remember per channel
MEMORY_IDLE_TIMEOUT = 60       # Seconds of inactivity before memory resets


# =============================================================================
# VALIDATION
# =============================================================================
def validate_config() -> List[str]:
    """Validate that required secrets are set."""
    errors = []
    if not DISCORD_BOT_TOKEN:
        errors.append("DISCORD_BOT_TOKEN is not set in .env")
    if not GROQ_API_KEY:
        errors.append("GROQ_API_KEY is not set in .env")
    return errors
