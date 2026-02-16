"""
VECTOR VISION v1.0 - FIXED
Auto Keyboard Language + Voice Switching
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
# KEYBOARD LANGUAGE DETECTOR
# ============================================================================

class KeyboardLanguageDetector:
    LANGUAGES = {
        0x0409: 'en',
        0x0419: 'ru',
        0x0422: 'uk',
        0x0423: 'be',
        0x0407: 'de',
        0x040C: 'fr',
        0x040A: 'es',
        0x0410: 'it',
        0x0416: 'pt',
        0x0415: 'pl',
        0x0411: 'ja',
        0x0412: 'ko',
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
        self.start = time.time()
        self.detected = Counter()
    
    @property
    def duration(self):
        return time.time() - self.start
    
    @property
    def fps(self):
        return self.frames / self.duration if self.duration > 0 else 0
    
    def export(self):
        data = {
            "version": "1.0",
            "frames": self.frames,
            "objects": self.objects,
            "text_scans": self.text_scans,
            "duration": round(self.duration, 2),
            "avg_fps": round(self.fps, 2),
            "top_objects": dict(self.detected.most_common(10)),
            "timestamp": datetime.now().isoformat()
        }
        filename = f"metrics_{datetime.now().strftime('%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filename


# ============================================================================
# VOICE ENGINE - FIXED
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
            
            # Получаем все голоса
            all_voices = self.engine.getProperty('voices')
            
            # Ищем голоса по языкам
            for voice in all_voices:
                print(f"      Voice: {voice.name}")
                
                # Определяем язык голоса
                if hasattr(voice, 'languages') and voice.languages:
                    lang = voice.languages[0][:2].lower()
                elif 'russian' in voice.name.lower() or 'RU' in voice.id:
                    lang = 'ru'
                elif 'english' in voice.name.lower() or 'EN' in voice.id:
                    lang = 'en'
                elif 'german' in voice.name.lower() or 'DE' in voice.id:
                    lang = 'de'
                elif 'french' in voice.name.lower() or 'FR' in voice.id:
                    lang = 'fr'
                else:
                    lang = 'en'  # По умолчанию
                
                if lang not in self.voices:
                    self.voices[lang] = voice
                    print(f"      ✅ {lang}: {voice.name}")
            
            # Устанавливаем голос по умолчанию
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
        
        # Определяем язык клавиатуры
        if auto_language:
            kb_lang = KeyboardLanguageDetector.get_current_language()
            lang_name = KeyboardLanguageDetector.get_language_name(kb_lang)
            print(f"[KEYBOARD] {lang_name} ({kb_lang})")
            
            # Ищем голос для этого языка
            if kb_lang in self.voices:
                target_voice = self.voices[kb_lang]
                if target_voice.id != self.current_voice:
                    print(f"[VOICE] Switching to {lang_name} voice")
                    self.engine.setProperty('voice', target_voice.id)
                    self.current_voice = target_voice.id
            else:
                print(f"[VOICE] No voice for {lang_name}, using default")
        
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
        self.colors = self.config.COLORS  # ИСПРАВЛЕНИЕ!
        
        self.last_ocr = 0
        self.last_speak = 0
        self.ocr_text = ""
        self.show_ocr_until = 0
        
        self._init()
    
    def _init(self):
        print("\n" + "=" * 70)
        print("  VECTOR VISION v1.0 - AUTO LANGUAGE")
        print("=" * 70)
        print()
        
        # EasyOCR
        print("[1/4] Loading EasyOCR...")
        self.ocr_reader = easyocr.Reader(['ru', 'en'], gpu=False, verbose=False)
        print("      ✅ Ready")
        
        # YOLO
        print("[2/4] Loading YOLO...")
        self.model = YOLO("yolov8n.pt")
        print("      ✅ Ready")
        
        # Camera
        print("[3/4] Camera...")
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        if not self.cap.isOpened():
            raise RuntimeError("Camera not found!")
        print("      ✅ Ready")
        
        # Voice
        print("[4/4] Voice engine...")
        self.voice = VoiceEngine()
        
        # Keyboard
        kb_lang = KeyboardLanguageDetector.get_language_name(
            KeyboardLanguageDetector.get_current_language()
        )
        print(f"      Keyboard: {kb_lang}")
        
        print()
        print("=" * 70)
        print("  CONTROLS:")
        print("    Q/ESC - Exit")
        print("    T     - Read text")
        print("    S     - Speak (auto language)")
        print("    L     - Show language")
        print("    SPACE - Screenshot")
        print("    E     - Export")
        print("=" * 70)
        print()
    
    def _draw_ui(self, frame):
        h, w = frame.shape[:2]
        c = self.colors  # ИСПРАВЛЕНИЕ!
        
        # Top panel
        cv2.rectangle(frame, (0, 0), (w, 55), c['panel'], -1)
        frame = self.text_renderer.put_text(frame, "[*] VECTOR VISION v1.0", 
                                           (15, 18), c['primary'], "medium")
        
        # Keyboard language
        kb_lang = KeyboardLanguageDetector.get_language_name(
            KeyboardLanguageDetector.get_current_language()
        )
        frame = self.text_renderer.put_text(frame, f"LANG: {kb_lang}", 
                                           (w - 150, 18), c['cyan'], "small")
        
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
        stats_x = w - 200
        cv2.rectangle(frame, (stats_x, 180), (w-10, 310), c['panel'], -1)
        cv2.rectangle(frame, (stats_x, 180), (w-10, 310), (50, 50, 65), 1)
        frame = self.text_renderer.put_text(frame, "[INFO] STATS", 
                                           (stats_x+12, 205), c['yellow'], "medium")
        
        sy = 240
        frame = self.text_renderer.put_text(frame, f"Frames: {self.metrics.frames}", 
                                           (stats_x+12, sy), c['text_dim'], "small")
        frame = self.text_renderer.put_text(frame, f"Objects: {self.metrics.objects}", 
                                           (stats_x+12, sy+18), c['text_dim'], "small")
        frame = self.text_renderer.put_text(frame, f"Text: {self.metrics.text_scans}", 
                                           (stats_x+12, sy+36), c['text_dim'], "small")
        frame = self.text_renderer.put_text(frame, f"Time: {self.metrics.duration:.0f}s", 
                                           (stats_x+12, sy+54), c['text_dim'], "small")
        
        return frame
    
    def run(self):
        print("[RUN] Started\n")
        self.voice.speak("Vector Vision started")
        
        try:
            while True:
                self.metrics.frames += 1
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                current = time.time()
                
                # Detection
                results = self.model(frame, verbose=False)
                annotated = results[0].plot()
                
                for result in results:
                    for box in result.boxes:
                        if float(box.conf[0]) > 0.5:
                            name = result.names[int(box.cls[0])]
                            self.metrics.detected[name] += 1
                            self.metrics.objects += 1
                
                # Auto-speak
                if self.metrics.detected and current - self.last_speak > 20:
                    top = self.metrics.detected.most_common(1)[0][0]
                    self.voice.speak(f"Seeing {top}")
                    self.last_speak = current
                
                # T - OCR
                if keyboard.is_pressed('t') and current - self.last_ocr > 3:
                    print("[OCR] Reading...")
                    self.metrics.text_scans += 1
                    
                    ocr_results = self.ocr_reader.readtext(frame)
                    
                    if ocr_results:
                        texts = [t for (bbox, t, conf) in ocr_results if conf > 0.5 and len(t.strip()) > 1]
                        if texts:
                            self.ocr_text = ' '.join(texts[:5])
                            self.show_ocr_until = current + 10
                            print(f"[OCR] ✓ {self.ocr_text}")
                            self.voice.speak("Text detected")
                            
                            # Draw boxes - ИСПРАВЛЕНО!
                            for (bbox, text, conf) in ocr_results:
                                if conf > 0.5:
                                    pts = np.array(bbox, dtype=np.int32)
                                    cv2.polylines(annotated, [pts], True, self.colors['secondary'], 2)
                        else:
                            print("[OCR] No text")
                    else:
                        print("[OCR] No text detected")
                    
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
                cv2.imshow("Vector Vision v1.0", frame_with_ui)
                
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
        print(f"[DONE] Duration: {self.metrics.duration:.0f}s")


if __name__ == "__main__":
    try:
        app = VectorVision()
        app.run()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")