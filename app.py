from fastapi import FastAPI, HTTPException

from config import Settings
from exceptions import OllamaConnectionError, EmptyKnowledgeBaseError, UnsupportedFileTypeError, EmptyFileError
from models import AskRequest, IngestResponse, StatsResponse
from ingest import load_document, chunk_document
from store import count, add_chunks
from generator import generate

settings = Settings()
app = FastAPI(
    title="Knowledge Agent API",
    description="Query your personal knowledge base"
)

@app.post("/ingest")
def ingest():
    # Get all txt and pdf files from data/raw
    txt_files = (settings.data_dir / "raw").glob("*.txt")
    pdf_files = (settings.data_dir / "raw").glob("*.pdf")
    files = list(txt_files) + list(pdf_files)

    if len(files) == 0:
        raise HTTPException(status_code=400, detail="No files found. Add files before ingesting.")

    # Extract chunks from each file and add them to db
    warnings = []
    num_chunks = 0
    num_documents = 0
    for file in files:
        try:
            document = load_document(file)
        except UnsupportedFileTypeError as e:
            warnings.append(str(e))
            continue
        except UnicodeDecodeError as e:
            warnings.append(str(e))
            continue
        except EmptyFileError as e:
            warnings.append(str(e))
            continue

        chunks = chunk_document(document)
        add_chunks(chunks)
        
        #stats for summary
        num_chunks += chunks[0].metadata["total_chunks"]
        num_documents += 1

    return IngestResponse(
        chunks_added = num_chunks,
        files_processed=num_documents,
        warnings=warnings
    )

@app.post("/ask")
def ask(request: AskRequest):
     # if question empty
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Please enter a question.")

    try:
        answer = generate(request.question)
    except OllamaConnectionError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except EmptyKnowledgeBaseError as e:
        raise HTTPException(status_code=503, detail=str(e))
    
    return answer


@app.get("/stats")
def stats():
    return StatsResponse(
        chunk_count=count()
    )

