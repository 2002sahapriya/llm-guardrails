import subprocess
import sys
from dotenv import load_dotenv, find_dotenv
from nemoguardrails import RailsConfig, LLMRails

# install dependencies 
def install_dependencies():
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

# load environment variables
def load_variables():
    load_dotenv(find_dotenv())

# load and use guardrails configuration
def guardrails():
    config = RailsConfig.from_path("./config")
    rails = LLMRails(config)
    
    # create a message
    message = {'role': 'user', 'content': 'Hi!'}

    # generate a response
    response = rails.generate(messages=[message])
    print(response['content'])


def main():
    # install_dependencies()
    load_variables()
    guardrails()

if __name__ == "__main__":
    # run the main
    main()

    # Rest of your main code
