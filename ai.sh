# To run this script
# Navigate to the directory containing this file 
#  % cd ~/Users/ben/Library/Mobile\ Documents/com~apple~CloudDocs/Projects/LocalScripts
# chmod +x hello.sh
# Now it can be run from terminal with ./hello.sh

#!/bin/bash

# Specify the directory where the Python scripts are located
SCRIPTS_DIR="/Users/ben/Library/Mobile Documents/com~apple~CloudDocs/Projects/LocalScripts"

# Move to the scripts directory
cd "$SCRIPTS_DIR" || exit

# Option to directly run a script if provided
if [ "$1" ]; then
  script_to_run=$1
  shift
else
  # If not directly provided, ask the user
  echo "What script do you want to run?"
  select script_to_run in *.py
  do
    [[ -f $script_to_run ]] && break
    echo "Please choose a number from the list."
  done
fi

# Default parameters
MODEL="gpt-3.5-turbo"
SYSTEM_PROMPT="You are a helpful AI assistant."
MAX_TOKENS="1000"
TEMPERATURE="0.5"

# Custom parameters based on chosen script
if [[ $script_to_run == 'singleshot.py' || $script_to_run == 'chat.py' ]]; then
  read -p "user: " USER_MESSAGE
fi

# Run the chosen script with the parameters
if [[ $script_to_run == 'whisper.py' || $script_to_run == "verse2resource.py" ]]; then
  python3 "$script_to_run"
else
  # Ask to change default parameters
  read -p "Change default parameters? (y/n): " change_default
  if [[ $change_default == 'y' || $change_default == 'Y' ]]; then
    read -p "Enter model (default: gpt-3.5-turbo): " input
    [ "$input" != "" ] && MODEL=$input
    read -p "Enter system prompt (default: You are a helpful AI assistant.): " input
    [ "$input" != "" ] && SYSTEM_PROMPT=$input
    read -p "Enter max tokens (default: 1000): " input
    [ "$input" != "" ] && MAX_TOKENS=$input
    read -p "Enter temperature (default: 0.5): " input
    [ "$input" != "" ] && TEMPERATURE=$input
  fi

  python3 "$script_to_run" "$USER_MESSAGE" "$MODEL" "$SYSTEM_PROMPT" "$MAX_TOKENS" "$TEMPERATURE" "$@"
fi