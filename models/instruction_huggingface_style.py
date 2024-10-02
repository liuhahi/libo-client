"""
This script provides a step-by-step tutorial on how to implement a chat function using the Hugging Face Transformers library.
The function takes a list of chat messages and returns the response from the language model.
"""

import os
from transformers import pipeline, LlamaTokenizer, LlamaForCausalLM

# Step 1: Load the LLaMA model and tokenizer
model_name = "meta-llama/Meta-Llama-3-8B"  # Replace with the actual model name on Hugging Face Hub
tokenizer = LlamaTokenizer.from_pretrained(model_name)
model = LlamaForCausalLM.from_pretrained(model_name)

# Initialize the Hugging Face pipeline with the model and tokenizer
chatbot = pipeline("text-generation", model=model, tokenizer=tokenizer)

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
    
    # Step 2: Prepare the chat history as a single string
    chat_history = []
    for c in chats:
        # Add the user prompt and assistant's answer to the chat history
        chat_history.append({"role": "user", "content": c["prompt"]})
        if "answer" in c.keys():
            chat_history.append({"role": "assistant", "content": c["answer"]})
        else:
            # If there is no answer, it means this is the prompt we need a response for
            break
    
    # Step 3: Generate the model's response
    response = chatbot(chat_history, max_length=1000, num_return_sequences=1)
    
    # Step 4: Extract and return the generated text
    generated_text = response[0]['generated_text']
    assistant_response = generated_text.split("Assistant:")[-1].strip()
    
    return assistant_response