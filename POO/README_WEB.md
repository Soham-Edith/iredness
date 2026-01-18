# Digital Eye Fatigue Analyzer - Web Usage Guide

## Getting Started

After installing and running the application, follow these steps to analyze eye fatigue.

## Step-by-Step Usage

### 1. Open Browser

Once the Flask application is running, open your web browser and navigate to:

\\\
http://127.0.0.1:5000
\\\

You should see the upload page with the title **\"Digital Eye Fatigue Analyzer\"**.

### 2. Upload Image

The application accepts the following image formats:
- PNG
- JPG / JPEG
- BMP
- GIF

Maximum file size: **16MB**

**Two ways to upload:**

#### Method A: Click and Browse
1. Click on the upload area
2. Select an image file from your computer
3. Image preview will appear

#### Method B: Drag and Drop
1. Locate your eye image file
2. Drag the file over the upload area
3. Release to upload

### 3. Preview Image

After selecting an image:
- Preview will display the selected image
- Click **\"Remove\"** button to deselect
- Select a different image if needed

### 4. Click Analyze

Once satisfied with the image:
1. Click the **\"Analyze Image\"** button
2. Wait for processing (shows \"Analyzing image...\" spinner)
3. Results will load automatically

## Results Page

The analysis results display three key metrics:

### Score Metrics

Each metric is displayed as:
- **Score**: 1-10 scale
- **Progress bar**: Visual representation of severity
- **Status label**: Color-coded indicator

#### 1. Redness (Left)
- Uses MediaPipe face detection + OpenCV image processing
- Analyzes sclera (white part of eye) color in HSV space
- **1-3 (Green)**: Normal eyes
- **4-6 (Orange)**: Mild redness
- **7-10 (Red)**: Severe redness

#### 2. Dryness (Center)
- Uses Roboflow AI model: dry-eye-prediction/3
- Detects dry eye symptoms
- **1-3 (Green)**: Eyes well-moisturized
- **4-6 (Orange)**: Moderate dryness
- **7-10 (Red)**: Severe dryness

#### 3. Fatigue (Right)
- Uses Roboflow AI model: eyes-bhltc/1
- Detects overall eye fatigue
- **1-3 (Green)**: No fatigue
- **4-6 (Orange)**: Mild fatigue
- **7-10 (Red)**: Severe fatigue

### Recommendations

Below scores, you'll see personalized recommendations:
-  Blink more frequently
- 20-20-20 Rule: Every 20 min, look 20 feet away for 20 seconds
-  Maintain proper lighting
-  Include vitamin A-rich foods
-  Ensure adequate sleep

### Action Buttons

#### Analyze Another Image
Returns to upload page to test another image

#### Download Results
Saves analysis report as text file with:
- Timestamp of analysis
- All three scores
- Easy to share and keep records

## Color Coding

The interface uses consistent color coding:

| Color | Score Range | Meaning |
|-------|-------------|---------|
|  Green | 1-3 | Normal / Healthy |
|  Orange | 4-6 | Moderate / Caution |
|  Red | 7-10 | High / Alert |

## Troubleshooting

### \"No file uploaded\" Error
- **Cause**: File selection cancelled
- **Solution**: Click the upload area again and select a file

### \"Invalid image file\" Error
- **Cause**: File is corrupted or not a valid image
- **Solution**: Try with a different image file

### \"File too large\" Error
- **Cause**: Image exceeds 16MB limit
- **Solution**: Compress image or use a smaller file

### \"Analysis failed\" Error
- **Cause**: Missing Roboflow API key or server issue
- **Solution**: Ensure API key is configured in digital_eye_fatigue_analyzer.py

### Results show default scores (5/10 for all)
- **Cause**: Roboflow API key not configured
- **Solution**: Add your Roboflow API key to digital_eye_fatigue_analyzer.py

## Best Practices for Accurate Results

### Image Quality
- **Lighting**: Ensure adequate, even lighting
- **Resolution**: Use high-quality camera or image
- **Angle**: Position eye clearly in frame
- **Distance**: Eyes should occupy ~30% of image

### Image Content
- Clear view of at least one eye
- Minimal shadows or reflections
- Natural eye position (not forced open or closed)
- No glasses or contacts causing reflections

### Multiple Analyses
- Test with multiple images for trends
- Compare results over time to track eye health
- Download reports to maintain history

## Example Workflow

1. **Morning Check**: Upload selfie  Score 3/10 Redness
2. **After 4 Hours Screen Time**: Upload image  Score 6/10 Redness
3. **After 8 Hours**: Upload image  Score 8/10 Fatigue
4. **Download Results**: Save reports for doctor visit

## API Information

The web interface communicates with backend via:

**Endpoint**: POST /analyze
**Input**: Image file (multipart/form-data)
**Output**: JSON with scores
**Timeout**: 30 seconds per analysis

## Performance Notes

- First analysis: May take 5-10 seconds (API initialization)
- Subsequent analyses: 2-5 seconds
- Internet connection required for Roboflow models
- Works best on modern browsers (Chrome, Firefox, Edge, Safari)

## Mobile Devices

The application is responsive and works on mobile devices:
- Touch-friendly upload area
- Scalable interface
- Mobile camera integration available

To use mobile camera:
1. Open http://127.0.0.1:5000 on mobile browser
2. Upload interface will detect camera capability
3. Grant camera permission when prompted

## Technical Support

### Check Application Status
- If page won't load: Verify Flask is running
- Check terminal for error messages
- Ensure http://127.0.0.1:5000 is accessible

### Internet Connectivity
- System requires internet for Roboflow API calls
- Offline mode will use fallback neutral scores

## Privacy

- Images are processed locally and deleted after analysis
- No images are stored on server
- Results are not logged or tracked
- Only anonymized metrics are retained

## Example Results Interpretation

### Scenario 1: Good Eye Health
`
Redness: 2/10  Normal
Dryness: 3/10  Normal
Fatigue: 2/10  Normal
`
 Eyes are healthy, continue regular habits

### Scenario 2: Digital Eye Strain
`
Redness: 5/10  Moderate
Dryness: 6/10  Moderate
Fatigue: 5/10  Moderate
`
 Take breaks, apply 20-20-20 rule

### Scenario 3: Severe Fatigue
`
Redness: 8/10  High
Dryness: 7/10  High
Fatigue: 8/10  High
`
 Rest needed, consider artificial tears

## Frequently Asked Questions

**Q: How accurate is the analysis?**
A: Accuracy depends on image quality and proper Roboflow API key configuration.

**Q: Can I use this for medical diagnosis?**
A: This is a screening tool only. Consult eye care professional for medical diagnosis.

**Q: How often should I test?**
A: Daily for tracking, weekly for trends.

**Q: What if results seem wrong?**
A: Try with better quality image or different lighting.

**Q: Can I run this offline?**
A: No, Roboflow API requires internet connection.
