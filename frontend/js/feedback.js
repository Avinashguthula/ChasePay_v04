function openFeedbackModal() {
    // Inject modal if it doesn't exist
    if (!document.getElementById('feedback-modal')) {
        const modalHTML = `
            <div id="feedback-modal" class="fixed inset-0 z-[60] flex items-center justify-center p-4 transition-all duration-300 opacity-0 invisible">
                <div class="absolute inset-0 bg-dark/40 backdrop-blur-md" onclick="toggleFeedbackModal()"></div>
                <div class="bg-white w-full max-w-md rounded-3xl overflow-hidden shadow-2xl relative z-10 transform scale-95 opacity-0 transition-all duration-300" id="feedback-card">
                    <div class="p-8">
                        <div class="flex justify-between items-start mb-6">
                            <div>
                                <h2 class="font-heading font-bold text-2xl text-text mb-1">Help us improve</h2>
                                <p class="text-sm text-muted">Your feedback helps us build a better experience.</p>
                            </div>
                            <button onclick="toggleFeedbackModal()" class="p-2 hover:bg-bg rounded-full transition-colors">
                                <svg class="w-5 h-5 text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                </svg>
                            </button>
                        </div>
                        
                        <form id="feedback-form" class="space-y-6">
                            <div class="space-y-3">
                                <label class="block text-[10px] font-mono font-bold uppercase tracking-widest text-muted">Rating</label>
                                <div class="flex gap-2">
                                    <button type="button" onclick="setFeedbackRating(this, 1)" class="rating-btn w-11 h-11 rounded-2xl border border-border flex items-center justify-center hover:border-amber transition-all text-xl grayscale hover:grayscale-0">😞</button>
                                    <button type="button" onclick="setFeedbackRating(this, 2)" class="rating-btn w-11 h-11 rounded-2xl border border-border flex items-center justify-center hover:border-amber transition-all text-xl grayscale hover:grayscale-0">😐</button>
                                    <button type="button" onclick="setFeedbackRating(this, 3)" class="rating-btn w-11 h-11 rounded-2xl border border-border flex items-center justify-center hover:border-amber transition-all text-xl grayscale hover:grayscale-0 active-rating">😊</button>
                                    <button type="button" onclick="setFeedbackRating(this, 4)" class="rating-btn w-11 h-11 rounded-2xl border border-border flex items-center justify-center hover:border-amber transition-all text-xl grayscale hover:grayscale-0">🔥</button>
                                    <button type="button" onclick="setFeedbackRating(this, 5)" class="rating-btn w-11 h-11 rounded-2xl border border-border flex items-center justify-center hover:border-amber transition-all text-xl grayscale hover:grayscale-0">💎</button>
                                </div>
                                <input type="hidden" name="rating" id="feedback-rating-input" value="3">
                            </div>

                            <div class="space-y-3">
                                <label class="block text-[10px] font-mono font-bold uppercase tracking-widest text-muted">Comment</label>
                                <textarea id="feedback-comment" class="w-full h-32 p-4 rounded-2xl border border-border bg-bg/30 focus:outline-none focus:ring-2 focus:ring-amber/10 focus:border-amber transition-all text-sm resize-none placeholder:text-muted/40" placeholder="What's on your mind?"></textarea>
                            </div>

                            <button type="submit" class="w-full py-4 bg-text text-white rounded-full text-xs font-mono font-bold uppercase tracking-widest hover:bg-muted transition-all shadow-soft active:scale-[0.98]">
                                Submit Feedback
                            </button>
                        </form>
                    </div>
                </div>
            </div>
            <style>
                .active-rating {
                    border-color: #FFB200 !important;
                    background-color: rgba(255, 178, 0, 0.05);
                    filter: grayscale(0) !important;
                    transform: scale(1.1);
                }
            </style>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Add form listener
        document.getElementById('feedback-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = e.target.querySelector('button[type="submit"]');
            const originalText = btn.textContent;
            btn.textContent = 'Sending...';
            btn.disabled = true;

            const rating = document.getElementById('feedback-rating-input').value;
            const comment = document.getElementById('feedback-comment').value;

            // Mock success
            setTimeout(() => {
                toggleFeedbackModal();
                showNotification('Success', 'Thank you for your feedback!', 'success');
                btn.textContent = originalText;
                btn.disabled = false;
                document.getElementById('feedback-comment').value = '';
            }, 800);
        });
    }

    // Toggle open
    setTimeout(() => {
        const modal = document.getElementById('feedback-modal');
        const card = document.getElementById('feedback-card');
        modal.classList.remove('invisible');
        modal.classList.add('opacity-100');
        card.classList.remove('scale-95', 'opacity-0');
        card.classList.add('scale-100', 'opacity-100');
    }, 10);
}

function toggleFeedbackModal() {
    const modal = document.getElementById('feedback-modal');
    const card = document.getElementById('feedback-card');
    if (!modal) return;
    
    modal.classList.add('opacity-0');
    card.classList.add('scale-95', 'opacity-0');
    setTimeout(() => {
        modal.classList.add('invisible');
    }, 300);
}

function setFeedbackRating(btn, value) {
    document.querySelectorAll('.rating-btn').forEach(b => b.classList.remove('active-rating'));
    btn.classList.add('active-rating');
    document.getElementById('feedback-rating-input').value = value;
}

// Utility to show notification if available, otherwise alert
function showNotification(title, message, type) {
    if (window.showToast) {
        window.showToast(message, type);
    } else {
        alert(message);
    }
}
