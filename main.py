from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

from spell_correction import get_corrections  # Use your correct import path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend URL if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SentenceRequest(BaseModel):
    sentence: str  # full sentence typed so far

class FileRequest(BaseModel):
    text: str

@app.post("/correct")
async def correct_word(data: SentenceRequest):
    sentence = data.sentence.strip()
    words = sentence.split()
    
    if not words:
        return {"word": "", "suggestions": []}

    current_word = words[-1]
    prev_word = words[-2] if len(words) >= 2 else ""
    prev_prev_word = words[-3] if len(words) >= 3 else ""

    top5 = get_corrections(current_word, sentence, prev_word, prev_prev_word)

    return {"word": current_word, "suggestions": top5}


@app.post("/file-correct")
def file_correct(req: FileRequest):
    sentences = req.text.strip().split("\n")
    corrected_sentences = []
    
    for line in sentences:
        words = line.strip().split()
        corrected_words = []
        for idx, word in enumerate(words):
            prev = words[idx - 1] if idx >= 1 else ""
            prev2 = words[idx - 2] if idx >= 2 else ""
            
            suggestions = get_corrections(word, line, prev, prev2)
            # Use first suggestion if available, else original
            
            if(len(suggestions)>1 and suggestions[0]!=word):
                corrected_words.append(suggestions[0]+'*')
            else:
                corrected_words.append(word)

        corrected_sentences.append(" ".join(corrected_words))
    corrected_text = "\n".join(corrected_sentences)
    return {"corrected_text": corrected_text}

