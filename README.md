# VirtueRed Quick Start

## Setup

1. Navigate to the client directory:
   ```
   cd client
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Adding a New Model

3. To add a new model:

   a. Create a new Python file:
      - Go to the `client/models` folder
      - Create a new Python file for your custom LLM code
      - Name the file as desired
      - Use `instruction_openai_style.py` as a template

   b. Implement the chat function:
      - Create a function called `chat`
      - This function should:
        - Take a question as input
        - Process it using your custom LLM
        - Return the answer
      - Refer to `instruction_huggingface_style.py` as an example

## Running the Code

4. Run the client and `save the client address`:
   ```
   python client.py
   ```

5. Open and run the `VirtueRed_API_Guide.ipynb` notebook to start the scanning process# libo-client
