import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('/home/asus/HDD/Tauking Researcher/voice_eda_system/.env')

# Initialize Groq client with API key from environment
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Make a simple chat completion request
try:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # You can change this to your preferred model
        messages=[
            {"role": "user", "content": "hi"}
        ],
        temperature=0.7,
        max_tokens=100
    )
    
    # Print the response
    print("Response from Groq API:")
    print(response.choices[0].message.content)
    
except Exception as e:
    print(f"Error calling Groq API: {e}")
