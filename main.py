from rich import print
from rich.panel import Panel
from rich.text import Text
import typer

from ingest import load_document, chunk_document
from store import count, add_chunks
from generator import generate
from config import Settings


settings = Settings()
app = typer.Typer()

@app.command(name="ingest")
def ingest():
    #gets all the txt files in data/raw
    files = list((settings.data_dir / "raw").glob("*.txt"))

    #extract chunks from each file and add them to db
    num_chunks = 0
    num_documents = 0
    for file in files:
        document = load_document(file)
        chunks = chunk_document(document)
        add_chunks(chunks)
        #stats for summary
        num_chunks += chunks[0].metadata["total_chunks"]
        num_documents += 1
    
    #print summary
    message = f"{num_chunks} chunks were added from {num_documents} files"
    print(Panel(message, title="Summary", border_style="green", expand=False))

@app.command(name="ask")
def ask(question: str):
    answer = generate(question)
    #print answer
    print(Panel(answer.answer, title="Knowledge Agent", border_style="green"))

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