run:
	ollama serve &
	uv run uvicorn app:app --reload &
	uv run streamlit run streamlit_app.py

stop:
	-pkill -f "ollama serve"
	-pkill -f "uvicorn app:app"
	-pkill -f "streamlit run"