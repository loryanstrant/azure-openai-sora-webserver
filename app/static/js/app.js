// JavaScript for Azure OpenAI Sora Video Generator

class VideoGenerator {
    constructor() {
        this.currentJobId = null;
        this.pollingInterval = null;
        this.initializeEventListeners();
        this.updateCharacterCount();
        this.updateDurationValue();
    }

    initializeEventListeners() {
        // Form submission
        document.getElementById('videoForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.generateVideo();
        });

        // Character counter for prompt
        document.getElementById('prompt').addEventListener('input', () => {
            this.updateCharacterCount();
        });

        // Duration slider
        document.getElementById('duration').addEventListener('input', () => {
            this.updateDurationValue();
        });

        // Generate new video button
        document.getElementById('generateNewBtn').addEventListener('click', () => {
            this.resetForm();
        });

        // Retry button
        document.getElementById('retryBtn').addEventListener('click', () => {
            this.resetForm();
        });
    }

    updateCharacterCount() {
        const prompt = document.getElementById('prompt');
        const charCount = document.getElementById('charCount');
        const currentLength = prompt.value.length;
        charCount.textContent = currentLength;
        
        // Update color based on character count
        if (currentLength > 900) {
            charCount.style.color = '#dc3545';
        } else if (currentLength > 700) {
            charCount.style.color = '#ffc107';
        } else {
            charCount.style.color = '#666';
        }
    }

    updateDurationValue() {
        const duration = document.getElementById('duration');
        const durationValue = document.getElementById('durationValue');
        durationValue.textContent = duration.value;
    }

    async generateVideo() {
        const formData = this.getFormData();
        
        if (!this.validateForm(formData)) {
            return;
        }

        this.showLoading();
        
        try {
            const response = await fetch('/api/video/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'Failed to start video generation');
            }

            if (result.success) {
                this.currentJobId = result.video_id;
                this.startPolling();
            } else {
                throw new Error(result.message || 'Failed to start video generation');
            }

        } catch (error) {
            console.error('Error starting video generation:', error);
            this.showError(error.message);
        }
    }

    getFormData() {
        return {
            prompt: document.getElementById('prompt').value.trim(),
            resolution: document.getElementById('resolution').value,
            duration: parseInt(document.getElementById('duration').value)
        };
    }

    validateForm(formData) {
        if (!formData.prompt) {
            this.showError('Please enter a video prompt');
            return false;
        }

        if (formData.prompt.length > 1000) {
            this.showError('Prompt must be 1000 characters or less');
            return false;
        }

        if (formData.duration < 1 || formData.duration > 15) {
            this.showError('Duration must be between 1 and 15 seconds');
            return false;
        }

        return true;
    }

    startPolling() {
        this.pollingInterval = setInterval(async () => {
            try {
                await this.checkVideoStatus();
            } catch (error) {
                console.error('Error checking video status:', error);
                this.stopPolling();
                this.showError('Failed to check video status');
            }
        }, 2000); // Poll every 2 seconds
    }

    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }

    async checkVideoStatus() {
        if (!this.currentJobId) {
            return;
        }

        const response = await fetch(`/api/video/status/${this.currentJobId}`);
        const status = await response.json();

        if (!response.ok) {
            throw new Error(status.detail || 'Failed to get video status');
        }

        this.updateProgress(status);

        if (status.status === 'completed') {
            this.stopPolling();
            this.showResult(status);
        } else if (status.status === 'failed') {
            this.stopPolling();
            this.showError(status.error_message || 'Video generation failed');
        }
    }

    updateProgress(status) {
        const statusText = document.getElementById('statusText');
        const progressFill = document.getElementById('progressFill');
        const progressPercent = document.getElementById('progressPercent');

        let statusMessage = 'Processing...';
        let progress = status.progress || 0;

        switch (status.status) {
            case 'pending':
                statusMessage = 'Waiting in queue...';
                progress = 5;
                break;
            case 'processing':
                statusMessage = 'Generating your video...';
                progress = Math.max(progress, 10);
                break;
            case 'completed':
                statusMessage = 'Video generation completed!';
                progress = 100;
                break;
            case 'failed':
                statusMessage = 'Video generation failed';
                progress = 0;
                break;
        }

        statusText.textContent = statusMessage;
        progressFill.style.width = `${progress}%`;
        progressPercent.textContent = `${progress}%`;
    }

    showLoading() {
        this.hideAllContainers();
        document.getElementById('loadingContainer').style.display = 'block';
        document.getElementById('generateBtn').disabled = true;
    }

    showResult(status) {
        this.hideAllContainers();
        const resultContainer = document.getElementById('resultContainer');
        resultContainer.style.display = 'block';

        if (status.video_url) {
            const video = document.getElementById('generatedVideo');
            const downloadSection = document.getElementById('downloadSection');
            const downloadLink = document.getElementById('downloadLink');

            video.src = status.video_url;
            video.style.display = 'block';
            
            downloadLink.href = status.video_url;
            downloadSection.style.display = 'block';
        }

        document.getElementById('generateBtn').disabled = false;
    }

    showError(message) {
        this.hideAllContainers();
        const errorContainer = document.getElementById('errorContainer');
        const errorMessage = document.getElementById('errorMessage');
        
        errorContainer.style.display = 'block';
        errorMessage.textContent = message;
        document.getElementById('generateBtn').disabled = false;
    }

    hideAllContainers() {
        document.getElementById('loadingContainer').style.display = 'none';
        document.getElementById('resultContainer').style.display = 'none';
        document.getElementById('errorContainer').style.display = 'none';
    }

    resetForm() {
        this.stopPolling();
        this.currentJobId = null;
        this.hideAllContainers();
        document.getElementById('generateBtn').disabled = false;
        
        // Reset video element
        const video = document.getElementById('generatedVideo');
        video.style.display = 'none';
        video.src = '';
        
        const downloadSection = document.getElementById('downloadSection');
        downloadSection.style.display = 'none';
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new VideoGenerator();
});