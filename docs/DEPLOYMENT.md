# Deployment Guide

This guide provides detailed instructions for deploying the DocuVision application using various platforms.

---

## 1. Streamlit Cloud

Streamlit Cloud is the easiest way to deploy your application.

### Prerequisites

- Your app is in a public or private GitHub repository.
- You have a `requirements.txt` file.
- Your main application file is named `app.py`.

### Steps

1.  **Push to GitHub**: Make sure your latest code is pushed to your GitHub repository.
2.  **Sign up for Streamlit Cloud**: Go to [share.streamlit.io](https://share.streamlit.io) and sign up.
3.  **Deploy**:
    - Click "New app".
    - Connect your GitHub account and select the repository.
    - Specify the branch and the main file path (`app.py`).
    - Click "Deploy!".

Your application will be live in a few minutes.

---

## 2. Docker

Deploying with Docker provides more control and portability.

### Prerequisites

- Docker is installed on your machine.
- A `Dockerfile` is present in your project root (see below).

### `Dockerfile`

```Dockerfile
# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# Tesseract for OCR, Poppler for PDF handling
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Set the entrypoint for the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Steps

1.  **Build the Docker image**:
    ```bash
    docker build -t docuvision-ocr .
    ```
2.  **Run the Docker container**:
    ```bash
    docker run -p 8501:8501 docuvision-ocr
    ```
    Your app will be accessible at `http://localhost:8501`.

---

## 3. Render

Render is another cloud platform that makes deployment simple.

### Prerequisites

- Your code is on GitHub.
- You have a Render account.

### Steps

1. **Create a `render.yaml` file** in your project root (or use the web UI).

   ```yaml
   services:
     - type: web
       name: docuvision
       env: python
       plan: free # or your preferred plan
       buildCommand: "pip install -r requirements.txt"
       startCommand: "streamlit run app.py --server.port $PORT"
       healthCheckPath: "/_stcore/health"
       envVars:
         - key: PYTHON_VERSION
           value: 3.10.0
   ```

2. **Deploy on Render**:
   - Go to your Render dashboard and create a new "Web Service".
   - Connect your GitHub repository.
   - Render will automatically detect the `render.yaml` or you can configure it manually.
   - Click "Create Web Service".

Render will build and deploy your application.

---

### Configuration Notes

- **Tesseract Path**: In some deployment environments, you might need to explicitly tell `pytesseract` where the Tesseract executable is. This can be done via an environment variable.
- **Poppler Path**: Similarly, `pdf2image` may need the path to Poppler. Ensure it's in the system's PATH. The Dockerfile provided handles this for Debian-based systems.
