// Global variables
let currentImage = null;
let stream = null;

// DOM elements
const uploadArea = document.getElementById('uploadArea');
const imageInput = document.getElementById('imageInput');
const uploadBtn = document.getElementById('uploadBtn');
const cameraBtn = document.getElementById('cameraBtn');
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const imagePreview = document.getElementById('imagePreview');
const previewImg = document.getElementById('previewImg');
const removeBtn = document.getElementById('removeBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const demoWarning = document.getElementById('demoWarning');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
});

function initializeEventListeners() {
    // Upload area events
    uploadArea.addEventListener('click', () => imageInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // File input events
    imageInput.addEventListener('change', handleFileSelect);
    
    // Camera events
    cameraBtn.addEventListener('click', startCamera);
    
    // Remove image event
    removeBtn.addEventListener('click', removeImage);
    
    // Analyze button event
    analyzeBtn.addEventListener('click', analyzeImage);
    
    // New analysis button event
    document.getElementById('newAnalysisBtn').addEventListener('click', resetAnalysis);
    
    // Download report button event
    document.getElementById('downloadReportBtn').addEventListener('click', downloadReport);
}

// Drag and drop handlers
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

// File selection handler
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

// File handling
function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        showNotification('Please select a valid image file.', 'error');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        currentImage = e.target.result;
        displayImagePreview(currentImage);
        enableAnalyzeButton();
    };
    reader.readAsDataURL(file);
}

// Camera functionality
async function startCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: { ideal: 640 },
                height: { ideal: 480 }
            } 
        });
        
        video.srcObject = stream;
        video.style.display = 'block';
        cameraBtn.style.display = 'none';
        
        // Add capture button
        const captureBtn = document.createElement('button');
        captureBtn.innerHTML = '<i class="fas fa-camera"></i> Capture Photo';
        captureBtn.className = 'camera-btn';
        captureBtn.style.background = 'linear-gradient(135deg, #28a745, #20c997)';
        captureBtn.onclick = capturePhoto;
        
        const cancelBtn = document.createElement('button');
        cancelBtn.innerHTML = '<i class="fas fa-times"></i> Cancel';
        cancelBtn.className = 'camera-btn';
        cancelBtn.style.background = 'linear-gradient(135deg, #dc3545, #c82333)';
        cancelBtn.onclick = stopCamera;
        
        const cameraSection = document.querySelector('.camera-section');
        cameraSection.appendChild(captureBtn);
        cameraSection.appendChild(cancelBtn);
        
    } catch (error) {
        console.error('Error accessing camera:', error);
        showNotification('Unable to access camera. Please check permissions.', 'error');
    }
}

function capturePhoto() {
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);
    
    currentImage = canvas.toDataURL('image/jpeg', 0.8);
    displayImagePreview(currentImage);
    enableAnalyzeButton();
    stopCamera();
}

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    
    video.style.display = 'none';
    cameraBtn.style.display = 'block';
    
    // Remove capture buttons
    const cameraSection = document.querySelector('.camera-section');
    const buttons = cameraSection.querySelectorAll('button:not(#cameraBtn)');
    buttons.forEach(btn => btn.remove());
}

// Image preview
function displayImagePreview(imageSrc) {
    previewImg.src = imageSrc;
    imagePreview.style.display = 'block';
    uploadArea.style.display = 'none';
}

function removeImage() {
    currentImage = null;
    imagePreview.style.display = 'none';
    uploadArea.style.display = 'block';
    disableAnalyzeButton();
    imageInput.value = '';
}

// Analyze button state
function enableAnalyzeButton() {
    analyzeBtn.disabled = false;
    analyzeBtn.style.background = 'linear-gradient(135deg, #667eea, #764ba2)';
}

function disableAnalyzeButton() {
    analyzeBtn.disabled = true;
    analyzeBtn.style.background = '#ccc';
}

// Analysis function
async function analyzeImage() {
    if (!currentImage) {
        showNotification('Please select an image first.', 'error');
        return;
    }
    
    const screenTime = parseFloat(document.getElementById('screenTime').value) || 8;
    const eyeCondition = document.getElementById('eyeCondition').value;
    
    // Show loading
    showLoading();
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                image: currentImage,
                screen_time: screenTime,
                condition: eyeCondition
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayResults(result);
        } else {
            throw new Error(result.error || 'Analysis failed');
        }
        
    } catch (error) {
        console.error('Analysis error:', error);
        showNotification('Analysis failed: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Display results
function displayResults(result) {
    // Update scores (display in 1-10 scale with 1 decimal place)
    document.getElementById('rednessScore').textContent = result.redness_score.toFixed(1) + '/10';
    document.getElementById('drynessScore').textContent = result.dryness_score.toFixed(1) + '/10';
    document.getElementById('fatigueScore').textContent = result.fatigue_score.toFixed(1) + '/10';
    document.getElementById('finalScore').textContent = result.final_fatigue.toFixed(1) + '/10';
    
    // Update fatigue level
    document.getElementById('levelEmoji').textContent = result.emoji;
    document.getElementById('levelText').textContent = result.fatigue_level;
    
    // Update parameters used
    document.getElementById('usedScreenTime').textContent = result.screen_time + ' hours';
    document.getElementById('usedCondition').textContent = result.condition;
    
    // Show demo warning if applicable
    if (result.demo_mode) {
        demoWarning.style.display = 'flex';
    } else {
        demoWarning.style.display = 'none';
    }
    
    // Update recommendations
    const recommendationsList = document.getElementById('recommendationsList');
    recommendationsList.innerHTML = '';
    result.recommendations.forEach(rec => {
        const li = document.createElement('li');
        li.textContent = rec;
        recommendationsList.appendChild(li);
    });
    
    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Loading functions
function showLoading() {
    loadingSection.style.display = 'block';
    resultsSection.style.display = 'none';
    analyzeBtn.disabled = true;
}

function hideLoading() {
    loadingSection.style.display = 'none';
    analyzeBtn.disabled = false;
}

// Reset analysis
function resetAnalysis() {
    removeImage();
    resultsSection.style.display = 'none';
    demoWarning.style.display = 'none';
    
    // Reset form
    document.getElementById('screenTime').value = '8';
    document.getElementById('eyeCondition').value = 'Normal';
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Download report
function downloadReport() {
    const results = {
        timestamp: new Date().toISOString(),
        redness_score: document.getElementById('rednessScore').textContent,
        dryness_score: document.getElementById('drynessScore').textContent,
        fatigue_score: document.getElementById('fatigueScore').textContent,
        final_fatigue_score: document.getElementById('finalScore').textContent,
        fatigue_level: document.getElementById('levelText').textContent,
        screen_time: document.getElementById('usedScreenTime').textContent,
        eye_condition: document.getElementById('usedCondition').textContent,
        recommendations: Array.from(document.querySelectorAll('.recommendations-list li')).map(li => li.textContent)
    };
    
    const dataStr = JSON.stringify(results, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `eye-fatigue-report-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
}

// Notification system
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'error' ? '#dc3545' : '#28a745'};
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 10px;
    }
`;
document.head.appendChild(style);

