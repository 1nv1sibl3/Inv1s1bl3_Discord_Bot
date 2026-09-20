import asyncio
import logging
import random
from typing import Any, Dict, Optional
import aiohttp

from src.config.settings import settings

logger = logging.getLogger("inv1s1bl3.api")

_session: Optional[aiohttp.ClientSession] = None


def get_http_session() -> aiohttp.ClientSession:
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
    return _session


async def close_http_session() -> None:
    global _session
    if _session is not None and not _session.closed:
        await _session.close()
        _session = None


async def get_fact() -> Optional[str]:
    session = get_http_session()
    try:
        async with session.get("https://uselessfacts.jsph.pl/random.json?language=en") as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("text")
    except Exception as e:
        logger.warning(f"Fact API request failed: {e}")
    return "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still edible!"


async def get_yesno() -> Optional[Dict[str, str]]:
    session = get_http_session()
    try:
        async with session.get("https://yesno.wtf/api") as resp:
            if resp.status == 200:
                return await resp.json()
    except Exception as e:
        logger.warning(f"YesNo API request failed: {e}")
    answer = random.choice(["yes", "no"])
    return {"answer": answer, "image": "https://media.giphy.com/media/26hkhHMHwnnUqL8TC/giphy.gif"}


async def get_wikipedia_summary(query: str) -> Optional[Dict[str, Any]]:
    session = get_http_session()
    try:
        async with session.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}") as resp:
            if resp.status == 200:
                return await resp.json()
    except Exception as e:
        logger.warning(f"Wikipedia API request failed: {e}")
    return None


async def get_nasa_apod(date: Optional[str] = None) -> Optional[Dict[str, Any]]:
    session = get_http_session()
    key = settings.nasa_api_key or "DEMO_KEY"
    url = f"https://api.nasa.gov/planetary/apod?api_key={key}"
    if date:
        url += f"&date={date}"
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
    except Exception as e:
        logger.warning(f"NASA APOD API request failed: {e}")
    return None


async def get_pokedex(pokemon: str) -> Optional[Dict[str, Any]]:
    session = get_http_session()
    try:
        async with session.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon.lower().strip()}") as resp:
            if resp.status == 200:
                return await resp.json()
    except Exception as e:
        logger.warning(f"PokeAPI request failed: {e}")
    return None


async def get_joke() -> Dict[str, str]:
    session = get_http_session()
    try:
        async with session.get("https://official-joke-api.appspot.com/random_joke") as resp:
            if resp.status == 200:
                data = await resp.json()
                return {"setup": data.get("setup", ""), "punchline": data.get("punchline", "")}
    except Exception as e:
        logger.warning(f"Joke API request failed: {e}")
    return {
        "setup": "Why do programmers prefer dark mode?",
        "punchline": "Because light attracts bugs!",
    }


async def get_truth_or_dare(kind: str = "truth") -> str:
    session = get_http_session()
    url = f"https://api.truthordarebot.xyz/v1/{kind}"
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("question", "")
    except Exception as e:
        logger.warning(f"TruthOrDare API request failed: {e}")

    fallbacks = {
        "truth": "What is the funniest thing that has ever happened to you in Discord?",
        "dare": "Speak only in OwO speak for the next 10 minutes!",
    }
    return fallbacks.get(kind, "Tell the chat your favorite video game.")


async def get_giphy_gif(query: str) -> Optional[str]:
    session = get_http_session()
    key = settings.giphy_api_key
    if not key:
        return None
    url = f"https://api.giphy.com/v1/gifs/translate?api_key={key}&s={query}"
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("data", {}).get("images", {}).get("original", {}).get("url")
    except Exception as e:
        logger.warning(f"GIPHY API request failed: {e}")
    return None


async def get_bored_activity() -> Dict[str, str]:
    session = get_http_session()
    try:
        async with session.get("https://bored-api.appbrewery.com/random") as resp:
            if resp.status == 200:
                data = await resp.json()
                return {
                    "activity": data.get("activity", "Learn a new Python module!"),
                    "type": data.get("type", "education"),
                    "participants": str(data.get("participants", 1)),
                    "price": str(data.get("price", "Free")),
                }
    except Exception as e:
        logger.warning(f"Bored API request failed: {e}")

    activities = [
        ("Learn a new Python framework", "education", "1", "Free"),
        ("Organize your Discord server roles", "productive", "1", "Free"),
        ("Play a game of Guess A Word with friends", "social", "2-4", "Free"),
        ("Write an open-source contribution", "diy", "1", "Free"),
    ]
    act = random.choice(activities)
    return {
        "activity": act[0],
        "type": act[1],
        "participants": act[2],
        "price": act[3],
    }


async def get_ai_chat_response(prompt: str, user_name: str) -> str:
    """Generate an AI chat response using configured OpenAI key or legacy fallback."""
    if settings.openai_api_key:
        try:
            headers = {
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are Inv1s1bl3 Bot, a helpful, enthusiastic, and slightly playful Discord bot originally created 4 years ago as a student learning project. Keep responses concise, friendly, and under 250 words.",
                    },
                    {"role": "user", "content": f"{user_name}: {prompt}"},
                ],
                "max_tokens": 150,
            }
            session = get_http_session()
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.warning(f"OpenAI chat completion failed: {e}")

    # Charming built-in conversational fallbacks
    canned_replies = [
        f"Hey {user_name}! I'm Inv1s1bl3 Bot, revived and modernized! How's your server doing today?",
        f"Beep boop! That's an interesting question, {user_name}. Did you check out the economy or business cogs?",
        f"I hear you loud and clear, {user_name}! Remember to use `i.help` to explore all my features.",
        f"Greetings {user_name}! I'm operating at peak performance on modern discord.py!",
    ]
    return random.choice(canned_replies)
