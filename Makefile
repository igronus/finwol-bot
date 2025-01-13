.PHONY: run install clean

# Default Python interpreter
PYTHON = python3
VENV = venv
BIN = $(VENV)/bin

# Install dependencies
install:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install -r requirements.txt

# Run bot with auto-restart
run:
	@while true; do \
		echo "Starting bot..."; \
		$(BIN)/python bot.py; \
		echo "Bot crashed. Restarting in 5 seconds..."; \
		sleep 5; \
	done

# Clean up pyc files and venv
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf $(VENV) 