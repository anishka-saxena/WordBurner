from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from roast import get_roast

app = FastAPI()

@app.get("/roast/{word}")
def roast_word(word: str):
    result = get_roast(word)
    return PlainTextResponse(result)