# Digital Eye Fatigue Analyzer - Web Application

A modern web application for analyzing eye fatigue using AI and computer vision models from Roboflow.

## 🌟 Features

### Frontend (HTML/CSS/JavaScript)
- **Modern Responsive UI**: Beautiful gradient design with smooth animations
- **Image Upload**: Drag & drop or click to upload images
- **Camera Capture**: Real-time webcam capture functionality
- **Interactive Parameters**: Screen time and eye condition inputs
- **Real-time Results**: Dynamic score display with visual indicators
- **Download Reports**: Export analysis results as JSON

### Backend (Flask)
- **RESTful API**: Clean API endpoints for image analysis
- **Roboflow Integration**: Multiple AI models for comprehensive analysis
- **Error Handling**: Graceful fallback to demo data when models fail
- **Base64 Image Processing**: Efficient image handling and processing

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Access the Web App
Open your browser and go to: `http://localhost:5000`

## 📁 Project Structure

```
POO/
├── app.py                          # Flask backend
├── requirements.txt                # Python dependencies
├── templates/
│   └── index.html                  # Main HTML template
├── static/
│   ├── style.css                  # CSS styling
│   └── script.js                  # JavaScript functionality
├── digital_eye_fatigue_analyzer_api.py  # Original Tkinter app
└── README_WEB.md                  # This file
```

## 🎯 How to Use

1. **Upload Image**: 
   - Drag & drop an image onto the upload area
   - Or click "Choose Image" to browse files
   - Or click "Capture from Camera" for webcam

2. **Set Parameters**:
   - Enter screen time in hours
   - Select eye condition (Normal, Diabetic Retinopathy, Glaucoma, Cataract)

3. **Analyze**: Click "Analyze Eye Fatigue" button

4. **View Results**:
   - See detailed scores for redness, dryness, and fatigue
   - Get personalized recommendations
   - Download analysis report

## 🔧 API Endpoints

### POST /analyze
Analyzes an eye image for fatigue.

**Request Body:**
```json
{
    "image": "data:image/jpeg;base64,/9j/4AAQ...",
    "screen_time": 8.0,
    "condition": "Normal"
}
```

**Response:**
```json
{
    "success": true,
    "fatigue_score": 0.967,
    "redness_score": 0.350,
    "dryness_score": 0.801,
    "final_fatigue": 0.575,
    "fatigue_level": "Moderate",
    "emoji": "😕",
    "color": "orange",
    "recommendations": ["...", "..."],
    "demo_mode": false
}
```

## 🎨 UI Features

### Responsive Design
- **Mobile-first**: Optimized for all screen sizes
- **Touch-friendly**: Easy to use on tablets and phones
- **Modern animations**: Smooth transitions and hover effects

### Visual Indicators
- **Score Cards**: Color-coded score displays
- **Fatigue Level**: Emoji and text indicators
- **Progress Bars**: Loading animations
- **Notifications**: Success/error messages

### Interactive Elements
- **Drag & Drop**: Intuitive image upload
- **Camera Integration**: Real-time photo capture
- **Dynamic Forms**: Real-time validation
- **Smooth Scrolling**: Enhanced user experience

## 🔬 Analysis Algorithm

The application uses the same sophisticated algorithm as the desktop version:

```
FinalFatigue = (0.5 × fatigue_score + 0.2 × redness_score + 0.1 × dryness_score + 0.2 × time_factor) × condition_multiplier
```

Where:
- `time_factor = min(screen_time / 10, 1.0)`
- `condition_multiplier` varies by eye condition

## 🌐 Browser Compatibility

- **Chrome**: 90+ ✅
- **Firefox**: 88+ ✅
- **Safari**: 14+ ✅
- **Edge**: 90+ ✅

## 📱 Mobile Support

- **iOS Safari**: 14+ ✅
- **Chrome Mobile**: 90+ ✅
- **Samsung Internet**: 13+ ✅

## 🛠️ Development

### Running in Development Mode
```bash
export FLASK_ENV=development
python app.py
```

### Customizing the UI
- Edit `static/style.css` for styling changes
- Modify `templates/index.html` for layout changes
- Update `static/script.js` for functionality changes

## 🔒 Security Notes

- Images are processed in memory and not stored
- API keys are embedded (consider environment variables for production)
- No user data is persisted

## 📊 Performance

- **Image Processing**: Optimized for speed
- **API Calls**: Asynchronous with fallback
- **UI Responsiveness**: Smooth 60fps animations
- **Memory Usage**: Efficient image handling

## 🎉 Features Comparison

| Feature | Desktop (Tkinter) | Web (Flask) |
|---------|------------------|-------------|
| Image Upload | ✅ | ✅ |
| Camera Capture | ✅ | ✅ |
| Real-time Analysis | ✅ | ✅ |
| Modern UI | ❌ | ✅ |
| Mobile Support | ❌ | ✅ |
| Report Download | ❌ | ✅ |
| Responsive Design | ❌ | ✅ |
| Cross-platform | Limited | ✅ |

The web application provides all the functionality of the desktop version with enhanced usability and modern design!

