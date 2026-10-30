#!/bin/zsh

# Move to the folder containing this script
cd "$(dirname "$0")" || exit 1

echo "=================================="
echo "       NEWS RESEARCHER SETUP"
echo "=================================="

# Check whether Python 3 is installed
if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: Python 3 is not installed."
    echo "Please install Python 3 and run this setup again."
    read -k 1 "?Press any key to close..."
    exit 1
fi

echo "Python found:"
python3 --version

# Create virtual environment if it does not exist
if [ ! -d ".venv" ]; then
    echo "Creating Python environment..."
    python3 -m venv .venv || exit 1
else
    echo "Python environment already exists."
fi

# Activate environment
source .venv/bin/activate

# Install dependencies
echo "Installing application dependencies..."
python -m pip install --upgrade pip || exit 1
python -m pip install -r requirements.txt || exit 1

echo ""
echo "=================================="
echo "SETUP COMPLETED SUCCESSFULLY"
echo "=================================="
echo "You can now double-click start_news.command"
read -k 1 "?Press any key to close..."