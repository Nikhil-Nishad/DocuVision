# API Reference

This document provides an API reference for the core modules of DocuVision.

---

## `src.ocr_engine.OCREngine`

Handles all OCR-related operations.

### `__init__(self, config=None)`

Initializes the OCR engine with optional custom configuration.

### `extract_text(self, image, **kwargs)`

Extracts text from a preprocessed image (numpy array).

- **Args**:
  - `image` (np.ndarray): The image to process.
  - `**kwargs`: Override OCR parameters.
- **Returns**: `str` - The extracted text.

### `extract_text_with_confidence(self, image, **kwargs)`

Extracts text along with word-level confidence scores.

- **Returns**: `Tuple[str, List[Dict]]` - The text and a list of confidence data.

### `get_supported_languages(self)`

Returns a list of Tesseract-supported languages.

---

## `src.image_processor.ImageProcessor`

Handles all image preprocessing tasks.

### `__init__(self, config=None)`

Initializes the image processor with optional custom configuration.

### `preprocess_image(self, image_input, enhancement_level='medium')`

Applies a full preprocessing pipeline to an image.

- **Args**:
  - `image_input`: Path, PIL Image, or numpy array.
  - `enhancement_level` (str): 'light', 'medium', or 'heavy'.
- **Returns**: `np.ndarray` - The processed image.

---

## `src.file_handler.FileHandler`

Manages file I/O operations.

### `__init__(self)`

Initializes the file handler.

### `validate_file(self, uploaded_file)`

Validates a file uploaded via Streamlit.

- **Returns**: `Tuple[bool, str]` - (is_valid, message).

### `process_uploaded_file(self, uploaded_file)`

Handles an uploaded file and returns a list of images ready for OCR.

- **Returns**: `List[np.ndarray]` - List of images.

### `save_text_to_file(self, text, filename, format_type='txt')`

Saves text to a `.txt` or `.docx` file.

- **Returns**: `str` - Path to the saved file.

---

## `src.utils`

Provides helper functions for the application.

### `setup_logger()`

Configures and returns a logger instance.

### `display_header()`

Displays the Streamlit application header.
