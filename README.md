# multilingual threat-aware training recommender

a system that analyzes your past training history and compares it with recent news or threat reports to recommend new subject areas or training courses. it supports both arabic and english languages with cross-lingual semantic analysis.

## prerequisites

- python 3.10.13
- ollama installed and running with the phi4 model
- git for cloning the repository

## running the program

> ![IMPORTANT]
> check setting up the environment on [environment-setup.md](./docs/environment/environment-setup.md) and then follow the following commands to setup the server

```bash
python3 app.py
```

then the server will run on https://127.0.00.1:5000 (most likey).