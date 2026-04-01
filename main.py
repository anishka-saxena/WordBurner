from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from roast import get_roast, get_surprise_roast, get_simple_phonetic

app = FastAPI()


class SurpriseRequest(BaseModel):
    used_words: list[str] = []


@app.get("/roast/{word}")
def roast_word(word: str):
    result = get_roast(word)
    return PlainTextResponse(result)


@app.get("/phonetic/{word}")
def phonetic_word(word: str):
    result = get_simple_phonetic(word)
    return PlainTextResponse(result or "")


@app.post("/surprise/{level}")
def surprise_word(level: str, body: SurpriseRequest):
    result = get_surprise_roast(level, body.used_words)
    return PlainTextResponse(result)