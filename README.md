# LLM NVIDIA Guardrails
This is a sample assignment on understanding and using NVIDIA LLM Guardrails

# How to run the project?
1. Activate the virtual environment: `source venv/bin/activate`
2. Run `main.py`: `python main.py`
   - Running main.py install all required dependencies at once
   - Ensure you have gcc and g++ to run C++ code with python bindings
4. For an interactive chat experience, run: `nemoguardrails chat`
5. Make sure to store your `OPENAI_API_KEY` API key in your `.env` file

# Guardrails 
## Hello Bot:
- Currently runs guardrails as presented in [here](https://github.com/NVIDIA/NeMo-Guardrails/tree/develop/examples/bots/hello_world)
  - Additionally added a flow to disable discussion of 'death'
 
   
