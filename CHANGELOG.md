# Changelog

## [1.1.0] - 2026-02-18

### Performance Improvements
- YOLO → ROI → OCR pipeline (ChatGPT recommendation)
- Bounding box padding for better OCR accuracy
- Preprocessing pipeline (CLAHE, denoising, thresholding)
- GPU acceleration option for EasyOCR
- Latency tracking (YOLO + OCR)

### New Features
- AI Assistant with conversational interface
- Context-aware responses
- Auto keyboard language detection
- Voice switching based on keyboard layout

### Architecture
- Modular OCR engine class
- Separated preprocessing pipeline
- Performance metrics export

### Fixed
- Voice engine language switching
- Text encoding issues
- Memory optimization

## [1.0.0] - 2026-02-17

Initial release with object detection, OCR, and voice assistance.
