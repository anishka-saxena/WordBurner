import os
import redis
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from roast import get_roast, get_surprise_roast, get_simple_phonetic

app = FastAPI()

redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, decode_responses=True)


def extract_word_from_result(result: str):
    for line in result.splitlines():
        if "📌 Word:" in line:
            return line.split("📌 Word:")[-1].strip().strip("*").strip()
    return None


@app.get("/roast/{word}")
def roast_word(word: str):
    result = get_roast(word)
    return PlainTextResponse(result)


@app.get("/phonetic/{word}")
def phonetic_word(word: str):
    result = get_simple_phonetic(word)
    return PlainTextResponse(result or "")


@app.post("/surprise/{level}")
def surprise_word(level: str):
    used_words = list(redis_client.smembers(f"used_words:{level.lower()}"))
    result = get_surprise_roast(level, used_words)
    extracted = extract_word_from_result(result)
    if extracted:
        redis_client.sadd(f"used_words:{level.lower()}", extracted.lower())
    return PlainTextResponse(result)
