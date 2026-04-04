from rich import print
from rich.panel import Panel
from rich.text import Text
import typer

from exceptions import OllamaConnectionError, EmptyKnowledgeBaseError, UnsupportedFileTypeError, EmptyFileError
from config import Settings
from ingest import load_document, chunk_document
from store import count, add_chunks
from generator import generate



settings = Settings()
app = typer.Typer()

@app.command(name="ingest")
def ingest():
    # Get all txt and pdf files from data/raw
    txt_files = (settings.data_dir / "raw").glob("*.txt")
    pdf_files = (settings.data_dir / "raw").glob("*.pdf")
    files = list(txt_files) + list(pdf_files)

    if len(files) == 0:
        print("There are no files to search through! Please provide file(s)")
        return

    # Extract chunks from each file and add them to db
    num_chunks = 0
    num_documents = 0
    for file in files:
        try:
            document = load_document(file)
        except UnsupportedFileTypeError as e:
            print(f"[yellow]Warning: {e}[/yellow]")
            continue
        except UnicodeDecodeError as e:
            print(f"[yellow]Warning: {e}[/yellow]")
            continue
        except EmptyFileError as e:
            print(f"[yellow]Warning: {e}[/yellow]")

        chunks = chunk_document(document)
        add_chunks(chunks)
        
        #stats for summary
        num_chunks += chunks[0].metadata["total_chunks"]
        num_documents += 1
    
    # Print summary
    message = f"{num_chunks} chunks were added from {num_documents} files"
    print(Panel(message, title="Summary", border_style="green", expand=False))

@app.command(name="ask")
def ask(question: str):
    # Error: if question empty
    if not question.strip():
        print("[red]Error: Please enter a question.[/red]")
        return

    try:
        answer = generate(question)
    except OllamaConnectionError as e:
        print(f"[red]Error: {e}[/red]")
        return
    except EmptyKnowledgeBaseError as e:
        print(f"[red]Error: {e}[/red]")
        return
    
    # Print answer
    print(Panel(answer.answer, title="Knowledge Agent", border_style="green"))

    # Print sources underneath answer
    print("[bold]Sources:[/bold]")
    for i, source in enumerate(answer.sources):
        print(f"  [cyan][Source {i+1}][/cyan] {source.chunk.metadata['source']}")


@app.command(name="stats")
def stats():
    message = f"There Are {count()} Chunks"
    print(Panel(message, title="Stats", border_style="green", expand=False))
    
    

if __name__ == "__main__":
    app()