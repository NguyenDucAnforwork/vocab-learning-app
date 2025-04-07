from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

app = FastAPI()

class UserMetadata(BaseModel):
    name: str
    age: Optional[int]
    occupation: Optional[str]
    hobbies: Optional[List[str]] = []
    favorite_books: Optional[List[str]] = []
    favorite_quotes: Optional[List[str]] = []
    learning_goals: Optional[List[str]] = []
    interests: Optional[List[str]] = []

class StoryRequest(BaseModel):
    user_metadata: UserMetadata
    english_level: str = "intermediate"

SAMPLE_CONVERSATION = [
    ("user", "What did you do last weekend?"),
    ("assistant", "I spent time reading and going for walks. How about you?"),
    ("user", "I went to a local coffee shop and tried some new desserts."),
    ("assistant", "That sounds lovely! What kind of desserts did you try?")
]

@app.post("/generate-story")
async def generate_story(request: StoryRequest):
    try:
        # Convert metadata to string format
        metadata_str = "\n".join([
            f"{key}: {value}" 
            for key, value in request.user_metadata.dict().items()
            if value  # Only include non-empty values
        ])
        
        # Create conversation context from sample conversation
        chat_context = "\n".join([f"{role}: {msg}" for role, msg in SAMPLE_CONVERSATION])
        
        story_prompt = f"""
        Based on the following chat conversation, create an engaging story in English (150-250 words).
        The story should naturally flow from the conversation topics.
        
        Chat context:
        {chat_context}
        
        Additional context about the reader:
        {metadata_str}
        
        Guidelines:
        - Focus primarily on the main themes from the conversation
        - Only incorporate personal details when they naturally fit the story's context
        - Use {request.english_level}-level English vocabulary
        - The story should feel natural and uncontrived
        - Don't force all personal details if they don't fit naturally
        """
        
        story_response = model.generate_content(story_prompt)
        
        return {
            "status": "success",
            "story": story_response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 