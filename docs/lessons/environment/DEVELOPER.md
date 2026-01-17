## How to run this application locally for development

### 0. Install environment tools
The application was developed using python version 3.10.13, which is a stable version.

1. install pyenv
for Linux:
```bash
curl -fsSL https://pyenv.run | bash
```

for macOS:
```bash
brew update
brew install pyenv
```

### 1. ensure pyenv is properly configured
To make pyenv work smoothly, you need to integrate it with your shell. Follow these steps:

#### a. add pyenv to your shell configuration
1. open your `~/.zshrc` file:
```bash
nano ~/.zshrc
```
2. add the following lines at the end of the file:
```bash
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - zsh)"
```
3. save and exit the file.

#### b. restart your shell
Reload your shell with the following command:
```bash
exec "$SHELL"
```

#### c. verify installation
Check if pyenv is working:
```bash
pyenv versions
```

### 2. set python version
We will use a virtual environment with python 3.10.13.

#### a. install python 3.10.13
If python 3.10.13 is not installed, install it using pyenv:
```bash
pyenv install 3.10.13
```

#### b. set python version locally
Set python 3.10.13 as the local version for your project:
```bash
pyenv local 3.10.13
```

#### c. verify python version
Check the python version:
```bash
python --version
```

### 3. recreate the virtual environment
If the virtual environment is using the wrong python version, recreate it:

#### a. remove an existing virtual environment
Delete the current venv folder:
```bash
rm -rf venv
```

#### b. create a new virtual environment
Create a new virtual environment with python 3.10.13:
```bash
python -m venv venv
```

#### c. activate the virtual environment
Activate the virtual environment:
```bash
source venv/bin/activate
```

#### d. verify python version in the virtual environment
Check the python version inside the virtual environment:
```bash
python --version
```

### 4. install dependencies
If your project has a requirements.txt file, install the dependencies:
```bash
pip install -r requirements.txt
```

### 5. test the environment
Run a simple python script or command to ensure everything is working:
```bash
python -c "print('environment is working!')"
```