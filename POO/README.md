# Digital Eye Fatigue Analyzer

A Python GUI application that analyzes eye fatigue using computer vision models from Roboflow.

## Features

- **Image Input**: Upload images from file or capture from webcam
- **Multi-Model Analysis**: Uses three Roboflow models for comprehensive analysis:
  - Fatigue Detection
  - Dryness Detection  
  - Redness Detection
- **Smart Scoring**: Calculates final fatigue score considering:
  - Screen time factor
  - Eye condition multiplier
  - Multiple model confidence scores
- **Personalized Recommendations**: Provides tailored advice based on analysis results
- **Clean GUI**: Modern Tkinter interface with progress indicators

## Installation

1. **Activate your virtual environment**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

## Usage

1. **Run the application**:
   ```powershell
   python digital_eye_fatigue_analyzer_api.py
   ```

2. **Using the GUI**:
   - **Upload Image**: Click "Upload Image" to select a photo from your computer
   - **Capture from Webcam**: Click "Capture from Webcam" to take a photo
   - **Set Parameters**: 
     - Enter screen time in hours
     - Select eye condition (Normal, Diabetic Retinopathy, Glaucoma, Cataract)
   - **Analyze**: Click "Analyze Eye Fatigue" to run the analysis
   - **View Results**: Results will appear in the scrollable text area

## Analysis Algorithm

The application calculates a comprehensive fatigue score using:

```
FinalFatigue = (0.5 × fatigue_score + 0.2 × redness_score + 0.1 × dryness_score + 0.2 × time_factor) × condition_multiplier
```

Where:
- `time_factor = min(screen_time / 10, 1.0)`
- `condition_multiplier` varies by eye condition:
  - Normal: 1.0
  - Diabetic Retinopathy: 0.9
  - Glaucoma: 0.85
  - Cataract: 0.85

## Fatigue Levels

- **Normal** (😊): Score < 0.3
- **Mild** (😐): Score 0.3 - 0.5
- **Moderate** (😕): Score 0.5 - 0.7
- **Severe** (😰): Score > 0.7

## Requirements

- Python 3.8+
- Internet connection (for Roboflow API)
- Webcam (optional, for image capture)

## API Configuration

The application uses the Roboflow API with the following models:
- Fatigue Detection: `eyes-bhltc/1`
- Dryness Detection: `dry-eye-prediction/3`
- Redness Detection: `redness-detect/1`

The API key is already configured in the code. For production use, consider using environment variables for API key management.

## Troubleshooting

- **Webcam Issues**: Ensure your webcam is not being used by another application
- **API Errors**: Check your internet connection and API key validity
- **Image Loading**: Supported formats: JPG, JPEG, PNG, BMP, GIF
- **Analysis Freezing**: The application uses threading to prevent GUI freezing during analysis



