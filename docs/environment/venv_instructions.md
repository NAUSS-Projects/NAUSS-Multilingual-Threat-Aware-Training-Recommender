## Local Development instructions using python virtual environment

1. Install pyenv

    1. install pyenv for managing python version

    ```sh
    brew install pyenv
    ```

    2. install a stable version of python that can work with pytorch and
    the dependecies seamisly.

    ```sh
    pyenv install 3.10.13
    ```

    3. switch to python 3.10.13

    ```sh
    pyenv local 3.10.13
    ```

2. Create Python Virtual Environment

    ```sh
    python -m venv venv
    ```

    activate the environment

    ```sh
    source venv/bin/activate
    ```


3. troubleshooting 

    if venv shell not updated to the local python version like the follwing:

    ```sh
    ➜ ProjectCode git:(main) ✗ pyenv install 3.10.13 pyenv: /Users/macbookpro/.pyenv/versions/3.10.13 already exists continue with installation? (y/N) N 
    ➜ ProjectCode git:(main) ✗ pyenv local 3.10.13 
    ➜ ProjectCode git:(main) ✗ rm -rf venv 
    ➜ ProjectCode git:(main) ✗ python -m venv venv zsh: command not found: python 
    ➜ ProjectCode git:(main) ✗ python3 -m venv venv 
    ➜ ProjectCode git:(main) ✗ source venv/bin/activate (venv) 
    ➜ ProjectCode git:(main) ✗ python3 --version Python 3.13.6
    ```

    1. initialize the pyenv

    ```sh
    pyenv init
    ```

    2. Add to ~/.zshrc
    ```sh
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
    ```

    3. Reload shell
    ```sh 
    exec zsh
    ```

    4. verify

    ```sh
    which python3
    ```

    or 
    ```sh
    python3 --version
    ```