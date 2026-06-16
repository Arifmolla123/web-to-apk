document.addEventListener('DOMContentLoaded', () => {
    const apkForm = document.getElementById('apk-form');
    const websiteUrlInput = document.getElementById('website-url');
    const appNameInput = document.getElementById('app-name');
    const appIconInput = document.getElementById('app-icon');
    const generateApkBtn = document.getElementById('generate-apk-btn');
    const downloadSection = document.getElementById('download-section');
    const downloadLink = document.getElementById('download-link');
    const statusMessageDiv = document.getElementById('status-message');

    const showStatusMessage = (message, type) => {
        statusMessageDiv.textContent = message;
        statusMessageDiv.className = ``; // Clear previous classes
        statusMessageDiv.classList.add(type);
        statusMessageDiv.classList.remove('hidden');
    };

    apkForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Hide previous messages and download link
        downloadSection.classList.add('hidden');
        statusMessageDiv.classList.add('hidden');
        generateApkBtn.disabled = true;
        showStatusMessage('Generating APK, please wait...', 'info');

        const formData = new FormData();
        formData.append('url', websiteUrlInput.value);
        formData.append('name', appNameInput.value);
        formData.append('icon', appIconInput.files[0]);

        try {
            const response = await fetch('https://apkverse-proxy.onrender.com/generate-apk', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);

                downloadLink.href = url;
                downloadLink.download = `${appNameInput.value.replace(/[^a-zA-Z0-9]/g, '_') || 'app'}.apk`;
                downloadSection.classList.remove('hidden');
                showStatusMessage('APK generated successfully!', 'success');
            } else {
                const errorText = await response.text();
                throw new Error(`API Error: ${response.status} - ${errorText}`);
            }
        } catch (error) {
            console.error('Error generating APK:', error);
            showStatusMessage(`Error: ${error.message || 'Failed to generate APK. Please try again.'}`, 'error');
        } finally {
            generateApkBtn.disabled = false;
        }
    });
}); 