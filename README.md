![Python Version](https://img.shields.io/badge/Python-3.6%2B-brightgreen)
# OCR Tool

## Overview
This is a Tkinter-based OCR (Optical Character Recognition) tool that allows users to extract text from images using Tesseract OCR. The application provides various image preprocessing options, including binarization and cropping, to improve OCR accuracy.

## Features
- Load and preprocess images before performing OCR.
- Apply cropping and binarization to enhance text extraction.
- Automatic binarization using the Otsu method.
- Extract text using Tesseract's different Page Segmentation Modes.
- Export extracted text as .txt or JSON.
- User-friendly GUI built with Tkinter.

## Requirements
- Python 3.7+
- Tesseract
- OpenCV
- Tkinter (built-in with Python)
- PIL (Pillow)

## Installation
### 1. Install Python
Ensure you have Python 3.7 or higher installed. You can download it from:
[https://www.python.org/downloads/](https://www.python.org/downloads/)

### 2. Install Tesseract OCR
#### Windows:
1. **Download Tesseract**:
   - Go to the [Tesseract OCR Installation page](https://github.com/UB-Mannheim/tesseract/wiki).
   - Download the latest stable version for Windows.
   
2. **Run the Installer**:
   - Launch the downloaded `.exe` file to start installation.
   - By default, Tesseract is installed in: C:\Program Files\Tesseract-OCR
   - During installation, select **Dutch (Flemish)** under additional language options.

3. **Add Tesseract OCR to path**:
   1. **Open Environment Variables**:  
      - Press `Win + S` and search for "Environment Variables."  
      - Select **Edit the system environment variables**.  

   2. **Edit PATH Variable**:  
      - In the **System Properties** window, click **Environment Variables**.  
      - Under **System variables**, find the `Path` variable, select it, and click **Edit**.  

   3. **Add Tesseract Path**:  
      - Click **New** and add the path to the Tesseract executable:  
      `C:\Program Files\Tesseract-OCR`  

   4. **Verify the PATH**:  
      - Open a new Command Prompt and type:  
         ```bash
         tesseract --version
         ```  
      - If the version information is displayed, Tesseract is successfully added to your PATH.

#### MacOS:

#### Install Homebrew (if not already installed):
1. Open the Terminal and run:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Follow the on-screen instructions to complete the installation.

#### Verify Homebrew installation:
```bash
brew --version
```

#### Install Tesseract using Homebrew:
```bash
brew install tesseract-lang
```
### 3. Install Python Dependencies
```sh
pip install opencv-python pillow pytesseract
```

## Usage
1. Run the script:
```sh
python ocr_tool_1.3.py
```
2. Use the GUI to:
   - Load images.
   - Apply preprocessing (cropping, binarization, etc.).
   - Extract text using Tesseract.
   - Export results as JSON.

## Troubleshooting
- If Tesseract is not found, ensure it is correctly installed and added to the system PATH.
- For improved accuracy, adjust image preprocessing options before performing OCR.

