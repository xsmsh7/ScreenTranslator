# Screen Translator

A powerful real-time screen translation tool that captures text from your screen and displays translated overlays. Built with Python, PyQt6, and Tesseract OCR.

![Screen Translator](debug_capture.png)

## Features

- **Real-time Screen Capture**: Select any area of your screen to capture text.
- **OCR Integration**: Uses Tesseract to recognize text from images.
- **AI Translation**: Supports translation using:
  - OpenAI GPT-3.5
  - Deep Translator (Google Translate)
- **Visual Overlay**: Displays translated text directly over the original content.

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ScreenTranslator
   ```

2. **Set up a virtual environment** (Optional but recommended):
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR**:
   - Download and install Tesseract from [here](https://github.com/UB-Mannheim/tesseract/wiki).
   - Ensure the `tesseract` executable is in your system PATH or configured in `utils.py`.

## Usage

1. Run the application:
   ```bash
   python main.py
   ```
2. Click "Capture" to select a screen area.
3. View the translation in the overlay window.

## Configuration

Creates a `.env` file in the root directory if you plan to use OpenAI:
```
OPENAI_API_KEY=your_api_key_here
```

## Contributing

1. Fork the project.
2. Create your feature branch (`git checkout -b feat/amazing-feature`).
3. Commit your changes (`git commit -m 'feat: add some amazing feature'`).
4. Push to the branch (`git push origin feat/amazing-feature`).
5. Open a Pull Request.
