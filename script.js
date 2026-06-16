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
        statusMessageDiv.className = '';
        statusMessageDiv.classList.add(type);
        statusMessageDiv.classList.remove('hidden');
    };

    apkForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        // হাইড করা
        downloadSection.classList.add('hidden');
        statusMessageDiv.classList.add('hidden');
        generateApkBtn.disabled = true;
        showStatusMessage('⏳ জেনারেট হচ্ছে, দয়া করে অপেক্ষা করুন...', 'info');

        const formData = new FormData();
        formData.append('url', websiteUrlInput.value);
        formData.append('name', appNameInput.value);
        formData.append('icon', appIconInput.files[0]);

        try {
            const response = await fetch('/generate-apk', {
                method: 'POST',
                body: formData,
            });

            // ১. কন্টেন্ট-টাইপ যাচাই (APK কিনা)
            const contentType = response.headers.get('content-type') || '';

            if (!response.ok) {
                // ২. এরর রেসপন্স (টেক্সট বা JSON)
                let errorMsg = `সার্ভার এরর: ${response.status}`;
                try {
                    const errorData = await response.json();
                    if (errorData.error) errorMsg = errorData.error;
                } catch {
                    const text = await response.text();
                    if (text) errorMsg = text.substring(0, 200);
                }
                throw new Error(errorMsg);
            }

            // ৩. যদি কন্টেন্ট-টাইপ APK না হয়, তাহলে এরর
            if (!contentType.includes('application/vnd.android.package-archive')) {
                const textPreview = await response.text();
                throw new Error(`API সঠিক APK ফেরত দেয়নি। এটি পেয়েছে: ${contentType} — ${textPreview.substring(0, 150)}`);
            }

            // ৪. সব ঠিক থাকলে BLOB ডাউনলোড
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);

            // ফাইলনেম ঠিক করা (স্পেশাল ক্যারেক্টার বাদ)
            const safeName = appNameInput.value.replace(/[^a-zA-Z0-9]/g, '_') || 'app';
            downloadLink.href = url;
            downloadLink.download = `${safeName}.apk`;
            downloadSection.classList.remove('hidden');
            showStatusMessage('✅ APK সফলভাবে জেনারেট হয়েছে!', 'success');

        } catch (error) {
            console.error('Error generating APK:', error);
            showStatusMessage(`❌ ${error.message || 'APK জেনারেট করতে ব্যর্থ। আবার চেষ্টা করুন।'}`, 'error');
        } finally {
            generateApkBtn.disabled = false;
        }
    });
});