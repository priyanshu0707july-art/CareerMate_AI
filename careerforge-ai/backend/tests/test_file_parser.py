import pytest
from fastapi import HTTPException
from app.services.file_parser import extract_text_from_file
from io import BytesIO

class MockUploadFile:
    def __init__(self, filename, content):
        self.filename = filename
        self.file = BytesIO(content)

def test_file_parser_empty_file():
    empty_file = MockUploadFile("test.pdf", b"")
    with pytest.raises(HTTPException) as excinfo:
        extract_text_from_file(empty_file)
    assert excinfo.value.status_code == 400
    assert "empty" in excinfo.value.detail.lower()

def test_file_parser_unsupported_format():
    txt_file = MockUploadFile("test.txt", b"Hello world")
    with pytest.raises(HTTPException) as excinfo:
        extract_text_from_file(txt_file)
    assert excinfo.value.status_code == 415

def test_file_parser_large_file():
    large_file = MockUploadFile("test.pdf", b"0" * (6 * 1024 * 1024))  # 6 MB
    with pytest.raises(HTTPException) as excinfo:
        extract_text_from_file(large_file)
    assert excinfo.value.status_code == 413
