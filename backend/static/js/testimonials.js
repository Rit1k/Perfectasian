// Fetch and render testimonials on page load
async function loadTestimonials() {
    const res = await fetch('/get_testimonials');
    const data = await res.json();
    const container = document.getElementById('testimonials-list');
    container.innerHTML = '';
    if (data && data.length > 0) {
        data.forEach(t => {
            const stars = '★'.repeat(t.rating) + '☆'.repeat(5 - t.rating);
            const card = document.createElement('div');
            card.className = 'bg-white rounded-lg shadow p-6 flex flex-col';
            card.innerHTML = `
                <div class="font-semibold text-lg text-green-800 mb-2">${t.project || t.name}</div>
                <div class="text-gray-700 mb-4">"${t.feedback}"</div>
                <div class="flex items-center">
                    <span class="text-yellow-400 text-xl">${stars}</span>
                </div>
            `;
            container.appendChild(card);
        });
    } else {
        container.innerHTML = '<p class="text-center col-span-2">No testimonials found.</p>';
    }
}

// Handle form submission
const form = document.getElementById('testimonial-form');
if (form) {
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        const payload = Object.fromEntries(formData.entries());
        const res = await fetch('/submit_testimonial', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const msg = document.getElementById('form-message');
        if (res.ok) {
            msg.textContent = 'Thank you for your feedback!';
            msg.classList.remove('hidden');
            form.reset();
            loadTestimonials();
        } else {
            msg.textContent = 'There was an error. Please try again.';
            msg.classList.remove('hidden');
        }
    });
}

window.addEventListener('DOMContentLoaded', loadTestimonials); 