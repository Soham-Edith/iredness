import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
import tempfile
import os
import base64
import io
import math
from inference_sdk import InferenceHTTPClient

class DigitalEyeFatigueAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Digital Eye Fatigue Analyzer")
        self.root.geometry("800x700")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize Roboflow client
        self.api_key = "hBljhOwZ15CdLgOj0Kjj"
        self.client = InferenceHTTPClient(
            api_url="https://serverless.roboflow.com",
            api_key=self.api_key
        )
        
        # Model IDs
        self.fatigue_model = "eyes-bhltc/1"
        self.dryness_model = "dry-eye-prediction/3"
        # Try different redness model IDs
        self.redness_models = [
            "redness-detect/1",
            "eye-redness-detection/1", 
            "red-eye-detection/1",
            "eyes-bhltc/1"  # Use same model as fatigue since it detects red_eyes
        ]
        
        # Variables
        self.current_image = None
        self.image_path = None
        
        self.setup_gui()
    
    def preprocess_image_pil(self, pil_image):
        """Preprocess PIL image: convert to BGR, apply CLAHE on L channel, return processed BGR array and base64 string"""
        try:
            # Convert PIL to numpy array (RGB)
            img_array = np.array(pil_image)
            
            # Convert RGB to BGR for OpenCV
            if len(img_array.shape) == 3:
                if img_array.shape[2] == 3:
                    bgr_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                elif img_array.shape[2] == 4:
                    # Handle RGBA
                    rgb_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
                    bgr_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
                else:
                    bgr_array = img_array
            else:
                # Grayscale, convert to BGR
                bgr_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
            
            # Convert BGR to LAB
            lab = cv2.cvtColor(bgr_array, cv2.COLOR_BGR2LAB)
            l_channel, a, b = cv2.split(lab)
            
            # Apply CLAHE on L channel
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l_channel = clahe.apply(l_channel)
            
            # Merge channels and convert back to BGR
            lab_processed = cv2.merge([l_channel, a, b])
            bgr_processed = cv2.cvtColor(lab_processed, cv2.COLOR_LAB2BGR)
            
            # Encode to JPEG base64
            success, buffer = cv2.imencode('.jpg', bgr_processed)
            if success:
                img_base64 = base64.b64encode(buffer).decode('utf-8')
                base64_string = f"data:image/jpeg;base64,{img_base64}"
            else:
                base64_string = None
            
            return bgr_processed, base64_string
        except Exception as e:
            print(f"Error in preprocess_image_pil: {e}")
            # Fallback: convert PIL to BGR without preprocessing
            img_array = np.array(pil_image)
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                bgr_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            else:
                bgr_array = img_array
            success, buffer = cv2.imencode('.jpg', bgr_array)
            base64_string = f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}" if success else None
            return bgr_array, base64_string
    
    def normalize_redness_score(self, raw_score):
        """Normalize redness score: reduce low scores (normal eyes) but preserve high scores (red eyes)"""
        if raw_score is None or raw_score == 0:
            return 0.0
        
        # Use a piecewise transformation that:
        # - Aggressively reduces low scores (normal eyes) -> 1-3/10 range
        # - Preserves high scores (red eyes) -> 7-10/10 range
        # - Smooth transition in the middle
        
        if raw_score < 0.2:
            # Very low scores (definitely normal eyes) - aggressive reduction
            # 0.0 -> 0.0, 0.1 -> 0.05, 0.2 -> 0.12
            calibrated = raw_score * 0.6
        elif raw_score < 0.4:
            # Low-medium scores (likely normal) - moderate reduction
            # 0.2 -> 0.12, 0.4 -> 0.25
            calibrated = 0.12 + (raw_score - 0.2) * 0.65
        elif raw_score < 0.6:
            # Medium scores - slight reduction, smooth transition
            # 0.4 -> 0.25, 0.6 -> 0.45
            calibrated = 0.25 + (raw_score - 0.4) * 1.0
        elif raw_score < 0.8:
            # Medium-high scores (likely redness) - preserve most value
            # 0.6 -> 0.45, 0.8 -> 0.75
            calibrated = 0.45 + (raw_score - 0.6) * 1.5
        else:
            # High scores (definitely red eyes) - preserve fully
            # 0.8 -> 0.75, 1.0 -> 1.0
            calibrated = 0.75 + (raw_score - 0.8) * 1.25
        
        # Clip to [0, 1]
        return max(0.0, min(1.0, calibrated))
    
    def normalize_and_calibrate(self, raw):
        """Normalize and calibrate raw score using piecewise function to preserve low values"""
        if raw is None:
            return 0.0
        try:
            # For normal eyes, we want to keep scores low even if API returns moderate values
            # Use piecewise normalization to handle different ranges appropriately
            if raw < 0.5:
                # For low-to-moderate values (likely normal eyes), apply reduction
                # This prevents normal eye scores from appearing too high
                # Scale down: 0.0->0.0, 0.3->0.2, 0.5->0.35
                calibrated = raw * 0.7  # Reduce by 30% to account for model sensitivity
            elif raw < 0.7:
                # For moderate-high values, use gentle sigmoid
                mean = 0.6
                scale = 0.2
                calibrated = 1.0 / (1.0 + math.exp(-(raw - mean) / scale))
                # Blend with linear to moderate the effect
                calibrated = calibrated * 0.5 + raw * 0.5
            else:
                # For high values, use sigmoid to ensure they're properly represented
                mean = 0.75
                scale = 0.15
                calibrated = 1.0 / (1.0 + math.exp(-(raw - mean) / scale))
            
            # Clip to [0, 1]
            return max(0.0, min(1.0, calibrated))
        except Exception as e:
            print(f"Error in normalize_and_calibrate: {e}")
            return 0.0
    
    def compute_final_fatigue(self, f_raw, r_raw, d_raw, screen_time_hours, condition):
        """Compute final fatigue score from normalized components (returns 1-10 scale)"""
        # Normalize and calibrate each component
        # Use specialized redness normalization to preserve high scores for red eyes
        f = self.normalize_and_calibrate(f_raw)
        r = self.normalize_redness_score(r_raw)  # Use specialized redness normalization
        d = self.normalize_and_calibrate(d_raw)
        
        # Time factor
        time_factor = min(screen_time_hours / 10.0, 1.0)
        
        # Condition multipliers
        condition_multipliers = {
            "Normal": 1.0,
            "Diabetic Retinopathy": 1.15,
            "Glaucoma": 1.10,
            "Cataract": 1.05
        }
        condition_multiplier = condition_multipliers.get(condition, 1.0)
        
        # Final calculation: 0.35*f + 0.25*r + 0.15*d + 0.25*time_factor
        final_raw = 0.35 * f + 0.25 * r + 0.15 * d + 0.25 * time_factor
        
        # Apply condition multiplier and clip
        final_0_1 = max(0.0, min(1.0, final_raw * condition_multiplier))
        
        # Convert to 1-10 scale
        f_10 = 1 + (f * 9)
        r_10 = 1 + (r * 9)
        d_10 = 1 + (d * 9)
        final_10 = 1 + (final_0_1 * 9)
        
        # Map to level / emoji / color using thresholds for 1-10 scale: <3.7 Low, <5.5 Moderate, else High
        if final_10 < 3.7:
            fatigue_level = "Low"
            emoji = "😊"
            color = "green"
        elif final_10 < 5.5:
            fatigue_level = "Moderate"
            emoji = "😐"
            color = "orange"
        else:
            fatigue_level = "High"
            emoji = "😰"
            color = "red"
        
        # Debug output
        print(f"DEBUG: Raw scores -> f={f_raw:.3f}, r={r_raw:.3f}, d={d_raw:.3f}")
        print(f"DEBUG: Calibrated (0-1) -> f={f:.3f}, r={r:.3f}, d={d:.3f}")
        print(f"DEBUG: Scores (1-10) -> f={f_10:.1f}, r={r_10:.1f}, d={d_10:.1f}")
        print(f"DEBUG: Time factor={time_factor:.3f}, Condition multiplier={condition_multiplier:.3f}")
        print(f"DEBUG: Final (0-1)={final_0_1:.3f}, Final (1-10)={final_10:.1f}, Level={fatigue_level}")
        
        return {
            'f_calibrated': round(f_10, 1),
            'r_calibrated': round(r_10, 1),
            'd_calibrated': round(d_10, 1),
            'time_factor': round(time_factor, 3),
            'final_fatigue': round(final_10, 1),
            'fatigue_level': fatigue_level,
            'emoji': emoji,
            'color': color
        }
        
    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Digital Eye Fatigue Analyzer", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Image section
        image_frame = ttk.LabelFrame(main_frame, text="Image Input", padding="10")
        image_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        image_frame.columnconfigure(1, weight=1)
        
        # Image display
        self.image_label = ttk.Label(image_frame, text="No image selected", 
                                   background='white', relief='sunken', anchor='center')
        self.image_label.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Image buttons
        ttk.Button(image_frame, text="Upload Image", 
                  command=self.upload_image).grid(row=1, column=0, padx=(0, 5))
        ttk.Button(image_frame, text="Capture from Webcam", 
                  command=self.capture_webcam).grid(row=1, column=1, padx=5)
        ttk.Button(image_frame, text="Clear Image", 
                  command=self.clear_image).grid(row=1, column=2, padx=(5, 0))
        
        # Input parameters section
        params_frame = ttk.LabelFrame(main_frame, text="Analysis Parameters", padding="10")
        params_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        params_frame.columnconfigure(1, weight=1)
        
        # Screen time input
        ttk.Label(params_frame, text="Screen Time (hours):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.screen_time_var = tk.StringVar(value="8")
        screen_time_entry = ttk.Entry(params_frame, textvariable=self.screen_time_var, width=10)
        screen_time_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Eye condition selection
        ttk.Label(params_frame, text="Eye Condition:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.condition_var = tk.StringVar(value="Normal")
        condition_combo = ttk.Combobox(params_frame, textvariable=self.condition_var, 
                                     values=["Normal", "Diabetic Retinopathy", "Glaucoma", "Cataract"],
                                     state="readonly", width=20)
        condition_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Analyze button
        analyze_button = ttk.Button(params_frame, text="Analyze Eye Fatigue", 
                                  command=self.start_analysis, style='Accent.TButton')
        analyze_button.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Analysis Results", padding="10")
        results_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Results text area
        self.results_text = scrolledtext.ScrolledText(results_frame, height=15, width=70, 
                                                    font=('Consolas', 10))
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
    def upload_image(self):
        """Upload image from file"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if file_path:
            self.load_image(file_path)
    
    def capture_webcam(self):
        """Capture image from webcam"""
        def capture():
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                messagebox.showerror("Error", "Could not open webcam")
                return
            
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Save temporarily
                temp_path = tempfile.mktemp(suffix='.jpg')
                cv2.imwrite(temp_path, frame)
                self.load_image(temp_path)
            else:
                messagebox.showerror("Error", "Failed to capture image")
        
        # Run in separate thread to avoid blocking GUI
        threading.Thread(target=capture, daemon=True).start()
    
    def load_image(self, image_path):
        """Load and display image"""
        try:
            # Load image
            image = Image.open(image_path)
            
            # Resize for display (max 400x300)
            display_image = image.copy()
            display_image.thumbnail((400, 300), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(display_image)
            
            # Update GUI
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo  # Keep a reference
            
            # Store original image path
            self.image_path = image_path
            self.current_image = image
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def clear_image(self):
        """Clear current image"""
        self.image_label.configure(image="", text="No image selected")
        self.image_label.image = None
        self.current_image = None
        self.image_path = None
    
    def start_analysis(self):
        """Start analysis in separate thread"""
        if not self.current_image:
            messagebox.showwarning("Warning", "Please select an image first")
            return
        
        try:
            screen_time = float(self.screen_time_var.get())
            if screen_time < 0:
                raise ValueError("Screen time must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid screen time (positive number)")
            return
        
        # Start progress bar
        self.progress.start()
        
        # Disable analyze button
        self.analyze_button = None
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.LabelFrame):
                        for grandchild in child.winfo_children():
                            if isinstance(grandchild, ttk.Button) and "Analyze" in str(grandchild.cget('text')):
                                self.analyze_button = grandchild
                                grandchild.configure(state='disabled')
                                break
        
        # Run analysis in separate thread
        threading.Thread(target=self.analyze_eye_fatigue, daemon=True).start()
    
    def analyze_eye_fatigue(self):
        """Analyze eye fatigue using Roboflow models"""
        processed_temp_path = None
        try:
            # Get parameters
            screen_time = float(self.screen_time_var.get())
            condition = self.condition_var.get()
            
            # Preprocess image
            print("Preprocessing image with CLAHE...")
            bgr_processed, processed_base64 = self.preprocess_image_pil(self.current_image)
            
            # Save processed image to temporary file (Roboflow client expects file path)
            processed_temp_path = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            processed_temp_path.close()
            cv2.imwrite(processed_temp_path.name, bgr_processed)
            processed_image_path = processed_temp_path.name
            
            # Run all three models using processed image
            results = {}
            api_success = False
            demo_mode = False
            
            # Fatigue detection
            try:
                fatigue_result = self.client.infer(processed_image_path, model_id=self.fatigue_model)
                fatigue_score = self.extract_confidence(fatigue_result, "fatigue")
                results['fatigue'] = fatigue_score
                if fatigue_score > 0:
                    api_success = True
            except Exception as e:
                print(f"Fatigue model error: {e}")
                results['fatigue'] = None
            
            # Dryness detection
            try:
                dryness_result = self.client.infer(processed_image_path, model_id=self.dryness_model)
                dryness_score = self.extract_confidence(dryness_result, "dryness")
                results['dryness'] = dryness_score
                if dryness_score > 0:
                    api_success = True
            except Exception as e:
                print(f"Dryness model error: {e}")
                results['dryness'] = None
            
            # Redness detection - try multiple models
            redness_score = None
            for i, redness_model in enumerate(self.redness_models):
                try:
                    print(f"Trying redness model {i+1}: {redness_model}")
                    redness_result = self.client.infer(processed_image_path, model_id=redness_model)
                    redness_score = self.extract_confidence(redness_result, "redness")
                    if redness_score > 0:
                        print(f"Redness model {redness_model} succeeded with score: {redness_score}")
                        results['redness'] = redness_score
                        api_success = True
                        break
                except Exception as e:
                    print(f"Redness model {redness_model} error: {e}")
                    continue
            
            if redness_score is None or redness_score == 0:
                results['redness'] = None
            
            # If some API calls failed, fill in missing data with demo values
            # Store raw demo values (compute_final_fatigue will normalize them)
            # Set demo_mode only if at least one model inference failed
            used_demo = False
            if results.get('fatigue') is None:
                # Use raw demo value (will be normalized in compute_final_fatigue)
                results['fatigue'] = 0.65
                used_demo = True
                print(f"Using demo fatigue (raw=0.65)")
            if results.get('redness') is None:
                # Use raw demo value (will be normalized in compute_final_fatigue)
                results['redness'] = 0.35
                used_demo = True
                print(f"Using demo redness (raw=0.35)")
            if results.get('dryness') is None:
                # Use raw demo value (will be normalized in compute_final_fatigue)
                results['dryness'] = 0.45
                used_demo = True
                print(f"Using demo dryness (raw=0.45)")
            
            demo_mode = used_demo
            if demo_mode:
                print("Demo mode enabled: at least one model inference failed, using demo data")
            
            # Get raw scores (API outputs or demo values, will be normalized in compute_final_fatigue)
            f_raw = results.get('fatigue', 0.0) if results.get('fatigue') is not None else 0.0
            r_raw = results.get('redness', 0.0) if results.get('redness') is not None else 0.0
            d_raw = results.get('dryness', 0.0) if results.get('dryness') is not None else 0.0
            
            # Compute final fatigue using new formula
            fatigue_result = self.compute_final_fatigue(f_raw, r_raw, d_raw, screen_time, condition)
            
            # Get recommendations using calibrated scores
            recommendations = self.generate_recommendations(
                fatigue_result['final_fatigue'],
                fatigue_result['r_calibrated'],
                fatigue_result['d_calibrated'],
                screen_time
            )
            
            # Update GUI with results
            self.root.after(0, self.display_results, {
                'fatigue_raw': round(f_raw, 3),
                'redness_raw': round(r_raw, 3),
                'dryness_raw': round(d_raw, 3),
                'fatigue_calibrated': fatigue_result['f_calibrated'],
                'redness_calibrated': fatigue_result['r_calibrated'],
                'dryness_calibrated': fatigue_result['d_calibrated'],
                'time_factor': fatigue_result['time_factor'],
                'final_fatigue': fatigue_result['final_fatigue'],
                'fatigue_level': fatigue_result['fatigue_level'],
                'emoji': fatigue_result['emoji'],
                'color': fatigue_result['color'],
                'recommendations': recommendations,
                'screen_time': screen_time,
                'condition': condition,
                'demo_mode': demo_mode
            })
            
        except Exception as e:
            self.root.after(0, self.show_error, f"Analysis failed: {str(e)}")
        finally:
            # Clean up temporary processed file
            if processed_temp_path and os.path.exists(processed_temp_path.name):
                try:
                    os.unlink(processed_temp_path.name)
                except Exception as e:
                    print(f"Warning: Could not delete temp file: {e}")
            # Stop progress bar and re-enable button
            self.root.after(0, self.analysis_complete)
    
    def extract_confidence(self, result, target_class):
        """Extract confidence score from Roboflow result"""
        try:
            print(f"Extracting confidence for {target_class}: {result}")
            
            if 'predictions' in result and result['predictions']:
                # Handle different prediction formats
                predictions = result['predictions']
                
                # Format 1: Dictionary with class names as keys
                if isinstance(predictions, dict):
                    for class_name, class_data in predictions.items():
                        if isinstance(class_data, dict) and 'confidence' in class_data:
                            confidence = class_data['confidence']
                            print(f"Found {class_name} with confidence: {confidence}")
                            # For fatigue, look for red_eyes or fatigue-related classes
                            if target_class.lower() == 'fatigue':
                                if 'red' in class_name.lower() or 'fatigue' in class_name.lower():
                                    return confidence
                            # For redness, look for red_eyes or redness-related classes
                            elif target_class.lower() == 'redness':
                                if 'red' in class_name.lower() or 'redness' in class_name.lower():
                                    return confidence
                            elif target_class.lower() in class_name.lower():
                                return confidence
                    # Return max confidence if no specific match
                    max_confidence = max([data.get('confidence', 0.0) for data in predictions.values() if isinstance(data, dict)], default=0.0)
                    print(f"Using max confidence from dict: {max_confidence}")
                    return max_confidence
                
                # Format 2: List of prediction objects
                elif isinstance(predictions, list):
                    for prediction in predictions:
                        print(f"Prediction: {prediction}")
                        if 'class' in prediction and target_class.lower() in prediction['class'].lower():
                            confidence = prediction.get('confidence', 0.0)
                            print(f"Found {target_class} with confidence: {confidence}")
                            return confidence
                        elif 'confidence' in prediction:
                            confidence = prediction['confidence']
                            print(f"Found general confidence: {confidence}")
                            return confidence
                    # If no specific class found, return the highest confidence
                    max_confidence = max([p.get('confidence', 0.0) for p in predictions if 'confidence' in p], default=0.0)
                    print(f"Using max confidence from list: {max_confidence}")
                    return max_confidence
                    
            elif 'confidence' in result:
                # Direct confidence in result
                confidence = result['confidence']
                print(f"Found direct confidence: {confidence}")
                return confidence
            return 0.0
        except Exception as e:
            print(f"Error extracting confidence: {e}")
            return 0.0
    
    def get_fatigue_level(self, score):
        """Get fatigue level based on score (1-10 scale, legacy method, compute_final_fatigue handles this now)"""
        if score < 3.7:
            return "Low", "😊", "green"
        elif score < 5.5:
            return "Moderate", "😐", "orange"
        else:
            return "High", "😰", "red"
    
    def generate_recommendations(self, final_score, redness_score, dryness_score, screen_time):
        """Generate recommendations based on analysis (scores in 1-10 scale)"""
        recommendations = []
        
        if final_score > 7.3:
            recommendations.append("🚨 HIGH FATIGUE DETECTED - Consider immediate rest")
        elif final_score > 5.5:
            recommendations.append("⚠️ Moderate fatigue detected - Take frequent breaks")
        
        if redness_score > 6.4:
            recommendations.append("👁️ Eye redness detected - Use lubricating eye drops")
        
        if dryness_score > 6.4:
            recommendations.append("💧 Dry eyes detected - Blink more frequently and use artificial tears")
        
        if screen_time > 8:
            recommendations.append("⏰ Reduce screen time - Follow 20-20-20 rule (every 20 minutes, look at something 20 feet away for 20 seconds)")
        elif screen_time > 6:
            recommendations.append("⏰ Consider taking more frequent breaks from screen work")
        
        if final_score < 3.7:
            recommendations.append("✅ Good eye health - Maintain current habits")
        
        # General recommendations
        recommendations.extend([
            "💡 Ensure proper lighting when using screens",
            "🪟 Take breaks to look at distant objects",
            "💧 Stay hydrated throughout the day",
            "😴 Get adequate sleep (7-9 hours)",
            "🥕 Eat foods rich in vitamin A and omega-3 fatty acids"
        ])
        
        return recommendations
    
    def display_results(self, results):
        """Display analysis results in the text area"""
        self.results_text.delete(1.0, tk.END)
        
        # Format results
        demo_note = "\n⚠️  DEMO MODE: API calls failed, using sample data for demonstration" if results.get('demo_mode', False) else ""
        
        output = f"""
╔══════════════════════════════════════════════════════════════╗
║                    EYE FATIGUE ANALYSIS RESULTS              ║
╚══════════════════════════════════════════════════════════════╝{demo_note}

📊 RAW SCORES (from API, 0-1 scale):
   • Fatigue (raw):        {results.get('fatigue_raw', 0.0):.3f}
   • Redness (raw):        {results.get('redness_raw', 0.0):.3f}
   • Dryness (raw):        {results.get('dryness_raw', 0.0):.3f}

📈 CALIBRATED COMPONENTS (1-10 scale):
   • Fatigue (calibrated): {results.get('fatigue_calibrated', 0.0):.1f}/10
   • Redness (calibrated): {results.get('redness_calibrated', 0.0):.1f}/10
   • Dryness (calibrated): {results.get('dryness_calibrated', 0.0):.1f}/10
   • Time Factor:          {results.get('time_factor', 0.0):.3f}

🎯 FINAL FATIGUE SCORE: {results['final_fatigue']:.1f}/10
   Level: {results['emoji']} {results['fatigue_level']}

📋 PARAMETERS:
   • Screen Time:          {results['screen_time']:.1f} hours
   • Eye Condition:        {results['condition']}

💡 RECOMMENDATIONS:
"""
        
        for i, rec in enumerate(results['recommendations'], 1):
            output += f"   {i:2d}. {rec}\n"
        
        output += f"\n{'='*60}\n"
        output += "Analysis completed successfully!\n"
        
        self.results_text.insert(1.0, output)
        self.results_text.see(1.0)  # Scroll to top
    
    def show_error(self, error_message):
        """Show error message"""
        messagebox.showerror("Analysis Error", error_message)
    
    def analysis_complete(self):
        """Called when analysis is complete"""
        self.progress.stop()
        if hasattr(self, 'analyze_button') and self.analyze_button:
            self.analyze_button.configure(state='normal')

def main():
    root = tk.Tk()
    app = DigitalEyeFatigueAnalyzer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
