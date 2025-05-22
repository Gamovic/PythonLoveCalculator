from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="RESTful API - Lova Calculator",
    description="An API to calculate love compatibility between two names",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins in development - ONLY FOR DEVELOPMENT
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Access environment variables
DEBUG = os.getenv("DEBUG", "False") == "True" # Convert DEBUG value to a boolean
API_KEY = os.getenv("API_KEY")

class Match(BaseModel):
    person1: str
    person2: str
    score: int  

# Eksempeldata
matches = [
    {"id": 1, "person1": "Emma", "person2": "Liam", "score": 86},
    {"id": 2, "person1": "Sophia", "person2": "Noah", "score": 92}
]

# GET love calculation/match mellem to navne, og tjek om dette match findes
@app.get("/lovecalc")
def beregn_kaerlighed(person1: str, person2: str):
    samlet_navn = (person1 + person2).lower()
    score = sum(ord(bogstav) for bogstav in samlet_navn) % 101

    # Tjek om match allerede findes (samme to personer)
    for match in matches:
        if {match["person1"].lower(), match["person2"].lower()} == {person1.lower(), person2.lower()}:
            return {
                "besked": "Match eksisterer allerede",
                "match": match
            }

    # Generer ny id
    nyt_id = max((match["id"] for match in matches), default=0) + 1
    nyt_match = {"id": nyt_id, "person1": person1, "person2": person2, "score": score}
    matches.append(nyt_match)

    return {
        "besked": f"Kærlighedsscore gemt: {score}%",
        "match": nyt_match
    }

# GET alle matches
@app.get("/matches")
def hent_matches():
    return matches

# POST nyt match, og tjek om match allerede findes
@app.post("/matches")
def tilføj_match(match: Match):
    # Tjek om match allerede findes (uanset rækkefølge og store/små bogstaver)
    for eksisterende in matches:
        sæt1 = {eksisterende["person1"].lower(), eksisterende["person2"].lower()}
        sæt2 = {match.person1.lower(), match.person2.lower()}
        if sæt1 == sæt2:
            return {
                "fejl": "Match mellem disse personer eksisterer allerede",
                "eksisterende_match": eksisterende
            }

    # Hvis det ikke findes, tilføj match
    matches.append(match)
    return {
        "besked": "Match tilføjet",
        "match": match
    }

@app.put("/matches/{id}")
def opdater_match(id: int, data: Match):
    for match in matches:
        if match["id"] == id:
            match.update(data)
            return {"besked": "Match opdateret", "match": match}
    return {"fejl": "Match ikke fundet"}

@app.delete("/matches/{id}")
def slet_match(id: int):
    for match in matches:
        if match["id"] == id:
            matches.remove(match)
            return {"besked": "Match slettet"}
    return {"fejl": "Match ikke fundet"}