# 📄 DocuVision – Python OCR Text Extractor

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

DocuVision is a lightweight, production-ready OCR-powered web application built with Streamlit that allows users to extract text from scanned documents or images using OpenCV and Tesseract OCR. Perfect for digitizing documents, automating data entry, and integrating into AI workflows.

## ✨ Features

- 🖼️ **Multi-format Support**: Upload `.png`, `.jpg`, `.jpeg`, and `.pdf` files
- 🔍 **Advanced Preprocessing**: Automatic image enhancement for better OCR accuracy
- 📝 **Instant Text Extraction**: Real-time OCR processing with Tesseract
- 💾 **Export Options**: Download extracted text as `.txt` or `.docx` files
- 🎯 **High Accuracy**: Optimized preprocessing pipeline for maximum text recognition
- 🚀 **Fast Processing**: Efficient image processing and OCR algorithms
- 📱 **Responsive UI**: Clean, intuitive interface that works on all devices
- 🔧 **Configurable**: Adjustable OCR parameters and preprocessing options

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, OpenCV, Pytesseract
- **Frontend**: Streamlit
- **Image Processing**: Pillow, NumPy
- **OCR Engine**: Tesseract OCR
- **Testing**: pytest, unittest
- **Documentation**: Comprehensive inline comments and docstrings

## 📦 Installation

### Prerequisites

1. **Install Tesseract OCR**:

   - **Windows**: Download from [GitHub releases](https://github.com/tesseract-ocr/tesseract/releases)
   - **macOS**: `brew install tesseract`
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`

2. **Install Poppler (for PDF support)**:

   - **Windows**: Download Poppler from [this link](https://github.com/oschwartz10612/poppler-windows/releases/), extract it, and add the `bin` folder to your system's PATH.
   - **macOS**: `brew install poppler`
   - **Ubuntu/Debian**: `sudo apt-get install poppler-utils`

3. **Clone the repository**:

```bash
git clone https://github.com/yourusername/docuvision-ocr.git
cd docuvision-ocr
```

4. **Install Python dependencies**:

```bash
pip install -r requirements.txt
```

### Quick Start

```bash
streamlit run app.py
```

Open your browser and navigate to `http://localhost:8501`

## 🚀 Usage

### Web Interface

1. Launch the application using `streamlit run app.py`
2. Upload an image or PDF file using the file uploader
3. Adjust preprocessing settings if needed
4. View the extracted text in real-time
5. Download the results as a text or Word document

### Programmatic Usage

```python
from src.ocr_engine import OCREngine
from src.image_processor import ImageProcessor

# Initialize components
processor = ImageProcessor()
ocr_engine = OCREngine()

# Process an image
processed_image = processor.preprocess_image("path/to/image.jpg")
extracted_text = ocr_engine.extract_text(processed_image)

print(extracted_text)
```

## 📁 Project Structure

```
docuvision-ocr/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                  # Project documentation
├── LICENSE                    # MIT license
├── .gitignore                # Git ignore rules
├── src/                      # Source code modules
│   ├── __init__.py
│   ├── ocr_engine.py         # OCR processing logic
│   ├── image_processor.py    # Image preprocessing
│   ├── file_handler.py       # File upload/download handling
│   └── utils.py              # Utility functions
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── test_ocr_engine.py
│   ├── test_image_processor.py
│   └── test_integration.py
├── sample_docs/              # Sample documents for testing
│   ├── example1.png
│   ├── example2.jpg
│   └── example3.pdf
├── docs/                     # Additional documentation
│   ├── API.md
│   └── DEPLOYMENT.md
└── config/                   # Configuration files
    └── settings.py
```

## 🧪 Testing

Run the complete test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/test_ocr_engine.py -v
```

## ⚙️ Configuration

Customize OCR settings in `config/settings.py`:

```python
# OCR Configuration
OCR_CONFIG = {
    'language': 'eng',
    'page_segmentation_mode': 6,
    'ocr_engine_mode': 3,
    'confidence_threshold': 30
}

# Image Processing Configuration
IMAGE_CONFIG = {
    'max_width': 2000,
    'max_height': 2000,
    'gaussian_blur_kernel': (5, 5),
    'threshold_type': 'adaptive'
}
```

## 🌐 Deployment

### Streamlit Cloud

1. Push your code to GitHub
2. Visit [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your repository
4. Deploy with one click

### Docker

```bash
# Build the image
docker build -t docuvision-ocr .

# Run the container
docker run -p 8501:8501 docuvision-ocr
```

### Render

1. Create a `render.yaml` file (included in the project)
2. Connect your GitHub repository to Render
3. Deploy automatically

## 📊 Performance

- **Average Processing Time**: 2-5 seconds per image
- **Supported File Sizes**: Up to 10MB
- **Accuracy**: 95%+ on clear, high-contrast documents
- **Memory Usage**: ~100MB baseline + image size

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for the OCR engine
- [Streamlit](https://streamlit.io/) for the web framework
- [OpenCV](https://opencv.org/) for image processing capabilities

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/docuvision-ocr/issues) page
2. Create a new issue with detailed information
3. Contact the maintainers

---

⭐ **Star this repository if you find it helpful!**
