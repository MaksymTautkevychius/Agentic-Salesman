# Agentic Salesman — Product Overview

*A plain-language guide for recruiters and hiring managers. Technical details live in the [README](../README.md).*

---

## The problem

Luxury watch dealers sell through chat. A typical inquiry is a screenshot of a watch and a message like *"how much for this? around 40k"*. Responding well takes skill and speed:

- Customers message at all hours and often in bursts of short messages.
- Each lead needs the same qualifying questions: who are you, which exact watch, what budget, how soon?
- Staff time is spent on casual browsers as much as on serious buyers.
- Slow replies lose sales to the next dealer who answers first.

## The solution

**Agentic Salesman is an AI sales assistant that handles the first conversation with every lead.** It chats on Telegram as a friendly, concise human-sounding salesperson named Adam, gathers the information a human salesperson would need, shows the customer the matching watch from inventory, and keeps track of where each conversation stands.

It never blindly follows a script. Different AI "specialists" handle different jobs, and a coordinator decides who responds.

## A customer's journey

1. **Customer sends a photo** of a watch they like, plus a short message.
2. **The system "looks" at the photo** and works out the brand and model.
3. **Adam replies in a natural tone**, asking one question at a time: name, budget, timing.
4. **When a watch is identified**, the system searches the inventory and replies with the best match **and its picture**.
5. **The conversation is remembered**, so the customer can come back tomorrow and Adam picks up where they left off.
6. **The system tracks readiness to buy**, so a human can step in for the final step with a qualified lead rather than a cold one.

## Why it's more than a chatbot

| Typical chatbot | Agentic Salesman |
|---|---|
| Replies to each message separately | Waits briefly and combines rapid-fire messages into one reply |
| Text only | Understands photos |
| Generic answers | Looks up real inventory and replies with the actual watch image |
| Forgets between sessions | Persistent memory per customer |
| One model does everything | Specialist agents, each using the model best suited to the task |
| Free text in, free text out | Extracts structured data (name, budget, timing, readiness) behind the scenes |

## What this project demonstrates

For someone evaluating the author, this repository is evidence of:

- **Applied AI engineering** – multi-agent orchestration, tool use, structured outputs, multimodal input, and natural-language-to-SQL, using LangGraph and LangChain.
- **Product thinking** – the design starts from a real sales workflow (message bursts, qualification questions, photo-first inquiries), not from a technology demo.
- **Reliability instincts** – deterministic overrides where an LLM shouldn't be trusted alone, caching with expiry and size limits, retry-style syncing of failed database writes, and thread-safe state.
- **Practical judgment** – model choice per task (cost/speed vs reasoning strength), prompts kept private and configurable, secrets in environment variables.
- **Backend fundamentals** – Python, PostgreSQL, event-driven message handling, timers and concurrency.
- **Honest scoping** – a clear roadmap separating what works from what is still being built.

## Skills at a glance

`Python` · `LangGraph` · `LangChain` · `Multi-agent systems` · `Prompt engineering` · `Vision / OCR with LLMs` · `Text-to-SQL` · `PostgreSQL` · `Telegram Bot API` · `Pydantic` · `Concurrency & caching`

## Where it could go next

- Voice-note understanding
- Automatic hand-off summary to a human salesperson once a lead is ready to buy
- Evaluation tooling to measure reply quality and lead-qualification accuracy
- A dashboard for reviewing conversations and leads
- Support for other channels (WhatsApp, Instagram DMs)

## Links

- 💻 Source code: https://github.com/MaksymTautkevychius/Agentic-Salesman
- 📘 Technical README: [../README.md](../README.md)
