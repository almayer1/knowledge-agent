from rich import print
from rich.panel import Panel
from rich.text import Text
import typer

from store import count
from generator import generate

app = typer.Typer()

@app.command(name="ingest")
def ingest():
    pass

@app.command(name="ask")
def ask(question: str):
    answer = generate(question)
    #print answer
    print(Panel(answer.answer, title="Answer", border_style="green"))

    #print sources underneath answer
    print("[bold]Sources:[/bold]")
    for i, source in enumerate(answer.sources):
        print(f"  [cyan][Source {i+1}][/cyan] {source.chunk.metadata['source']}")


@app.command(name="stats")
def stats():
    message = f"There Are {count()} Chunks"
    print(Panel(message, title="Stats", border_style="green", expand=False))
    
    

if __name__ == "__main__":
    app()