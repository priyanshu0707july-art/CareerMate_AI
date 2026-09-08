import io
from fastapi import HTTPException, status, UploadFile
from pypdf import PdfReader
from docx import Document

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

def extract_text_from_file(file: UploadFile) -> str:
    # Validate file size (can't easily do it without reading, but we can read the first chunk or all and check size)
    # Since we are reading into memory, we should ensure it's not huge. 
    # FastAPI UploadFile allows seeking.
    
    file.file.seek(0, 2) # go to end
    file_size = file.file.tell()
    file.file.seek(0) # reset
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds the 5MB limit"
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty"
        )
        
    filename = file.filename.lower()
    content = file.file.read()
    
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(content)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(content)
    else:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file format. Only PDF and DOCX are allowed."
        )

def extract_text_from_pdf(content: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(content))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        if not text.strip():
            raise ValueError("No text could be extracted from the PDF")
            
        return text
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not parse PDF. File might be corrupted or empty. Error: {str(e)}"
        )

def extract_text_from_docx(content: bytes) -> str:
    try:
        doc = Document(io.BytesIO(content))
        text = "\n".join([para.text for para in doc.paragraphs])
        
        if not text.strip():
            raise ValueError("No text could be extracted from the DOCX")
            
        return text
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not parse DOCX. File might be corrupted or empty. Error: {str(e)}"
        )
