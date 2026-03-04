"""
Shared bot commands as a Discord Cog.
Provides common commands for all bot variants.
"""
import os
import sys
import logging
import asyncio
import discord
import requests
from discord.ext import commands
from calculator_view import CalculatorView
from config import GROQ_API_KEY, GROQ_API_URL, GROQ_MODEL_HIERARCHY

logger = logging.getLogger(__name__)


class BotCommands(commands.Cog):
    """Common commands shared across bot variants."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def stop(self, ctx: commands.Context):
        """Shut down the bot. Owner only."""
        logger.info(f"Stop command issued by {ctx.author}")
        await ctx.send("Shutting down the bot...")
        await self.bot.close()

    @commands.command()
    @commands.is_owner()
    async def restart(self, ctx: commands.Context):
        """Restart the bot. Owner only."""
        import subprocess
        logger.info(f"Restart command issued by {ctx.author}")
        await ctx.send("Restarting the bot...")
        
        # Spawn new process before closing (Windows-compatible)
        subprocess.Popen(
            [sys.executable, "bot.py"],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        # Exit current process
        await self.bot.close()
        os._exit(0)

    @commands.command()
    async def calculator(self, ctx: commands.Context):
        """Open an interactive calculator."""
        view = CalculatorView()
        await ctx.send("```0```", view=view)

    @commands.command()
    async def roast(self, ctx: commands.Context, target: discord.Member = None):
        """Roast a user! Usage: >>>roast @User"""
        if target is None:
            await ctx.send("You gotta tag someone to roast! Usage: `>>>roast @User`")
            return
        
        if target == self.bot.user:
            await ctx.send("Nice try. I'm unroastable. 🦐")
            return

        async with ctx.typing():
            prompt = (
                f"Roast the user named '{target.display_name}' as hard as possible. "
                "Rules you MUST follow:\n"
                "- Be SAVAGE and BRUTAL, but as friendly as possible. Go for the ego, the confidence, the life choices.\n"
                "- Absolutely NO bad words, slurs, or profanity. Clean language only.\n"
                "- NO puns. NO wordplay. NO dad jokes. Straight-up savage observations.\n"
                "- Keep it short, devastating, and funny.\n"
                "- Make it sound like a confident roast comedian on stage.\n"
                "- Do NOT hold back. The goal is to make everyone laugh."
            )

            # Try each model in hierarchy
            for model in GROQ_MODEL_HIERARCHY:
                try:
                    response = requests.post(
                        GROQ_API_URL,
                        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                        json={
                            "model": model,
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 1.0,
                            "max_tokens": 150,
                        },
                        timeout=10,
                    )
                    if response.status_code == 429:
                        continue
                    response.raise_for_status()
                    data = response.json()
                    roast_text = data["choices"][0]["message"]["content"].strip()
                    await ctx.send(f"{target.mention} {roast_text}")
                    return
                except Exception as e:
                    logger.warning(f"Roast failed on {model}: {e}")
                    continue

            await ctx.send(f"{target.mention} You're so boring even my AI refused to roast you.")

    @commands.command(name="help")
    async def help_command(self, ctx: commands.Context):
        """Display bot commands and capabilities."""
        embed = discord.Embed(
            title="🦐 PrawnKing Bot Help",
            description="Here's what I can do!",
            color=discord.Color.orange()
        )
        
        embed.add_field(
            name="💬 Chat with me",
            value="Mention me (@PrawnKing) in an allowed channel and I'll respond!",
            inline=False
        )
        
        embed.add_field(
            name="📝 Commands",
            value=(
                "**>>>calculator** - Open interactive calculator\n"
                "**>>>roast @User** - Roast someone (HEHEHEHA)\n"
                "**>>>help** - Show this help message\n"
                "**>>>stop** - Shut down bot (owner only)\n"
                "**>>>restart** - Restart bot (owner only)"
            ),
            inline=False
        )
        
        embed.add_field(
            name="✨ Features",
            value=(
                "• Per-channel conversation memory (60s timeout)\n"
                "• Recognizes who's talking & reply context\n"
                "• Responds in your language\n"
            ),
            inline=False
        )
        
        embed.set_footer(text="Created by XJ | Prawns are the ultimate life form")
        
        await ctx.send(embed=embed)

    @stop.error
    @restart.error
    async def owner_command_error(self, ctx: commands.Context, error):
        """Handle errors for owner-only commands."""
        if isinstance(error, commands.NotOwner):
            await ctx.send("You do not have permission to use this command.")
        else:
            logger.error(f"Command error: {error}")
            await ctx.send(f"An error occurred: {error}")


async def setup(bot: commands.Bot):
    """Setup function for loading the cog."""
    await bot.add_cog(BotCommands(bot))
