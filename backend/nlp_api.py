from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class TextRequest(BaseModel):
    text: str

@app.post("/predict")
def predict(req: TextRequest):
    text = req.text.lower()

    positive_words = [
        "love", "like", "liked", "good", "great","best",
        "awesome", "amazing", "excellent", "happy", "nice",
        "Fantastic", "Wonderful", "Brilliant", "Beautiful", 
        "strong", "powerful", "Successful", "proud", "trust",
        "excitement", "Enjoy", "Inspired", "positive"
        
    ]

    negative_words = [
        "hate", "not like", "bad", "worst",
        "terrible", "awful", "sad", "angry", "dislike",
        "Worst", "Negative", "Failure", "Weak", "Fear", "Pain", 
        "stress", "Depressed", "lonely", "frustrated",
        "Disappointed", "Tired","Broken", "not good", "not"
    ]

    pos_count = sum(word in text for word in positive_words)
    neg_count = sum(word in text for word in negative_words)

    if pos_count > neg_count and pos_count > 0:
        label = "POSITIVE"
        confidence = min(0.6 + pos_count * 0.1, 0.95)
        

    elif neg_count > pos_count and neg_count > 0:
        label = "NEGATIVE"
        confidence = min(0.6 + neg_count * 0.1, 0.95)
        

    else:
        label = "NEUTRAL"
        confidence = 0.5
        

    return {
        "text": req.text,
        "label": label,
    
        "confidence": round(confidence, 2)
    }

if __name__ == "__main__":
    uvicorn.run("nlp_api:app", host="127.0.0.1", port=8000, reload=True)
