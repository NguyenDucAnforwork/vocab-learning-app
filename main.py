import gradio as gr
from app import VocabLearningBot, create_interface
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

# FastAPI app
app = FastAPI()

# Gradio interface with auto_reload
demo = create_interface()
demo.queue()  # Enable queuing for better handling of multiple requests

# Launch Gradio with auto_reload
if __name__ == "__main__":
    demo.launch(reload=True, show_error=True) 