# Just Another Code Agent
A digital coding assistant.

## Prerequisites
- universal-ctags (v5.x+) - check the universal ctags is in your path with `ctage --version`, if it's the Xcode version you'll see an error.
- python 3

## Getting Started
1. Get your prerequesits sorted
2. Create a virtual environment (not essential but recommended)
3. `pip install`
4. Copy `.env.example` to `.env` and fill in your keys
Congratulations, you can now use the agent. You just need to put a config file in your project:
5. Copy one of the example from ./configs into your project and rename it config.yaml, tweak it as needed.
6. In the root of this project, execute `python main.py --project ./ "Your request to the coding agent"`
 