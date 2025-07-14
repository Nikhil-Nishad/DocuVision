"""
Unit tests for the ImageProcessor class.
"""

import pytest
import numpy as np
from PIL import Image
from unittest.mock import patch, MagicMock
import os

from src.image_processor import ImageProcessor, IMAGE_CONFIG

@pytest.fixture
def processor():
    """Returns an ImageProcessor instance."""
    return ImageProcessor()

def create_mock_image(width=100, height=100, channels=3):
    """Creates a mock numpy image."""
    if channels > 0:
        return np.uint8(np.random.rand(height, width, channels) * 255)
    else:
        return np.uint8(np.random.rand(height, width) * 255)

def test_initialization(processor):
    """Test ImageProcessor initialization."""
    assert processor.config == IMAGE_CONFIG

def test_load_image_from_numpy(processor):
    """Test loading an image from a numpy array."""
    mock_img = create_mock_image()
    loaded_img = processor._load_image(mock_img)
    assert np.array_equal(loaded_img, mock_img)
    assert id(loaded_img) != id(mock_img)  # Should be a copy

def test_load_image_from_pil(processor):
    """Test loading an image from a PIL Image."""
    mock_pil_img = Image.fromarray(create_mock_image())
    loaded_img = processor._load_image(mock_pil_img)
    assert isinstance(loaded_img, np.ndarray)
    assert loaded_img.shape[:2] == (100, 100)

@patch('cv2.imread')
def test_load_image_from_path(mock_imread, processor):
    """Test loading an image from a file path."""
    mock_imread.return_value = create_mock_image()
    loaded_img = processor._load_image("dummy/path/to/image.png")
    mock_imread.assert_called_with("dummy/path/to/image.png")
    assert isinstance(loaded_img, np.ndarray)

def test_resize_image(processor):
    """Test image resizing."""
    large_image = create_mock_image(width=3000, height=3000)
    processor.config['max_width'] = 1000
    processor.config['max_height'] = 1000
    
    resized_image = processor._resize_image(large_image)
    assert resized_image.shape[0] <= 1000
    assert resized_image.shape[1] <= 1000

def test_grayscale_conversion(processor):
    """Test grayscale conversion."""
    image_bgr = create_mock_image(channels=3)
    # This is a simplified way to access a protected method for testing
    processed_image = processor._light_preprocessing(image_bgr) 
    assert len(processed_image.shape) == 2

def test_noise_reduction(processor):
    """Test noise reduction."""
    image_gray = create_mock_image(channels=0)
    denoised_image = processor._reduce_noise(image_gray)
    assert denoised_image.shape == image_gray.shape

def test_adaptive_thresholding(processor):
    """Test adaptive thresholding."""
    image_gray = create_mock_image(channels=0)
    thresholded_image = processor._apply_threshold(image_gray, method='adaptive')
    assert thresholded_image.shape == image_gray.shape
    # Check if the image is binary
    assert len(np.unique(thresholded_image)) <= 2

# Note to user: The following test requires a sample image.
# Please create a 'test_image.png' in the 'sample_docs' directory.
@pytest.mark.skipif(not os.path.exists('sample_docs/test_image.png'), reason="Sample image not found")
def test_preprocess_image_pipeline_from_file():
    """Test the full preprocessing pipeline with a real image file."""
    # This is a more realistic integration test for the processor
    processor = ImageProcessor()
    # The user should provide a sample image for this test to run
    processed_image = processor.preprocess_image('sample_docs/test_image.png')
    assert isinstance(processed_image, np.ndarray)
    assert len(processed_image.shape) == 2  # Should be grayscale 