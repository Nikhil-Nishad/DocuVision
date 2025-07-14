"""
Integration tests for the DocuVision application.

These tests check the interaction between different components,
such as the ImageProcessor and OCREngine.
"""

import pytest
import numpy as np
import os
from unittest.mock import patch

from src.image_processor import ImageProcessor
from src.ocr_engine import OCREngine
from src.file_handler import FileHandler

# Note to user: These tests may require sample files in the 'sample_docs' directory.
# Please add 'test_image.png' and 'test_doc.pdf' to 'sample_docs' for full test coverage.

@pytest.fixture
def image_processor():
    return ImageProcessor()

@pytest.fixture
def ocr_engine():
    with patch.object(OCREngine, '_validate_tesseract_installation', return_value=None):
        yield OCREngine()

@pytest.fixture
def file_handler():
    return FileHandler()

@pytest.mark.skipif(not os.path.exists('sample_docs/test_image.png'), reason="Sample image not found")
def test_full_pipeline_for_image(image_processor, ocr_engine):
    """
    Test the full pipeline from image preprocessing to text extraction.
    """
    # 1. Preprocess the image
    processed_image = image_processor.preprocess_image('sample_docs/test_image.png')
    assert isinstance(processed_image, np.ndarray)

    # 2. Extract text from the processed image
    with patch('pytesseract.image_to_string') as mock_ocr:
        mock_ocr.return_value = "Sample Text"
        extracted_text = ocr_engine.extract_text(processed_image)
        
        # Verify that the OCR function was called
        mock_ocr.assert_called_once()
        
        # Verify that some text is returned
        assert isinstance(extracted_text, str)
        assert extracted_text == "Sample Text"

@pytest.mark.skipif(not os.path.exists('sample_docs/test_doc.pdf'), reason="Sample PDF not found")
def test_full_pipeline_for_pdf(file_handler, image_processor, ocr_engine):
    """
    Test the full pipeline for PDF processing.
    """
    # 1. Convert PDF to images
    # We assume the user has installed pdf2image and poppler
    images = file_handler.convert_pdf_to_images('sample_docs/test_doc.pdf')
    assert isinstance(images, list)
    assert len(images) > 0
    assert isinstance(images[0], np.ndarray)

    # 2. Process and OCR the first page
    first_page = images[0]
    processed_page = image_processor.preprocess_image(first_page)
    
    with patch('pytesseract.image_to_string') as mock_ocr:
        mock_ocr.return_value = "PDF Sample Text"
        extracted_text = ocr_engine.extract_text(processed_page)
        
        mock_ocr.assert_called_once()
        assert extracted_text == "PDF Sample Text"

def test_file_handler_and_save_text(file_handler):
    """
    Test saving extracted text to different formats.
    """
    sample_text = "This is a test for saving files."
    base_filename = "test_output"
    
    # Test TXT saving
    txt_path = file_handler.save_text_to_file(sample_text, base_filename, 'txt')
    assert os.path.exists(txt_path)
    with open(txt_path, 'r', encoding='utf-8') as f:
        assert f.read() == sample_text
    
    # Test DOCX saving
    docx_path = file_handler.save_text_to_file(sample_text, base_filename, 'docx')
    assert os.path.exists(docx_path)
    
    # Clean up created files
    os.remove(txt_path)
    os.remove(docx_path) 