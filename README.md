# Git Commands and Exiting Vim Guide

## Basic Git Workflow

```sh
git add .         # Stage all changes
git commit -m "Your commit message"  # Commit staged changes with a message
git push origin main  # Push changes to GitHub (replace 'main' with your branch name if different)
```

## Steps to Exit Vim and Save Your Commit
1. **Press `Esc`** – This exits INSERT mode.
2. **Type `:wq`** – This means "write (save) and quit."
3. **Press `Enter`** – This confirms the command and exits Vim.

## If You Want to Cancel the Commit Instead
1. **Press `Esc`** to ensure you're not in INSERT mode.
2. **Type `:q!`** – This quits **without saving**.
3. **Press `Enter`** – This discards the commit message and exits Vim.

