#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# setup_venv.sh — create + activate this project's NAMED venv (we never use .venv).
# For macOS / Linux / WSL.  (Windows PowerShell: use setup_venv.ps1)
#
#   source setup_venv.sh        # <- run it SOURCED so the activation sticks
#
# Why "source"? A script runs in a child shell. Activating a venv only changes
# the shell it runs in — so if you run ./setup_venv.sh normally, the venv is
# built and deps install, but your shell is NOT left activated. Sourcing runs
# the lines in YOUR shell, so ($VENV_NAME) appears in your prompt and stays.
#
# WSL speed note: if this project lives on a Windows drive (a /mnt/* path),
# building a venv there is PAINFULLY slow (the 9p filesystem bridge chokes on
# the thousands of tiny files a venv + pip create). So when we detect /mnt/*,
# we put the venv on native Linux storage (~/venvs/) instead. Seconds, not
# minutes. The project files stay where they are.
# ---------------------------------------------------------------------------

VENV_NAME="aja-cca-f"

# Are we sourced? (Activation only persists if we are.)
(return 0 2>/dev/null) && _SOURCED=1 || _SOURCED=0

# Folder this script lives in — whether sourced or executed, bash or zsh.
# (bash exposes BASH_SOURCE; zsh sets $0 to the sourced file path.)
if [ -n "${BASH_SOURCE:-}" ]; then
  _SELF="${BASH_SOURCE[0]}"
else
  _SELF="$0"
fi
cd "$(dirname "$_SELF")" || return 1 2>/dev/null || exit 1
PROJECT_DIR="$(pwd)"

# Decide WHERE the venv goes.
case "$PROJECT_DIR" in
  /mnt/*)
    # On a Windows drive under WSL — keep the venv off the slow bridge.
    VENV_DIR="$HOME/venvs/$VENV_NAME"
    mkdir -p "$HOME/venvs"
    echo "WSL detected: project is on a Windows drive ($PROJECT_DIR)."
    echo "Putting the venv on fast native Linux storage instead:"
    echo "    $VENV_DIR"
    ;;
  *)
    VENV_DIR="$PROJECT_DIR/$VENV_NAME"
    ;;
esac

# Find a Python 3 interpreter.
PY="$(command -v python3 || command -v python || true)"
if [ -z "$PY" ]; then
  echo "Python 3.10+ was not found on your PATH. Install it, then re-run."
  return 1 2>/dev/null || exit 1
fi

# Create the venv once; reuse it on later runs.
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating named venv:   $VENV_DIR"
  "$PY" -m venv "$VENV_DIR" || { echo "venv creation failed."; return 1 2>/dev/null || exit 1; }
else
  echo "Reusing existing venv: $VENV_DIR"
fi

# Activate it in THIS shell.
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

# Install dependencies into the venv (requirements.txt is in the project dir).
python -m pip install --quiet --upgrade pip
pip install -r "$PROJECT_DIR/requirements.txt"

# Scaffold .env for the Anthropic key if it isn't there yet (never overwrites).
if [ ! -f "$PROJECT_DIR/.env" ] && [ -f "$PROJECT_DIR/.env.example" ]; then
  cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
  echo "Created .env from .env.example — add your ANTHROPIC_API_KEY."
fi

echo ""
echo "Done. The venv '$VENV_NAME' is active — your prompt should show ($VENV_NAME)."
if [ "$_SOURCED" = "0" ]; then
  echo "NOTE: you ran this WITHOUT 'source', so activation did not stick."
  echo "      Re-run it as:   source setup_venv.sh"
fi
echo "Deactivate anytime with:  deactivate"
