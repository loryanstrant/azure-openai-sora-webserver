// Azure OpenAI Sora Video Generator - Frontend JavaScript

class VideoGenerator {
    constructor() {
        this.currentVideoId = null;
        this.statusCheckInterval = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const form = document.getElementById('videoForm');
        const retryBtn = document.getElementById('retryBtn');
        const newVideoBtn = document.getElementById('newVideoBtn');
        const downloadBtn = document.getElementById('downloadBtn');

        form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        retryBtn.addEventListener('click', () => this.resetForm());
        newVideoBtn.addEventListener('click', () => this.resetForm());
        downloadBtn.addEventListener('click', () => this.downloadVideo());
    }

    async handleFormSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const requestData = {
            prompt: formData.get('prompt'),
            resolution: formData.get('resolution'),
            duration: parseInt(formData.get('duration'))
        };

        // Validate form data
        if (!requestData.prompt.trim()) {
            this.showError('Please enter a video prompt');
            return;
        }

        if (requestData.duration < 1 || requestData.duration > 60) {
            this.showError('Duration must be between 1 and 60 seconds');
            return;
        }

        await this.generateVideo(requestData);
    }

    async generateVideo(requestData) {
        try {
            this.setLoadingState(true);
            this.hideError();
            this.hideStatus();

            // Submit generation request
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to start video generation');
            }

            const result = await response.json();
            this.currentVideoId = result.video_id;

            // Show status and start monitoring
            this.showStatus();
            this.startStatusChecking();

        } catch (error) {
            console.error('Error generating video:', error);
            this.showError(error.message);
            this.setLoadingState(false);
        }
    }

    startStatusChecking() {
        this.updateStatus('Initializing video generation...', 0);
        
        // Check status every 2 seconds
        this.statusCheckInterval = setInterval(async () => {
            await this.checkVideoStatus();
        }, 2000);
    }

    async checkVideoStatus() {
        if (!this.currentVideoId) return;

        try {
            const response = await fetch(`/api/status/${this.currentVideoId}`);
            
            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error('Video generation job not found');
                }
                throw new Error('Failed to check video status');
            }

            const status = await response.json();
            this.handleStatusUpdate(status);

        } catch (error) {
            console.error('Error checking status:', error);
            this.stopStatusChecking();
            this.showError(error.message);
        }
    }

    handleStatusUpdate(status) {
        const { status: statusText, progress, video_url, revised_prompt } = status;

        switch (statusText) {
            case 'pending':
                this.updateStatus('Waiting in queue...', progress);
                break;
            case 'processing':
                this.updateStatus('Generating video...', progress);
                break;
            case 'completed':
                this.updateStatus('Video generation completed!', 100);
                this.stopStatusChecking();
                this.setLoadingState(false);
                this.showVideoResult(video_url, revised_prompt);
                break;
            case 'failed':
                this.stopStatusChecking();
                this.setLoadingState(false);
                this.showError('Video generation failed. Please try again.');
                break;
            default:
                this.updateStatus(`Status: ${statusText}`, progress);
        }
    }

    updateStatus(message, progress) {
        const statusText = document.getElementById('statusText');
        const progressFill = document.getElementById('progressFill');

        statusText.textContent = message;
        progressFill.style.width = `${progress}%`;

        // Add loading dots animation for processing states
        if (message.includes('Generating') || message.includes('Waiting')) {
            statusText.classList.add('loading-dots');
        } else {
            statusText.classList.remove('loading-dots');
        }
    }

    showVideoResult(videoUrl, revisedPrompt) {
        const videoResult = document.getElementById('videoResult');
        const generatedVideo = document.getElementById('generatedVideo');
        
        generatedVideo.src = videoUrl;
        videoResult.style.display = 'block';
        videoResult.classList.add('fade-in');

        // Show revised prompt if available
        if (revisedPrompt && revisedPrompt !== document.getElementById('prompt').value) {
            const statusText = document.getElementById('statusText');
            statusText.innerHTML = `✅ Video generated successfully!<br><small><strong>Revised prompt:</strong> ${revisedPrompt}</small>`;
        }
    }

    downloadVideo() {
        const video = document.getElementById('generatedVideo');
        if (video.src) {
            const a = document.createElement('a');
            a.href = video.src;
            a.download = `sora-video-${this.currentVideoId}.mp4`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }
    }

    setLoadingState(isLoading) {
        const generateBtn = document.getElementById('generateBtn');
        const formInputs = document.querySelectorAll('#videoForm input, #videoForm textarea, #videoForm select');

        if (isLoading) {
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<span>🔄 Generating...</span>';
            formInputs.forEach(input => input.disabled = true);
        } else {
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<span>🎥 Generate Video</span>';
            formInputs.forEach(input => input.disabled = false);
        }
    }

    showStatus() {
        const statusContainer = document.getElementById('statusContainer');
        const videoResult = document.getElementById('videoResult');
        
        statusContainer.style.display = 'block';
        statusContainer.classList.add('fade-in');
        videoResult.style.display = 'none';
    }

    hideStatus() {
        const statusContainer = document.getElementById('statusContainer');
        statusContainer.style.display = 'none';
        statusContainer.classList.remove('fade-in');
    }

    showError(message) {
        const errorContainer = document.getElementById('errorContainer');
        const errorMessage = document.getElementById('errorMessage');
        
        errorMessage.textContent = message;
        errorContainer.style.display = 'block';
        errorContainer.classList.add('fade-in');
    }

    hideError() {
        const errorContainer = document.getElementById('errorContainer');
        errorContainer.style.display = 'none';
        errorContainer.classList.remove('fade-in');
    }

    resetForm() {
        // Stop any ongoing status checking
        this.stopStatusChecking();
        
        // Reset UI state
        this.setLoadingState(false);
        this.hideStatus();
        this.hideError();
        
        // Clear current video ID
        this.currentVideoId = null;
        
        // Reset form
        document.getElementById('videoForm').reset();
        document.getElementById('duration').value = 5; // Reset to default
    }

    stopStatusChecking() {
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
            this.statusCheckInterval = null;
        }
    }
}

// Initialize the video generator when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new VideoGenerator();
});

// Handle page unload to clean up intervals
window.addEventListener('beforeunload', () => {
    if (window.videoGenerator) {
        window.videoGenerator.stopStatusChecking();
    }
});