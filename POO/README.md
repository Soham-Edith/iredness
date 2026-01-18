# Digital Eye Fatigue Analyzer

A final-year engineering project that combines **MediaPipe**, **Roboflow AI**, and **Flask** to analyze digital eye fatigue through computer vision.

## Project Overview

This system analyzes eye images to detect three key indicators of digital eye fatigue:

- **Redness**: Detected using MediaPipe FaceMesh and OpenCV image processing
- **Dryness**: Analyzed using Roboflow AI model (dry-eye-prediction/3)
- **Fatigue**: Detected using Roboflow AI model (eyes-bhltc/1)

All scores are normalized to a 1-10 scale with color-coded results:
- 1-3: Green (Normal)
- 4-6: Orange (Moderate)
- 7-10: Red (High)

## Requirements

- Python 3.8+
- pip (Python package manager)

## Installation

### Step 1: Create Virtual Environment

Windows:
\\\ash
python -m venv venv
\\\

Mac/Linux:
\\\ash
python3 -m venv venv
\\\

### Step 2: Activate Virtual Environment

Windows:
\\\ash
venv\Scripts\activate
\\\

Mac/Linux:
\\\ash
source venv/bin/activate
\\\

### Step 3: Install Dependencies

\\\ash
pip install -r requirements.txt
\\\

## Configuration

### Roboflow API Key

To use Roboflow models for dryness and fatigue detection:

1. Sign up at [Roboflow](https://roboflow.com)
2. Get your API key from the dashboard
3. Update the API key in [digital_eye_fatigue_analyzer.py](digital_eye_fatigue_analyzer.py):

\\\python
self.api_key = "YOUR_ROBOFLOW_API_KEY"
\\\

## Running the Application

\\\ash
python app.py
\\\

The application will start on \http://127.0.0.1:5000\

Open your browser and navigate to the URL to use the system.

## Testing

Run unit tests to verify the analyzer:

\\\ash
python -m unittest tests/test_scoring.py -v
\\\

Tests verify:
- Analyzer initialization
- Score range validation (1-10)
- API response handling
- Error handling

## Project Structure

\\\
.
 app.py                           # Flask web application
 digital_eye_fatigue_analyzer.py  # Core analysis engine
 requirements.txt                 # Python dependencies
 README.md                        # Setup instructions
 README_WEB.md                    # Web usage guide
 static/
    style.css                    # UI styling
 templates/
    index.html                   # Upload page
    result.html                  # Results page
 tests/
    test_scoring.py              # Unit tests
 venv/                            # Virtual environment
\\\

## Technical Details

### Backend (digital_eye_fatigue_analyzer.py)

**EyeFatigueAnalyzer Class:**
- get_redness(image_bgr): Uses MediaPipe FaceMesh landmarks to extract eye regions, analyzes sclera color in HSV space
- get_dryness(image_path): Calls Roboflow API for dry eye detection
- get_fatigue(image_path): Calls Roboflow API for eye fatigue detection
- nalyze_image(image_path): Performs complete analysis

**Key Features:**
- Error handling with fallback neutral scores (5/10)
- Score normalization to 1-10 scale
- Graceful degradation if API calls fail

### Frontend (Flask + HTML/CSS)

**Routes:**
- GET /: Upload page
- POST /analyze: Image analysis endpoint
- GET /results: Results display page

**Features:**
- Drag-and-drop file upload
- Image preview before analysis
- Real-time validation
- Responsive design for mobile

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| flask | 2.3.0 | Web framework |
| opencv-python | 4.8.0.74 | Image processing |
| mediapipe | 0.10.0 | Face mesh detection |
| numpy | 1.24.3 | Numerical computations |
| inference-sdk | 0.13.0 | Roboflow API client |
| Werkzeug | 2.3.0 | WSGI utilities |

## API Specifications

### POST /analyze

**Request:**
- Method: POST (multipart/form-data)
- File: Image file (PNG, JPG, JPEG, BMP, GIF)
- Max size: 16MB

**Response:**
\\\json
{
  "success": true,
  "redness": 5,
  "dryness": 4,
  "fatigue": 6
}
\\\

## Error Handling

- Invalid file types: Error message with allowed formats
- File size exceeded: Returns 413 status code
- Missing Roboflow API key: Falls back to neutral scores
- Face not detected: Uses default neutral redness score (5)

## Academic Standards

This project follows academic best practices:
- Clear code documentation and comments
- Modular architecture separating concerns
- Comprehensive unit tests
- Proper error handling
- User-friendly interface

## Future Improvements

- Real-time camera analysis
- Historical data tracking
- Export analysis reports
- Mobile app integration
- Additional eye condition models

## License

This project is for educational purposes.

## Authors

Final-Year Engineering Project - Eye Fatigue Analysis System

## Support

For issues or questions, refer to:
- [MediaPipe Documentation](https://mediapipe.dev)
- [Roboflow Documentation](https://docs.roboflow.com)
- [Flask Documentation](https://flask.palletsprojects.com)
