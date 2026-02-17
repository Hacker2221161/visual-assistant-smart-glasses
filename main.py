"""
================================================================================
  VECTOR VISION v1.1.0 - PRODUCTION READY
  Smart Glasses Computer Vision System
  
  Version System:
    - 1st digit: Code version (1 = stable)
    - 2nd digit: Documentation version (1 = complete)
    - 3rd digit: AI version (0 = basic assistant)
  
  Improvements:
    - YOLO → ROI → OCR pipeline (faster, more accurate)
    - Preprocessing pipeline (CLAHE, denoising)
    - Bounding box padding
    - GPU acceleration option
    - AI Assistant integration
  
  Licensed under the Apache License, Version 2.0
================================================================================
"""

import cv2
import numpy as np
from ultralytics import YOLO
import keyboard
import pyttsx3
import easyocr
from datetime import datetime
from collections import Counter
from PIL import Image, ImageDraw, ImageFont
import time
import threading
import json
import ctypes


# ============================================================================
# VERSION INFO
# ============================================================================

VERSION = "1.1.0"
VERSION_NAME = "Production Ready"
VERSION_DATE = "2026-02-18"


# ============================================================================
# AI ASSISTANT
# ============================================================================

class AIAssistant:
    """AI Assistant for conversational help"""
    
    def __init__(self):
        self.context = {
            "objects_seen": [],
            "text_read": [],
            "session_start": time.time()
        }
        
        self.responses = {
            "привет": "Привет! Я Vector Vision - умные очки с компьютерным зрением",
            "hello": "Hello! I'm Vector Vision - smart glasses with computer vision",
            "что ты умеешь": "Я умею: распознавать объекты, читать текст, говорить что вижу",
            "what can you do": "I can: detect objects, read text, and describe what I see",
            "версия": f"Версия Vector Vision {VERSION}",
            "version": f"Vector Vision version {VERSION}",
            "помощь": "Нажми: T - читать текст, S - сказать что вижу, A - спросить AI, H - помощь",
            "help": "Press: T - read text, S - speak, A - ask AI, H - help",
        }
    
    def add_context(self, obj_type, data):
        if obj_type == "object":
            self.context["objects_seen"].append(data)
        elif obj_type == "text":
            self.context["text_read"].append(data)
    
    def respond(self, query):
        query = query.lower().strip()
        
        for key, response in self.responses.items():
            if key in query:
                return response
        
        if "вижу" in query or "see" in query:
            if self.context["objects_seen"]:
                recent = self.context["objects_seen"][-5:]
                return f"За сессию я видел: {', '.join(set(recent))}"
            return "Пока ничего не видел"
        
        if "читал" in query or "read" in query:
            if self.context["text_read"]:
                recent = self.context["text_read"][-3:]
                return f"Я читал: {'; '.join(recent)}"
            return "Пока ничего не читал"
        
        return "Я не совсем понял. Попробуй: 'помощь' или 'help'"


# ============================================================================
# OCR ENGINE - IMPROVED WITH ROI
# ============================================================================

class OCREngine:
    """OCR with ROI preprocessing (ChatGPT recommendation)"""
    
    def __init__(self, languages=['ru', 'en'], use_gpu=False):
        self.reader = easyocr.Reader(languages, gpu=use_gpu, verbose=False)
        self.use_gpu = use_gpu
        print(f"      ✅ EasyOCR ready (GPU: {use_gpu})")
    
    def preprocess_roi(self, roi):
        """Preprocessing pipeline for better OCR accuracy"""
        # Convert to grayscale
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        
        # Denoising
        gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Resize for better accuracy
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        
        # Thresholding
        _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return gray
    
    def read_text_full_frame(self, frame):
        """Read text from entire frame (old method - slower)"""
        results = self.reader.readtext(frame)
        return [(bbox, text, conf) for (bbox, text, conf) in results if conf > 0.5]
    
    def read_text_roi(self, frame, bbox, padding=20):
        """Read text from ROI with preprocessing (new method - faster & accurate)"""
        x1, y1, x2, y2 = map(int, bbox)
        
        # Add padding
        h, w = frame.shape[:2]
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(w, x2 + padding)
        y2 = min(h, y2 + padding)
        
        # Extract ROI
        roi = frame[y1:y2, x1:x2]
        
        if roi.size == 0:
            return []
        
        # Preprocess
        processed = self.preprocess_roi(roi)
        
        # OCR
        results = self.reader.readtext(processed)
        
        # Adjust coordinates back to original frame
        adjusted_results = []
        for (bbox_roi, text, conf) in results:
            if conf > 0.5:
                # Adjust bbox coordinates
                adjusted_bbox = [[pt[0] + x1, pt[1] + y1] for pt in bbox_roi]
                adjusted_results.append((adjusted_bbox, text, conf))
        
        return adjusted_results


# ============================================================================
# KEYBOARD LANGUAGE DETECTOR
# ============================================================================

class KeyboardLanguageDetector:
    LANGUAGES = {
        0x0409: 'en', 0x0419: 'ru', 0x0422: 'uk', 0x0423: 'be',
        0x0407: 'de', 0x040C: 'fr', 0x040A: 'es', 0x0410: 'it',
        0x0416: 'pt', 0x0415: 'pl', 0x0411: 'ja', 0x0412: 'ko',
        0x0804: 'zh',
    }
    
    @staticmethod
    def get_current_language():
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            threadid = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, 0)
            layout_id = ctypes.windll.user32.GetKeyboardLayout(threadid) & 0xFFFF
            return KeyboardLanguageDetector.LANGUAGES.get(layout_id, 'en')
        except:
            return 'en'
    
    @staticmethod
    def get_language_name(lang_code):
        names = {
            'en': 'English', 'ru': 'Russian', 'uk': 'Ukrainian',
            'be': 'Belarusian', 'de': 'German', 'fr': 'French',
            'es': 'Spanish', 'it': 'Italian', 'pt': 'Portuguese',
            'pl': 'Polish', 'ja': 'Japanese', 'ko': 'Korean', 'zh': 'Chinese',
        }
        return names.get(lang_code, lang_code)


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    USE_GPU = False  # Set to True if you have NVIDIA GPU
    CONFIDENCE_THRESHOLD = 0.5
    OCR_PADDING = 20
    OCR_COOLDOWN = 3.0
    OCR_DISPLAY_DURATION = 10.0
    AUTO_SPEAK_INTERVAL = 20.0
    
    COLORS = {
        'primary': (100, 255, 150),
        'secondary': (255, 0, 255),
        'panel': (30, 30, 45),
        'text': (240, 240, 240),
        'text_dim': (180, 180, 180),
        'success': (100, 255, 150),
        'warning': (100, 200, 255),
        'error': (100, 100, 255),
        'cyan': (255, 255, 100),
        'yellow': (100, 255, 255),
    }


# ============================================================================
# TEXT RENDERER
# ============================================================================

class TextRenderer:
    def __init__(self):
        self._load_fonts()
    
    def _load_fonts(self):
        try:
            self.font_small = ImageFont.truetype("arial.ttf", 16)
            self.font_medium = ImageFont.truetype("arial.ttf", 20)
            self.font_large = ImageFont.truetype("arial.ttf", 24)
        except:
            self.font_small = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_large = ImageFont.load_default()
    
    def put_text(self, img, text, pos, color=(255, 255, 255), font_size="medium"):
        font = {"small": self.font_small, "medium": self.font_medium, "large": self.font_large}.get(font_size, self.font_medium)
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        draw.text(pos, text, font=font, fill=tuple(color))
        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


# ============================================================================
# METRICS
# ============================================================================

class SessionMetrics:
    def __init__(self):
        self.frames = 0
        self.objects = 0
        self.text_scans = 0
        self.screenshots = 0
        self.ai_queries = 0
        self.ocr_latency = []
        self.yolo_latency = []
        self.start = time.time()
        self.detected = Counter()
    
    @property
    def duration(self):
        return time.time() - self.start
    
    @property
    def fps(self):
        return self.frames / self.duration if self.duration > 0 else 0
    
    @property
    def avg_ocr_latency(self):
        return sum(self.ocr_latency) / len(self.ocr_latency) if self.ocr_latency else 0
    
    @property
    def avg_yolo_latency(self):
        return sum(self.yolo_latency) / len(self.yolo_latency) if self.yolo_latency else 0
    
    def export(self):
        data = {
            "version": f"v{VERSION} - {VERSION_NAME}",
            "frames": self.frames,
            "objects": self.objects,
            "text_scans": self.text_scans,
            "screenshots": self.screenshots,
            "ai_queries": self.ai_queries,
            "duration": round(self.duration, 2),
            "avg_fps": round(self.fps, 2),
            "avg_ocr_latency_ms": round(self.avg_ocr_latency * 1000, 2),
            "avg_yolo_latency_ms": round(self.avg_yolo_latency * 1000, 2),
            "top_objects": dict(self.detected.most_common(10)),
            "timestamp": datetime.now().isoformat()
        }
        filename = f"metrics_{datetime.now().strftime('%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filename


# ============================================================================
# VOICE ENGINE
# ============================================================================

class VoiceEngine:
    def __init__(self):
        self.engine = None
        self.voices = {}
        self.current_voice = None
        
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 130)
            self.engine.setProperty('volume', 0.85)
            
            all_voices = self.engine.getProperty('voices')
            
            for voice in all_voices:
                if hasattr(voice, 'languages') and voice.languages:
                    lang = voice.languages[0][:2].lower()
                elif 'russian' in voice.name.lower() or 'RU' in voice.id:
                    lang = 'ru'
                elif 'english' in voice.name.lower() or 'EN' in voice.id:
                    lang = 'en'
                else:
                    lang = 'en'
                
                if lang not in self.voices:
                    self.voices[lang] = voice
            
            if all_voices:
                self.engine.setProperty('voice', all_voices[0].id)
                self.current_voice = all_voices[0].id
            
            print("[OK] Voice engine ready")
            print(f"      Available: {', '.join(self.voices.keys())}")
            
        except Exception as e:
            print(f"[WARN] Voice disabled: {e}")
            self.engine = None
    
    def speak(self, text, auto_language=True):
        if not self.engine:
            print(f"[VOICE] {text}")
            return
        
        if auto_language:
            kb_lang = KeyboardLanguageDetector.get_current_language()
            lang_name = KeyboardLanguageDetector.get_language_name(kb_lang)
            print(f"[KEYBOARD] {lang_name} ({kb_lang})")
            
            if kb_lang in self.voices:
                target_voice = self.voices[kb_lang]
                if target_voice.id != self.current_voice:
                    print(f"[VOICE] Switching to {lang_name}")
                    self.engine.setProperty('voice', target_voice.id)
                    self.current_voice = target_voice.id
        
        def _say():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"[VOICE] Error: {e}")
        
        threading.Thread(target=_say, daemon=True).start()


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class VectorVision:
    def __init__(self):
        self.config = Config()
        self.metrics = SessionMetrics()
        self.text_renderer = TextRenderer()
        self.colors = self.config.COLORS
        
        self.last_ocr = 0
        self.last_speak = 0
        self.ocr_text = ""
        self.show_ocr_until = 0
        self.ocr_results = []
        
        # AI Assistant
        self.ai = AIAssistant()
        
        self._init()
    
    def _init(self):
        print("\n" + "=" * 70)
        print(f"  VECTOR VISION v{VERSION} - {VERSION_NAME}")
        print(f"  Smart Glasses with AI Assistant")
        print("=" * 70)
        print()
        
        # EasyOCR with ROI
        print("[1/5] Loading EasyOCR (ROI mode)...")
        self.ocr = OCREngine(languages=['ru', 'en'], use_gpu=self.config.USE_GPU)
        
        # YOLO
        print("[2/5] Loading YOLO...")
        self.model = YOLO("yolov8n.pt")
        print("      ✅ Ready")
        
        # Camera
        print("[3/5] Camera...")
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        if not self.cap.isOpened():
            raise RuntimeError("Camera not found!")
        print("      ✅ Ready")
        
        # Voice
        print("[4/5] Voice engine...")
        self.voice = VoiceEngine()
        
        # AI Assistant
        print("[5/5] AI Assistant...")
        print("      ✅ Ready")
        
        kb_lang = KeyboardLanguageDetector.get_language_name(
            KeyboardLanguageDetector.get_current_language()
        )
        print(f"      Keyboard: {kb_lang}")
        
        print()
        print("=" * 70)
        print("  CONTROLS:")
        print("    Q/ESC - Exit")
        print("    T     - Read text (ROI mode - faster!)")
        print("    S     - Speak (auto language)")
        print("    A     - Ask AI Assistant")
        print("    H     - Help")
        print("    L     - Show language")
        print("    SPACE - Screenshot")
        print("    E     - Export metrics")
        print("=" * 70)
        print()
    
    def _draw_ui(self, frame):
        h, w = frame.shape[:2]
        c = self.colors
        
        # Top panel
        cv2.rectangle(frame, (0, 0), (w, 55), c['panel'], -1)
        frame = self.text_renderer.put_text(frame, f"[*] VECTOR VISION v{VERSION}", 
                                           (15, 18), c['primary'], "medium")
        
        # Keyboard language
        kb_lang = KeyboardLanguageDetector.get_language_name(
            KeyboardLanguageDetector.get_current_language()
        )
        frame = self.text_renderer.put_text(frame, f"🌐 {kb_lang}", 
                                           (w - 180, 18), c['cyan'], "small")
        
        # Time
        frame = self.text_renderer.put_text(frame, datetime.now().strftime("%H:%M:%S"), 
                                           (w - 110, 38), c['text_dim'], "small")
        
        # Bottom panel
        cv2.rectangle(frame, (0, h-45), (w, h), c['panel'], -1)
        cv2.circle(frame, (18, h-22), 6, c['success'], -1)
        
        # Objects
        if self.metrics.detected:
            top = self.metrics.detected.most_common(3)
            obj_text = "  ".join([f"{obj}:{cnt}" for obj, cnt in top])
            frame = self.text_renderer.put_text(frame, obj_text[:60], 
                                               (35, h-22), c['cyan'], "small")
        
        # FPS
        fps = self.metrics.fps
        fps_color = c['success'] if fps > 15 else c['warning'] if fps > 10 else c['error']
        frame = self.text_renderer.put_text(frame, f"FPS: {fps:.0f}", 
                                           (w - 100, h-22), fps_color, "small")
        
        # OCR Panel
        if time.time() < self.show_ocr_until and self.ocr_text:
            panel_x = w - 360
            cv2.rectangle(frame, (panel_x, 65), (w-10, 145), c['panel'], -1)
            cv2.rectangle(frame, (panel_x, 65), (w-10, 145), c['secondary'], 2)
            frame = self.text_renderer.put_text(frame, "[TEXT] DETECTED", 
                                               (panel_x+15, 88), c['secondary'], "medium")
            frame = self.text_renderer.put_text(frame, self.ocr_text[:50], 
                                               (panel_x+15, 115), c['text'], "small")
        
        # Stats
        stats_x = w - 220
        cv2.rectangle(frame, (stats_x, 190), (w-10, 370), c['panel'], -1)
        cv2.rectangle(frame, (stats_x, 190), (w-10, 370), (50, 50, 65), 1)
        frame = self.text_renderer.put_text(frame, "[INFO] STATS", 
                                           (stats_x+12, 215), c['yellow'], "medium")
        
        sy = 250
        frame = self.text_renderer.put_text(frame, f"Frames: {self.metrics.frames}", 
                                           (stats_x+12, sy), c['text_dim'], "small")
        frame = self.text_renderer.put_text(frame, f"Objects: {self.metrics.objects}", 
                                           (stats_x+12, sy+18), c['text_dim'], "small")
        frame = self.text_renderer.put_text(frame, f"Text: {self.metrics.text_scans}", 
                                           (stats_x+12, sy+36), c['text_dim'], "small")
        frame = self.text_renderer.put_text(frame, f"AI queries: {self.metrics.ai_queries}", 
                                           (stats_x+12, sy+54), c['cyan'], "small")
        frame = self.text_renderer.put_text(frame, f"YOLO: {self.metrics.avg_yolo_latency*1000:.0f}ms", 
                                           (stats_x+12, sy+72), c['text_dim'], "small")
        frame = self.text_renderer.put_text(frame, f"OCR: {self.metrics.avg_ocr_latency*1000:.0f}ms", 
                                           (stats_x+12, sy+90), c['text_dim'], "small")
        frame = self.text_renderer.put_text(frame, f"Time: {self.metrics.duration:.0f}s", 
                                           (stats_x+12, sy+108), c['text_dim'], "small")
        
        return frame
    
    def run(self):
        print("[RUN] Started\n")
        self.voice.speak("Vector Vision started. AI assistant ready")
        
        try:
            while True:
                self.metrics.frames += 1
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                current = time.time()
                
                # YOLO Detection
                yolo_start = time.time()
                results = self.model(frame, verbose=False)
                self.metrics.yolo_latency.append(time.time() - yolo_start)
                
                annotated = results[0].plot()
                
                # Process objects
                text_objects = []  # Objects that might have text
                for result in results:
                    for box in result.boxes:
                        conf = float(box.conf[0])
                        if conf >= self.config.CONFIDENCE_THRESHOLD:
                            name = result.names[int(box.cls[0])]
                            self.metrics.detected[name] += 1
                            self.metrics.objects += 1
                            self.ai.add_context("object", name)
                            
                            # Track objects that might have text
                            if name in ['bottle', 'book', 'cell phone', 'laptop', 'cup']:
                                text_objects.append(box)
                
                # Auto-speak
                if self.metrics.detected and current - self.last_speak > self.config.AUTO_SPEAK_INTERVAL:
                    top = self.metrics.detected.most_common(1)[0][0]
                    self.voice.speak(f"Seeing {top}")
                    self.last_speak = current
                
                # T - OCR with ROI (IMPROVED!)
                if keyboard.is_pressed('t') and current - self.last_ocr > self.config.OCR_COOLDOWN:
                    print("[OCR] Reading with ROI mode...")
                    self.metrics.text_scans += 1
                    
                    ocr_start = time.time()
                    
                    # If we detected text objects, use ROI
                    if text_objects:
                        print(f"      Found {len(text_objects)} potential text objects")
                        all_texts = []
                        self.ocr_results = []
                        
                        for box in text_objects:
                            bbox = box.xyxy[0].cpu().numpy()
                            results = self.ocr.read_text_roi(frame, bbox, self.config.OCR_PADDING)
                            
                            for (bbox_roi, text, conf) in results:
                                all_texts.append(text)
                                self.ocr_results.append((bbox_roi, text, conf))
                                self.ai.add_context("text", text)
                        
                        if all_texts:
                            self.ocr_text = ' '.join(all_texts[:5])
                            self.show_ocr_until = current + self.config.OCR_DISPLAY_DURATION
                            print(f"[OCR] ✓ {self.ocr_text}")
                            self.voice.speak("Text detected")
                            
                            # Draw boxes
                            for (bbox, text, conf) in self.ocr_results:
                                pts = np.array(bbox, dtype=np.int32)
                                cv2.polylines(annotated, [pts], True, self.colors['secondary'], 2)
                        else:
                            print("[OCR] No text in ROI")
                    else:
                        # Fallback to full frame
                        print("      No text objects detected, using full frame")
                        results = self.ocr.read_text_full_frame(frame)
                        
                        if results:
                            texts = [t for (bbox, t, conf) in results if conf > 0.5]
                            if texts:
                                self.ocr_text = ' '.join(texts[:5])
                                self.show_ocr_until = current + self.config.OCR_DISPLAY_DURATION
                                print(f"[OCR] ✓ {self.ocr_text}")
                                self.voice.speak("Text detected")
                        else:
                            print("[OCR] No text detected")
                    
                    self.metrics.ocr_latency.append(time.time() - ocr_start)
                    self.last_ocr = current
                
                # S - Speak
                if keyboard.is_pressed('s'):
                    if self.ocr_text:
                        self.voice.speak(self.ocr_text)
                    else:
                        top = self.metrics.detected.most_common(2)
                        if top:
                            self.voice.speak(f"Seeing {', '.join([o for o, _ in top])}")
                        else:
                            self.voice.speak("Nothing detected")
                
                # A - Ask AI
                if keyboard.is_pressed('a'):
                    print("\n[AI] Ask me anything (or 'exit' to quit):")
                    try:
                        question = input("You: ").strip()
                        if question.lower() not in ['exit', 'quit', 'q']:
                            self.metrics.ai_queries += 1
                            response = self.ai.respond(question)
                            print(f"[AI] {response}")
                            self.voice.speak(response)
                    except:
                        pass
                    time.sleep(0.5)
                
                # H - Help
                if keyboard.is_pressed('h'):
                    help_text = "T-read text, S-speak, A-AI, H-help, L-language, SPACE-screenshot, E-export"
                    print(f"\n[HELP] {help_text}")
                    self.voice.speak("Help displayed")
                    time.sleep(0.5)
                
                # L - Language
                if keyboard.is_pressed('l'):
                    kb_lang = KeyboardLanguageDetector.get_language_name(
                        KeyboardLanguageDetector.get_current_language()
                    )
                    print(f"\n[KEYBOARD] {kb_lang}")
                    self.voice.speak(f"Language is {kb_lang}", auto_language=False)
                    time.sleep(0.5)
                
                # SPACE - Screenshot
                if keyboard.is_pressed('space'):
                    name = f"shot_{datetime.now().strftime('%H%M%S')}.jpg"
                    cv2.imwrite(name, annotated)
                    self.metrics.screenshots += 1
                    print(f"[SHOT] {name}")
                    self.voice.speak("Screenshot saved")
                
                # E - Export
                if keyboard.is_pressed('e'):
                    filename = self.metrics.export()
                    print(f"[EXPORT] {filename}")
                    self.voice.speak("Metrics exported")
                
                # UI
                frame_with_ui = self._draw_ui(annotated)
                cv2.imshow("Vector Vision v1.1.0", frame_with_ui)
                
                # Exit
                if keyboard.is_pressed('q') or cv2.waitKey(1) & 0xFF == 27:
                    break
        
        except KeyboardInterrupt:
            print("\n[INFO] Interrupted")
        finally:
            self._cleanup()
    
    def _cleanup(self):
        print("\n[SHUTDOWN]")
        self.metrics.export()
        self.cap.release()
        cv2.destroyAllWindows()
        self.voice.speak("Goodbye")
        print(f"[DONE] Frames: {self.metrics.frames}")
        print(f"[DONE] Objects: {self.metrics.objects}")
        print(f"[DONE] AI queries: {self.metrics.ai_queries}")
        print(f"[DONE] Duration: {self.metrics.duration:.0f}s")
        print(f"[DONE] Avg YOLO latency: {self.metrics.avg_yolo_latency*1000:.0f}ms")
        print(f"[DONE] Avg OCR latency: {self.metrics.avg_ocr_latency*1000:.0f}ms")


if __name__ == "__main__":
    try:
        app = VectorVision()
        app.run()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")