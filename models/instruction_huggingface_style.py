"""
This script provides a step-by-step tutorial on how to implement a chat function using the Hugging Face Transformers library.
The function takes a list of chat messages and returns the response from the language model.
"""

import os
from transformers import pipeline, LlamaTokenizer, LlamaForCausalLM

# Step 1: Load the LLaMA model and tokenizer
# model_name = "meta-llama/Llama-3.2-1B"  # Replace with the actual model name on Hugging Face Hub
# Load model directly
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-1B")
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-1B")
# # model = LlamaForCausalLM.from_pretrained(model_name)
# try:
#     tokenizer = LlamaTokenizer.from_pretrained(model_name, use_auth_token=True)
#     model = LlamaForCausalLM.from_pretrained(model_name, use_auth_token=True)
#     print("Tokenizer loaded successfully!")
# except OSError as e:
#     print(f"Error loading tokenizer: {e}")


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
    prompt = ""
    for c in chats:
        prompt += f"Human: {c['prompt']}\n"
        if "answer" in c:
            prompt += f"Assistant: {c['answer']}\n"
    prompt += "Assistant: "

    # Step 3: Generate the model's response
    response = chatbot(prompt, max_length=1000, num_return_sequences=1)
    
    # Step 4: Extract and return the generated text
    generated_text = response[0]['generated_text']
    assistant_response = generated_text.split("Assistant:")[-1].strip()
    
    return assistant_response