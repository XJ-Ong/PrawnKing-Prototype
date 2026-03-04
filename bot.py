"""
Unified Discord Bot - Supports both Manual and LLM response modes.

Usage:
    python bot.py    # Interactive mode selection
"""
import sys
import logging
import time
import discord
from discord.ext import commands
import requests
from typing import Dict, List

from config import (
    BOT_PREFIX,
    DISCORD_BOT_TOKEN,
    ALLOWED_CHANNEL_IDS,
    GROQ_API_KEY,
    GROQ_API_URL,
    GROQ_MODEL_HIERARCHY,
    MEMORY_MAX_MESSAGES,
    MEMORY_IDLE_TIMEOUT,
    validate_config,
)
from bot_commands import BotCommands

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# Conversation Memory
# =============================================================================

# Per-channel conversation history: {channel_id: {"messages": [...], "last_active": timestamp}}
conversation_memory: Dict[int, dict] = {}


def get_channel_memory(channel_id: int) -> List[dict]:
    """Get conversation history for a channel, clearing if idle too long."""
    current_time = time.time()
    
    if channel_id in conversation_memory:
        channel_data = conversation_memory[channel_id]
        # Check if memory has expired
        if current_time - channel_data["last_active"] > MEMORY_IDLE_TIMEOUT:
            logger.info(f"Memory expired for channel {channel_id}, clearing...")
            conversation_memory[channel_id] = {"messages": [], "last_active": current_time}
            return []
        return channel_data["messages"]
    else:
        # Initialize memory for new channel
        conversation_memory[channel_id] = {"messages": [], "last_active": current_time}
        return []


def add_to_memory(channel_id: int, role: str, content: str, username: str = None):
    """Add a message to channel memory."""
    if channel_id not in conversation_memory:
        conversation_memory[channel_id] = {"messages": [], "last_active": time.time()}
    
    channel_data = conversation_memory[channel_id]
    channel_data["last_active"] = time.time()
    
    # Add user attribution for user messages
    if role == "user" and username:
        content = f"[{username}]: {content}"
    
    channel_data["messages"].append({"role": role, "content": content})
    
    # Trim to max messages
    if len(channel_data["messages"]) > MEMORY_MAX_MESSAGES:
        channel_data["messages"] = channel_data["messages"][-MEMORY_MAX_MESSAGES:]


def clear_channel_memory(channel_id: int):
    """Clear memory for a specific channel."""
    if channel_id in conversation_memory:
        del conversation_memory[channel_id]
        logger.info(f"Cleared memory for channel {channel_id}")


# =============================================================================
# Response Generators
# =============================================================================

def generate_llm_response(channel_id: int, prompt: str, username: str) -> str:
    """Generate response using Groq API with conversation memory and model fallback."""
    from config import GROQ_SYSTEM_PROMPT, GROQ_TEMPERATURE, GROQ_MAX_TOKENS
    
    # Get existing conversation history
    history = get_channel_memory(channel_id)
    
    # Add current message to memory
    add_to_memory(channel_id, "user", prompt, username)
    
    # Build messages list: system + history + current
    messages = [{"role": "system", "content": GROQ_SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": f"[{username}]: {prompt}"})
    
    # Try each model in the hierarchy
    for model in GROQ_MODEL_HIERARCHY:
        try:
            response = requests.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": GROQ_TEMPERATURE,
                    "max_tokens": GROQ_MAX_TOKENS,
                },
                timeout=30
            )
            
            # Check for rate limit (429) - try next model
            if response.status_code == 429:
                logger.warning(f"Rate limited on {model}, trying next model...")
                continue
            
            response.raise_for_status()
            
            # Success - extract response and add to memory
            data = response.json()
            result = data["choices"][0]["message"]["content"].strip()
            
            # Add assistant response to memory
            add_to_memory(channel_id, "assistant", result)
            
            logger.info(f"Response generated using model: {model}")
            return result
            
        except requests.Timeout:
            logger.warning(f"Timeout on {model}, trying next model...")
            continue
        except requests.RequestException as e:
            logger.warning(f"Error with {model}: {e}, trying next model...")
            continue
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing response from {model}: {e}")
            continue
    
    # All models exhausted
    logger.error("All models exhausted or rate limited")
    return "Sorry, all AI models are currently unavailable. Please try again later."


# =============================================================================
# Bot Setup
# =============================================================================

# Create bot instance
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents, help_command=None)


@bot.event
async def on_ready():
    """Called when bot is connected and ready."""
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    logger.info("Running in LLM mode")
    logger.info("-" * 40)
    # Load shared commands cog
    await bot.add_cog(BotCommands(bot))
    logger.info("Loaded BotCommands cog")


@bot.event
async def on_message(message: discord.Message):
    """Handle incoming messages."""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Check if message is in allowed channel and mentions the bot
    # Skip if it's a command (starts with prefix) to avoid double-responding
    if (message.channel.id in ALLOWED_CHANNEL_IDS 
        and bot.user.mentioned_in(message)
        and not message.content.startswith(BOT_PREFIX)):
        # Clean the message
        cleaned_message = message.content.replace(f"<@{bot.user.id}>", "").strip()
        
        # Log incoming message
        logger.info(f"[CHAT IN] #{message.channel.name} | {message.author.display_name}: {cleaned_message}")
        
        # Check if user is replying to a previous message
        reply_context = ""
        if message.reference and message.reference.message_id:
            try:
                replied_msg = await message.channel.fetch_message(message.reference.message_id)
                reply_author = replied_msg.author.display_name
                reply_content = replied_msg.content[:200]  # Limit context length
                if replied_msg.author == bot.user:
                    reply_context = f"[Replying to bot's message: \"{reply_content}\"]\n"
                else:
                    reply_context = f"[Replying to {reply_author}'s message: \"{reply_content}\"]\n"
                logger.info(f"[REPLY CONTEXT] {reply_context.strip()}")
            except Exception as e:
                logger.warning(f"Could not fetch replied message: {e}")
        
        # Combine reply context with user message
        full_message = reply_context + cleaned_message
        
        # Generate LLM response
        async with message.channel.typing():
            response = generate_llm_response(
                message.channel.id,
                full_message,
                message.author.display_name
            )
            
            # Log bot response
            logger.info(f"[CHAT OUT] #{message.channel.name} | Bot: {response[:200]}{'...' if len(response) > 200 else ''}")
            
            # Split long messages (Discord limit is 2000 characters)
            if len(response) > 2000:
                parts = [response[i:i+2000] for i in range(0, len(response), 2000)]
                for part in parts:
                    await message.reply(part, mention_author=False)
            else:
                await message.reply(response, mention_author=False)

    # Process commands
    await bot.process_commands(message)


def main():
    """Main entry point."""
    
    # Validate configuration
    errors = validate_config()
    if errors:
        for error in errors:
            logger.error(error)
        raise SystemExit(1)

    print(f"\nStarting bot in LLM mode...")
    
    # Run the bot
    try:
        bot.run(DISCORD_BOT_TOKEN)
    except discord.LoginFailure:
        logger.error("Invalid Discord token. Please check your .env file.")
        raise SystemExit(1)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise


if __name__ == "__main__":
    main()
