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
# Guardrails Process

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

---
# ABC Bot Demo Use Case
This overview describes a use case for a fictional company, ABC Company, with a bot, ABC bot, that assists employees by providing information on the organization's employee handbook and policies. 
1. Input Moderation: Verify that any user input is safe before proceeding.
2. Output Moderation: Ensures that the bot's output is not offensive and does not include specific words
3. Preventing off-topic questions: Guarantee that the bot only responds to specific topics
4. Retrival Augmented Generation: Integrate external knowledge bases

## Configuration Guide 
1. General Options: which LLM(s) to use, general instructions (similar to system prompts), sample conversation, which rails are active, specific rails configuration options, etc.; these options are typically placed in a `config.yml` file.
2. Rails: Colang flows implementing the rails; these are typically placed in a `rails` folder.
3. Actions: custom actions implemented in Python; these are typically placed in an `actions.py` module in the root of the config or in an `actions` sub-package.
4. Knowledge Base Documents: documents that can be used in a RAG (Retrieval-Augmented Generation) scenario using the built-in Knowledge Base support; these documents are typically placed in a kb folder.
5. Initialization Code: custom Python code performing additional initialization, e.g. registering a new type of LLM.

### General Instructions
The general instruction (similar to a system prompt) get appended at the beginning of every prompt, and you can configure them as show below:
```
instructions:
  - type: general
    content: |
      Below is a conversation between the NeMo Guardrails bot and a user.
      The bot is talkative and provides lots of specific details from its context.
      If the bot does not know the answer to a question, it truthfully says it does not know.
```

### Sample Conversation
The sample conversation sets the tone for how the conversation between the user and the bot should go. It will help the LLM learn better the format, the tone of the conversation, and how verbose responses should be. This section should have a minimum of two turns. Since we append this sample conversation to every prompt, it is recommended to keep it short and relevant.
```
sample_conversation: |
  user "Hello there!"
    express greeting
  bot express greeting
    "Hello! How can I assist you today?"
  user "What can you do for me?"
    ask about capabilities
  bot respond about capabilities
    "As an AI assistant, I can help provide more information on NeMo Guardrails toolkit. This includes question answering on how to set it up, use it, and customize it for your application."
  user "Tell me a bit about the what the toolkit can do?"
    ask general question
  bot response for general question
    "NeMo Guardrails provides a range of options for quickly and easily adding programmable guardrails to LLM-based conversational systems. The toolkit includes examples on how you can create custom guardrails and compose them together."
  user "what kind of rails can I include?"
    request more information
  bot provide more information
    "You can include guardrails for detecting and preventing offensive language, helping the bot stay on topic, do fact checking, perform output moderation. Basically, if you want to control the output of the bot, you can do it with guardrails."
  user "thanks"
    express appreciation
  bot express appreciation and offer additional help
    "You're welcome. If you have any more questions or if there's anything else I can help you with, please don't hesitate to ask."
```

### LLM Prompts
You can customize the prompts that are used for the various LLM tasks (eg. generate_user_intent, generate_next_step, generate_bot_message) using the `prompt` key. 
For example, to override the prompt used for the generate_user_intent task for the openai/gpt-3.5-turbo model:
```
prompts:
  - task: generate_user_intent
    models:
      - openai/gpt-3.5-turbo
    max_length: 3000
    content: |-
      <<This is a placeholder for a custom prompt for generating the user intent>>
```

- For each task, you can also specify the maximum length of the prompt to be used for the LLM call in terms of the number of characters. This is useful if you want to limit the number of tokens used by the LLM or when you want to make sure that the prompt length does not exceed the maximum context length. When the maximum length is exceeded, the prompt is truncated by removing older turns from the conversation history until the length of the prompt is less than or equal to the maximum length. The default maximum length is 16000 characters.

The full list of tasks used by the NeMo Guardrails toolkit is the following:
1. `general`: generate the next bot message, when no canonical forms are used;
2. `generate_user_intent`: generate the canonical user message;
3. `generate_next_steps`: generate the next thing the bot should do/say;
4. `generate_bot_message`: generate the next bot message;
5. `generate_value`: generate the value for a context variable (a.k.a. extract user-provided values)
6. `self_check_facts`: check the facts from the bot response against the provided evidence;
7. `self_check_input`: check if the input from the user should be allowed;
8. `self_check_output`: check if bot response should be allowed;
9. `self_check_hallucination`: check if the bot response is a hallucination.

## Guardrail Definitions
Guardrails (or rails for short) are implemented through flows. Depending on their role, rails can be split into several main categories:
1. Input rails: triggered when a new input from the user is received
2. Output rails: triggered when a new output should be sent to the user
3. Dialog rails: triggered after a user message is interpreted, i.e, a canonical form has been identified
4. Retrival rails: triggered aftter the retrival step has been performed (ie. the `retrieve_relevant_chunks` action has finished)
5. Execution rails: triggered before and after an action is invoked

The active rails are configured using the `rails` key in `config.yml`. Below is a quick example:
```python
rails:
  # Input rails are invoked when a new message from the user is received.
  input:
    flows:
      - check jailbreak
      - check input sensitive data
      - check toxicity
      - ... # Other input rails

  # Output rails are triggered after a bot message has been generated.
  output:
    flows:
      - self check facts
      - self check hallucination
      - check output sensitive data
      - ... # Other output rails

  # Retrieval rails are invoked once `$relevant_chunks` are computed.
  retrieval:
    flows:
      - check retrieval sensitive data
```

All the flows that are not input, output, or retrieval flows are considered dialog rails and execution rails, i.e., flows that dictate how the dialog should go and when and how to invoke actions. Dialog/execution rail flows don’t need to be enumerated explicitly in the config. However, there are a few other configuration options that can be used to control their behavior.

```python
rails:
  # Dialog rails are triggered after user message is interpreted, i.e., its canonical form
  # has been computed.
  dialog:
    # Whether to try to use a single LLM call for generating the user intent, next step and bot message.
    single_call:
      enabled: False

      # If a single call fails, whether to fall back to multiple LLM calls.
      fallback_to_multiple_calls: True

    user_messages:
      # Whether to use only the embeddings when interpreting the user's message
      embeddings_only: False
```

### Input Rails
Input rails process the message from the user. For example:
```python
define flow self check input
  $allowed = execute self_check_input

  if not $allowed
    bot refuse to respond
    stop
```
Input rails can alter the input by changing the `$user_message` context variable.

