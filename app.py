import gradio as gr
import google.generativeai as genai
from typing import List, Tuple
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

class VocabLearningBot:
    def __init__(self):
        self.chat_history: List[Tuple[str, str]] = []
        self.target_words = []
        self.user_level = "intermediate"  # Default level
        self.chat = model.start_chat(history=[])
        self.user_metadata = {
            "name": "",
            "age": "",
            "occupation": "",
            "hobbies": [],
            "favorite_books": [],
            "favorite_quotes": [],
            "learning_goals": [],
            "interests": [],
            "preferred_topics": [],
            "travel_experiences": []
        }
        
    def detect_language(self, text: str) -> str:
        # Simple detection - can be improved
        vietnamese_chars = set('àáãạảăắằẳẵặâấầẩẫậèéẹẻẽêềếểễệđìíĩỉịòóõọỏôốồổỗộơớờởỡợùúũụủưứừửữựỳýỵỷỹ')
        if any(char.lower() in vietnamese_chars for char in text):
            return 'vi'
        return 'en'

    def generate_response(self, user_input: str) -> str:
        language = self.detect_language(user_input)
        
        # Store chat history
        self.chat_history.append(("user", user_input))
        
        # Generate chatbot response using Gemini
        prompt = f"""
        You are a friendly English teacher chatbot. Respond naturally to the user's message.
        If the user writes in Vietnamese, you can respond in Vietnamese, but include some English vocabulary 
        that would be useful for them to learn in the context.
        
        User level: {self.user_level}
        Current message: {user_input}
        Language detected: {language}
        """
        
        response = self.chat.send_message(prompt).text
        self.chat_history.append(("assistant", response))
        
        return response
    
    def update_user_metadata(self, metadata_dict: dict) -> None:
        """Update user metadata with new information"""
        self.user_metadata.update(metadata_dict)
        
    def generate_story(self) -> str:
        chat_context = "\n".join([f"{role}: {msg}" for role, msg in self.chat_history])
        metadata_context = "\n".join([
            f"{key}: {value}" for key, value in self.user_metadata.items()
            if value  # Only include non-empty values
        ])
        
        story_prompt = f"""
        Based on the following chat conversation, create an engaging story in English (150-250 words).
        The story should naturally flow from the conversation topics.
        
        Chat context:
        {chat_context}
        
        Additional context about the reader:
        {metadata_context}
        
        Guidelines:
        - Focus primarily on the main themes from the conversation
        - Only incorporate personal details when they naturally fit the story's context
        - Use {self.user_level}-level English vocabulary
        - The story should feel natural and uncontrived
        - Don't force all personal details if they don't fit naturally
        """
        
        story_response = model.generate_content(story_prompt)
        return story_response.text

def create_interface():
    bot = VocabLearningBot()
    
    with gr.Blocks() as interface:
        with gr.Row():
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(label="Chat with English Teacher")
                msg = gr.Textbox(label="Type your message")
                send = gr.Button("Send")
                generate = gr.Button("Generate Story")
                story_output = gr.Textbox(label="Generated Story", lines=10)
            
            # Add user metadata input column
            with gr.Column(scale=1):
                gr.Markdown("### Personal Information")
                name = gr.Textbox(label="Name")
                age = gr.Number(label="Age")
                occupation = gr.Textbox(label="Occupation")
                hobbies = gr.Textbox(label="Hobbies (comma-separated)")
                favorite_books = gr.Textbox(label="Favorite Books (comma-separated)")
                favorite_quotes = gr.Textbox(label="Favorite Quotes (comma-separated)")
                learning_goals = gr.Textbox(label="Learning Goals (comma-separated)")
                interests = gr.Textbox(label="Interests (comma-separated)")
                update_info = gr.Button("Update Personal Information")
        
        def update_metadata(name, age, occupation, hobbies, books, quotes, goals, interests):
            metadata = {
                "name": name,
                "age": age,
                "occupation": occupation,
                "hobbies": [x.strip() for x in hobbies.split(",") if x.strip()],
                "favorite_books": [x.strip() for x in books.split(",") if x.strip()],
                "favorite_quotes": [x.strip() for x in quotes.split(",") if x.strip()],
                "learning_goals": [x.strip() for x in goals.split(",") if x.strip()],
                "interests": [x.strip() for x in interests.split(",") if x.strip()]
            }
            bot.update_user_metadata(metadata)
            return "Personal information updated successfully!"
        
        def respond(message, history):
            bot_response = bot.generate_response(message)
            history.append((message, bot_response))
            return "", history
        
        def create_story():
            return bot.generate_story()
        
        send.click(respond, [msg, chatbot], [msg, chatbot])
        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        generate.click(create_story, [], story_output)
        update_info.click(
            update_metadata,
            inputs=[name, age, occupation, hobbies, favorite_books, 
                   favorite_quotes, learning_goals, interests],
            outputs=gr.Textbox(label="Status")
        )
    
    return interface

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(share=True) 