"""
This script provides a step-by-step tutorial on how to implement a chat function using the OpenAI sytle API.
The function takes a list of chat messages and returns the response from the language model.
"""

import os
import openai

# Step 1: Set your OpenAI API key
# Replace 'YOUR_API_KEY_HERE' with your actual API key
os.environ['OPENAI_API_KEY'] = 'YOUR_API_KEY_HERE'

# Initialize the OpenAI client with the API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Don't change the name of the function or the function signature
def chat(chats):
    """
    This function takes a list of chat messages and returns the response from the language model.
    
    Parameters:
    chats (list): A list of dictionaries. Each dictionary contains a "prompt" and optionally an "answer".
                  The last item in the list should have a "prompt" without an "answer".
    
    Returns:
    str: The response from the language model.
    
    Example of `chats` list with few-shot prompts:
    [
        {"prompt": "Hello, how are you?", "answer": "I'm an AI, so I don't have feelings, but thanks for asking!"},
        {"prompt": "What is the capital of France?", "answer": "The capital of France is Paris."},
        {"prompt": "Can you tell me a joke?"}
    ]
    
    Another example of `chats` list with one-shot prompt:
    [
        {"prompt": "What is the weather like today?"}
    ]
    """
    
    # Step 2: Prepare the messages list for the API request
    messages = []
    for c in chats:
        # Add the user prompt to the messages list
        messages.append({"role": "user", "content": c["prompt"]})
        if "answer" in c:
            # If there is an assistant's answer, add it to the messages list
            messages.append({"role": "assistant", "content": c["answer"]})
        else:
            # If there is no answer, it means this is the prompt we need a response for
            break
    
    # Step 3: Make the API request to get the model's response
    response = openai.ChatCompletion.create(
        model="gpt-4-0613",  # Specify the model you want to use
        messages=messages,   # Pass the messages list to the API
        temperature=0,       # Set the temperature for response generation
    )
    
    # Step 4: Return the model's response
    return response['choices'][0]['message']['content']
