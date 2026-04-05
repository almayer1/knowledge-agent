run:
	uv run uvicorn app:app --reload &
	uv run streamlit run streamlit_app.py

stop:
	-pkill -f uvicorn
	-pkill -f streamlit

dev:
	ollama serve &
	uv run uvicorn app:app --reload &
	uv run streamlit run streamlit_app.py