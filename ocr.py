import hashlib
from pathlib import Path
from pdf2image import convert_from_path
import Vision
import Quartz
from PIL import Image
import numpy as np

from models import Document, DocType
from config import Settings

settings = Settings()

def pil_to_cgimage(image):
    # Convert to numpy array
    np_image = np.array(image.convert("RGB"))
    height, width = np_image.shape[:2]

    # Convert to raw bytes
    raw_data = np_image.tobytes()

    # Create a CGDataProvider
    provider = Quartz.CGDataProviderCreateWithData(
        None,        
        raw_data,    
        len(raw_data),  
        None         
    )

    # Assemble the CGImage
    cg_image = Quartz.CGImageCreate(
        width,                                    # pixels wide
        height,                                   # pixels tall
        8,                                        # bits per component (8 = standard)
        24,                                       # bits per pixel (8 x 3 channels)
        width * 3,                                # bytes per row
        Quartz.CGColorSpaceCreateDeviceRGB(),     # RGB color space
        Quartz.kCGImageAlphaNone,                 # no transparency
        provider,                                 # your data source
        None,                                     # no decode array
        False,                                    # no interpolation
        Quartz.kCGRenderingIntentDefault          # standard rendering
    )

    return cg_image

def ocr_image(image) -> tuple[str, float]:
    # Convert image to CGImage
    cg_image = pil_to_cgimage(image)

    # Create Request
    request = Vision.VNRecognizeTextRequest.alloc().init()
    request.setRecognitionLevel_(1)  
    request.setUsesLanguageCorrection_(True) 

    # Create Handler
    handler = Vision.VNImageRequestHandler.alloc()
    handler.initWithCGImage_options_(cg_image, {})

    # Preform Request
    success, error = handler.performRequests_error_([request], None)

    # Extract Results
    observations = request.results()
    lines = []
    confidences = []

    for observation in observations:
        candidate = observation.topCandidates_(1)[0] 
        lines.append(candidate.string())
        confidences.append(candidate.confidence())
    
    text = "\n".join(lines)
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

    return text, avg_confidence

def pdf_to_images(path: Path) -> list:
    return convert_from_path(path, dpi=settings.ocr_dpi)

def read_handwritten_pdf(path: Path) -> Document:
    path = path.resolve()

    # Convert PDF pages to images
    images = pdf_to_images(path)

    # OCR each page, collect text and confidence
    all_text = []
    confidences = []
    
    #extract text and confidence of each image/page
    for i, image in enumerate(images):
        text, confidence = ocr_image(image)
        all_text.append(f"[Page {i+1}]\n{text}")
        confidences.append(confidence)
    
    #combine pages into one string
    full_text = "\n\n".join(all_text)

    #get confidence of all a pages
    avg_confidence = sum(confidences) / len(confidences)

    # Check if confidence is below minimun acceptable confidence
    if avg_confidence < settings.ocr_min_confidence:
        print(f"⚠️  Low confidence on {path.name} ({avg_confidence:.0%}) - check handwriting quality")

    #create Document
    return Document(
        id=hashlib.md5(str(path).encode()).hexdigest(),
        source=str(path),
        content=full_text,
        doc_type=DocType.HANDWRITTEN_PDF,
        ocr_confidence=avg_confidence
    )