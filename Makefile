.PHONY: run install install36 clean

# Default Python interpreter
PYTHON = python3
VENV = venv
BIN = $(VENV)/bin

# Install dependencies for Python 3.7+
install:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt

# Install dependencies for Python 3.6
install36:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements36.txt

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