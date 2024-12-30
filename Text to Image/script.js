document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements
    const generateBtn = document.getElementById('generateBtn');
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');
    const resultContainer = document.getElementById('resultContainer');
    const downloadBtn = document.getElementById('downloadBtn');
    const imagination = document.getElementById('imagination');

    // Function to show loading state
    const showLoading = () => {
        loading.classList.add('active');
        generateBtn.disabled = true;
        resultContainer.classList.remove('active');
    };

    // Function to hide loading state
    const hideLoading = () => {
        loading.classList.remove('active');
        generateBtn.disabled = false;
    };

    // Function to display error
    const showError = (message) => {
        alert(message);
        console.error('Error:', message);
    };

    // Function to generate artwork
    const generateArtwork = async (prompt) => {
        try {
            console.log('Generating text description...');
            const textResponse = await fetch('http://localhost:5000/generate_text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ topic: prompt })
            });

            if (!textResponse.ok) {
                throw new Error('Failed to generate text description');
            }

            const textData = await textResponse.json();
            console.log('Text description generated:', textData.description);

            console.log('Generating image...');
            const imageResponse = await fetch('http://127.0.0.1:5000//generate_image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: textData.description })
            });

            if (!imageResponse.ok) {
                throw new Error('Failed to generate image');
            }

            const blob = await imageResponse.blob();
            return URL.createObjectURL(blob);
        } catch (error) {
            throw new Error(`Generation failed: ${error.message}`);
        }
    };

    // Function to display the generated image
    const displayImage = (imageUrl) => {
        const img = document.createElement('img');
        img.src = imageUrl;
        img.alt = 'Generated artwork';
        img.className = 'generated-image';

        result.innerHTML = '';
        result.appendChild(img);
        resultContainer.classList.add('active');
    };

    // Handle generate button click
    generateBtn.addEventListener('click', async () => {
        const prompt = imagination.value.trim();
        
        if (!prompt) {
            showError('Please describe what you want to create');
            return;
        }

        showLoading();

        try {
            const imageUrl = await generateArtwork(prompt);
            displayImage(imageUrl);
        } catch (error) {
            showError(error.message);
        } finally {
            hideLoading();
        }
    });

    // Handle download button click
    downloadBtn.addEventListener('click', async () => {
        const image = document.querySelector('.generated-image');
        if (!image) {
            showError('No image to download');
            return;
        }

        try {
            const response = await fetch(image.src);
            const blob = await response.blob();
            
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `ai-artwork-${Date.now()}.png`;
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } catch (error) {
            showError('Failed to download image');
        }
    });
});