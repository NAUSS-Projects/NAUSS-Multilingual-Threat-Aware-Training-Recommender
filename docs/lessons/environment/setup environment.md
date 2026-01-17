Great question — this is **the key misunderstanding point** with `pyenv`, and once it clicks, everything else will make sense.

I’ll explain it the way a systems person would, starting from the *real problem*.

---

## 1️⃣ Problem statement (what you *think* happened vs what *actually* happened)

You think:

> “I told pyenv to use Python 3.10.13, so my venv should use it.”

But your shell reality is:

> ❌ Your shell is **still using system Python 3.13**
> ❌ `pyenv` is installed but **NOT ACTIVE**

That’s why:

* `python` is “command not found”
* `python3` is **still 3.13**
* `torch` cannot install

---

## 2️⃣ The root cause (the real WHY)

### 🔴 This line is the smoking gun

```
pyenv: shell integration not enabled
```

This means:

> **pyenv is not hooked into your shell**
> so it cannot intercept `python` / `python3`

### pyenv is NOT magic

It works by inserting **shims** at the **front of your PATH**.

Right now:

```
python3  → /usr/bin/python3  → Python 3.13
```

What you *want*:

```
python3 → ~/.pyenv/shims/python3 → Python 3.10.13
```

But your shell never loaded pyenv.

---

## 3️⃣ Why `pyenv local 3.10.13` did nothing

`pyenv local` only creates this file:

```
.python-version
```

That file says:

```
3.10.13
```

But unless pyenv is **initialized**, your shell **never reads it**.

So:

* The file exists ✅
* The shell ignores it ❌

---

## 4️⃣ Why `python -m venv` failed

```
zsh: command not found: python
```

macOS no longer guarantees `python` exists.
Only `python3`.

But even worse:

```
python3 --version
Python 3.13.6
```

This proves:

> ❌ pyenv shims are not active
> ❌ system Python is still winning

---

## 5️⃣ Why torch STILL cannot install

Same root cause, downstream effect:

```
pip install torch
ERROR: No matching distribution found
```

Because pip sees:

```
Python 3.13
```

And PyTorch says:

```
❌ I do not ship wheels for Python 3.13
```

So pip correctly refuses.

---

## 6️⃣ The fix (this is the missing step)

You must **initialize pyenv in your shell**.

### Run this ONCE:

```bash
pyenv init
```

It will tell you to add something like this.

### Add to `~/.zshrc` (important)

```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

Then reload shell:

```bash
exec zsh
```

---

## 7️⃣ Verify pyenv is now active (critical)

Run:

```bash
which python3
```

You should see something like:

```
/Users/macbookpro/.pyenv/shims/python3
```

Then:

```bash
python3 --version
```

Expected:

```
Python 3.10.13
```

If you don’t see this — **stop**, pyenv is still not active.

---

## 8️⃣ Now redo venv (correctly)

```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
python --version
```

✅ Must say:

```
Python 3.10.13
```

---

## 9️⃣ Install torch (this time it works)

```bash
pip install torch
pip install sentence-transformers
```

No backtracking.
No errors.
No drama.

---

## 🔟 Mental model (this is the “aha”)

```
Terminal starts
   │
   ├─ loads ~/.zshrc ❌ (before)
   │
   └─ loads ~/.zshrc ✅ (after pyenv init)
            │
            ▼
      pyenv shims active
            │
            ▼
      python3 → 3.10.13
            │
            ▼
      torch wheel exists ✅
```

---

## Vocabulary notes (English)

* **shim**: a small redirect program
* **PATH**: list of directories searched for commands
* **initialize**: make a tool active in the environment
* **system Python**: Python shipped with the OS

---

## Final answer (one sentence)

**Because pyenv was never initialized, your shell kept using system Python 3.13, and PyTorch does not support it.**

Once you enable pyenv properly, everything falls into place.

If you want, next we can:

* Lock this project with `.python-version`
* Add `requirements.txt`
* Or Dockerize it so this *never* breaks again
