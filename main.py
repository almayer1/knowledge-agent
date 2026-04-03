from rich import print
from rich.panel import Panel
from rich.text import Text
import typer

from store import count

app = typer.Typer()

@app.command(name="ingest")
def ingest():
    pass

@app.command(name="ask")
def ask(question: str):
    pass

@app.command(name="stats")
def stats():
    count = count()
    

if __name__ == "__main__":
    app()