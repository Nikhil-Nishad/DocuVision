"""
Unit tests for the OCREngine class.
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from src.ocr_engine import OCREngine, OCR_CONFIG

@pytest.fixture
def engine():
    """Returns an OCREngine instance with a mocked Tesseract validation."""
    with patch.object(OCREngine, '_validate_tesseract_installation', return_value=None):
        yield OCREngine()

def create_mock_image(width=100, height=100):
    """Creates a mock numpy image."""
    return np.uint8(np.random.rand(height, width) * 255)

def test_initialization(engine):
    """Test OCREngine initialization."""
    assert engine.config == OCR_CONFIG

@patch('pytesseract.image_to_string')
def test_extract_text(mock_image_to_string, engine):
    """Test basic text extraction."""
    mock_image_to_string.return_value = "This is a test."
    image = create_mock_image()
    
    extracted_text = engine.extract_text(image)
    
    mock_image_to_string.assert_called_once()
    assert extracted_text == "This is a test."

def test_extract_text_with_invalid_image(engine):
    """Test text extraction with invalid image."""
    with pytest.raises(ValueError, match="Invalid or empty image provided"):
        engine.extract_text(None)
    
    with pytest.raises(ValueError, match="Invalid or empty image provided"):
        engine.extract_text(np.array([]))

@patch('pytesseract.image_to_data')
def test_extract_text_with_confidence(mock_image_to_data, engine):
    """Test text extraction with confidence scores."""
    mock_data = {
        'text': ['hello', 'world'],
        'conf': ['95', '90'],
        'left': [10, 80], 'top': [10, 10],
        'width': [70, 70], 'height': [20, 20]
    }
    mock_image_to_data.return_value = mock_data
    image = create_mock_image()

    text, confidence_data = engine.extract_text_with_confidence(image)

    assert text == "hello world"
    assert len(confidence_data) == 2
    assert confidence_data[0]['word'] == 'hello'
    assert confidence_data[0]['confidence'] == 95

@patch('pytesseract.get_languages')
def test_get_supported_languages(mock_get_languages, engine):
    """Test getting supported languages."""
    mock_get_languages.return_value = ['eng', 'fra', 'deu']
    languages = engine.get_supported_languages()
    assert languages == ['eng', 'fra', 'deu']

def test_build_tesseract_config(engine):
    """Test building the Tesseract config string."""
    config = {
        'page_segmentation_mode': 1,
        'ocr_engine_mode': 2,
        'custom_config': '-c my_var=1'
    }
    config_str = engine._build_tesseract_config(config)
    assert "--psm 1" in config_str
    assert "--oem 2" in config_str
    assert "-c my_var=1" in config_str

def test_clean_extracted_text(engine):
    """Test cleaning of extracted text."""
    raw_text = "  this |s a test   with extra   spaces and artifacts. "
    cleaned_text = engine._clean_extracted_text(raw_text)
    assert cleaned_text == "this Is a test with extra spaces and artifacts." 