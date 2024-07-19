# LLM NVIDIA Guardrails
This is a sample assignment on understanding and using NVIDIA LLM Guardrails

# How to run the project?
1. Activate the virtual environment: `source venv/bin/activate`
2. Run `main.py`: `python main.py`
   - Running main.py install all required dependencies at once
   - Ensure you have gcc and g++ to run C++ code with python bindings
4. For an interactive chat experience, run: `nemoguardrails chat`
5. Make sure to store your `OPENAI_API_KEY` API key in your `.env` file
--- 
# Guardrails 
## Hello Bot:
- Currently runs guardrails as presented in [here](https://github.com/NVIDIA/NeMo-Guardrails/tree/develop/examples/bots/hello_world)
  - Additionally added a flow to disable discussion of 'death'
 

# Colong Concepts
## What is Colang ?
Coland is a modeling language for conversational applications. Use Colang to design how the conversation between a user and a bot should happen. 

## Core Concepts 
Two core concepts:
1. Messages
2. Flows

### Messages
In Colang, a conversation is modeled as an exchange of messages between a user and a bot. An exchnaged message has an `utterance` such as `What can you do?` and a `canonical form` such as `ask about capabilities`. A canonical form is a paraphrase of the utterance to a standard, usually shorter, form. Using Colang, you can define the user messages that are important for your LLM-based applications. 
````colang
define user express greeting
  "Hello"
  "Hi"
  "Wassup?"
````
The `express greeting` represents the canonical form and "Hello", "Hi", "Wassup?" represent example utterances. The role of an example utterance is to teach the bot the meaning of a defined canonical form. 
- If more than one utterance is given for a canoncial form, the bot uses a randum utterance whenever the message is used. 
- You can think of __user message canonical form__ as classical intents. However, when using intent, the bot is not constrained to use only the pre-defined list. 

### Flows
A flow is a sequence of messages that the bot can use to respond to a user message. In their simplest form, they are sequences of user and bot messages. 
For example:
````colang
define flow greeting
  user express greeting
  bot express greeting
  bot ask how are you
````
This flow instructs the bot to respond with a greeting and ask how the user is feeling every time the user greets the bot. 

### Guardrails
Messages and flows provide the core building blocks for defining guardrails, or rails for short. 
The previous `greeting` flow is in fact a rail that guides the LLM how to respond to a greeting.

#### How does it work ?
- How are the user and bot message definitions used ?
- How is the LLM prompted and how many calls are made ?
- Can I use bot messages without example utterances ?

##### The `ExplainInfo` Class
To get information about the LLM calls, call the **explain** function of the `LLMRails` class.
````python
info = rails.explain()
````
##### Colang History
Use the `colang_history` function to retrieve the history of the conversation in Colang format. This shows us the exact messages and their canonical forms:
````python
print(info.colang_history)
user "Hello!"
  express greeting
bot express greeting
  "Hello World!"
bot ask how are you
  "How are you doing?"
````

##### LLM Calls
Use the `print_llm_calls_summary` function to list a summary of the LLM calls that have been made:
````python
info.print_llm_calls_summary()

Summary: 1 LLM call(s) took 0.48 seconds and used 524 tokens.

1. Task `generate_user_intent` took 0.48 seconds and used 524 tokens.
````

#### The Process
Once an input message is received from the user, a multi-step process begins. 

1. Compute the canonical form of the user message
After an utterance, such as "Hello" in the previous example, is received from the user, the guardrails instance uses the LLM to compute the corresponding canonical form. 
- In the case of the "Hello" message, a single LLM call is made using the `generate_user_intent` task prompt template. 
- Note: NeMo Guardrails uses a task-oriented interaction model with the LLM. Every time the LLM is called, it uses a specific task prompt template such as `generate_user_input`, `generate_next_step`, `generate_bot_message`.
- In the case of the "Hello!" message, a single LLM call is made using the generate_user_intent task prompt template. 
````python
print(info.llm_calls[0].prompt)
"""
Below is a conversation between a helpful AI assistant and a user. The bot is designed to generate human-like text based on the input that it receives. The bot is talkative and provides lots of specific details. If the bot does not know the answer to a question, it truthfully says it does not know.
"""

# This is how a conversation between a user and the bot can go (Conversation Example):
user "Hello there!"
  express greeting
bot express greeting
  "Hello! How can I assist you today?"
user "What can you do for me?"
  ask about capabilities
bot respond about capabilities
  "As an AI assistant, I can help you with a wide range of tasks. This includes question answering on various topics, generating text for various purposes and providing suggestions based on your preferences."
user "Tell me a bit about the history of NVIDIA."
  ask general question
bot response for general question
  "NVIDIA is a technology company that specializes in designing and manufacturing graphics processing units (GPUs) and other computer hardware. The company was founded in 1993 by Jen-Hsun Huang, Chris Malachowsky, and Curtis Priem."
user "tell me more"
  request more information
bot provide more information
  "Initially, the company focused on developing 3D graphics processing technology for the PC gaming market. In 1999, NVIDIA released the GeForce 256, the world's first GPU, which was a major breakthrough for the gaming industry. The company continued to innovate in the GPU space, releasing new products and expanding into other markets such as professional graphics, mobile devices, and artificial intelligence."
user "thanks"
  express appreciation
bot express appreciation and offer additional help
  "You're welcome. If you have any more questions or if there's anything else I can help you with, please don't hesitate to ask."

# This is how the user talks:
user "Wassup?"
  express greeting

user "Hi"
  express greeting

user "Hello"
  express greeting

# This is the current conversation between the user and the bot (Current conversation context):
# Choose intent from this list: express greeting
user "Hello there!"
  express greeting
bot express greeting
  "Hello! How can I assist you today?"
user "What can you do for me?"
  ask about capabilities
bot respond about capabilities
  "As an AI assistant, I can help you with a wide range of tasks. This includes question answering on various topics, generating text for various purposes and providing suggestions based on your preferences."
user "Hello!"

"""
Summary
- Identifying the intent behind the user's message
- Responding appropriately based on that intent
"""
````


The prompt has four logical sections:
a. A set of general instructions - guide the LLM's overall behaviour
b. A sample conversation - provide a template for typical interactions
c. A set of examples for converting user utterances to canonical forms - show how to translate user utterances into standard form
d. The current conversation preceded by the first two turns from the sample conversation - provide relevant conversation history to maintain coherence. 

2. Determine the next step
- After the canonical form for the user message has been computed, the guardrails instance needs to decide what should happen next. These are two cases:
    - a. If **there is a flow** that matches the canonical form, then it is used. The flow can decide that the bot should respond with a certain message or execute an action.
    - b. If **there is no flow**, the LLM is prompted for the next step using the `generate_next_step` task
- In our example, there was a match from the `greeting` flow and the next steps are:
````colang
bot express greeting
bot ask how are you
````
3. Generate the bot message
Once the canonical form for what the bot should say has been decided, the message must be generated. There are two cases:
- a. If a **predefined message is found**, the exact utterance is used. If more than one example utterances are associated with the same canonical form, a random one is used.
- b. If a **predefined message does not exist**, the LLM is prompted to generate the message using the `generate_bot_message` task. 
In our "Hello World" example, the predefined messages "Hello World" and "How are you doing?" are used. 

Summary of the outlined sequence of steps:
1. Pre-defined Flow Exists
   - User input message
   - Determine canonical form: LLM computes the canonical form `express greeting` using `generate_user_intent` prompt
   - Determine next step: A flow is found that matches the canonical form `express greeting`
   - Generate the bot message: Uses the predefined messages from the flow
  ![Screenshot 2024-07-18 at 9 43 01 PM](https://github.com/user-attachments/assets/a71e579b-014f-4953-be9e-171c61862c8a)

2. Pre-defined Flow Does Not Exist
   - User input message
   - Determine canonical form: LLM computes the canonical form `Ask general question` by calling `generate_user_input`
   - Determine next steps: Flow for canonical message is not found. LLM is prompted to compute the bot's canonical form via `generate_next_step`
   - Generate bot message: Predefined message or flow is not found for the bot's canonical form, so LLM is prompted to compute the bot's message via `generate_bot_message`.
![Screenshot 2024-07-18 at 9 43 18 PM](https://github.com/user-attachments/assets/f3e2e10d-7779-49c3-b69b-c5f3337d1fd4)
![Screenshot 2024-07-18 at 9 43 30 PM](https://github.com/user-attachments/assets/6b560a7c-83e1-4a8c-8471-1cab52acb3c0)
