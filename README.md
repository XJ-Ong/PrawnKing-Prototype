# 🦐 PrawnKing Discord Bot

> Just a random, funsies Discord bot built with Python and the Groq Cloud API. 

This is my personal side project! It's a fully functional AI-powered chatbot with conversation memory and some fun utility commands.

<p align="center">
  <img src="architecture_diagram.png" alt="PrawnKing Bot Architecture" width="800">
</p>

## ✨ What does it do?

- **AI Chatting:** Talk to it normally in text channels! It remembers the last 60 seconds of context and knows who is talking.
- **Roasting:** Use `>>>roast @User` for an unapologetically savage (but clean) AI roast.
- **Calculator:** Use `>>>calculator` to spawn down an interactive math calculator right in the chat with clickable Discord buttons.
- **Smart Fallback:** If the main AI model gets rate-limited, it automatically falls back to backup models so it never goes offline.

## 📖 How does it work?

Are you a beginner who wants to know how LLMs, Groq, and Discord bots actually work under the hood? I wrote a full guide mapping out everything! 

👉 **[Read the Beginner's Guide to AI Chatbots](chatbot_guide.md)**

## 🛠 Tech Stack

Just keeping it simple:
- Python 3 (`discord.py`)
- Llama 3 API (via Groq Cloud)

## 📄 License

MIT License — feel free to steal this code and make your own bot! See [LICENSE](LICENSE) for details.
