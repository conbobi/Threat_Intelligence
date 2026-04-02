// Lazy loading effect with Intersection Observer for cards animation
document.addEventListener('DOMContentLoaded', () => {
    // Add fade-in effect to cards with a staggered delay
    const cards = document.querySelectorAll('.animate-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.05}s`;
        card.style.opacity = '1';
    });

    // Optional: Add a "scroll to top" button dynamically
    const createScrollTopButton = () => {
        const btn = document.createElement('button');
        btn.innerHTML = '<i class="bi bi-arrow-up-short"></i>';
        btn.className = 'scroll-top-btn';
        btn.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #3b82f6;
            color: white;
            border: none;
            width: 45px;
            height: 45px;
            border-radius: 50%;
            font-size: 24px;
            cursor: pointer;
            opacity: 0;
            transition: opacity 0.3s;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            z-index: 999;
        `;
        document.body.appendChild(btn);

        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                btn.style.opacity = '1';
            } else {
                btn.style.opacity = '0';
            }
        });

        btn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    };

    createScrollTopButton();

    // Optional: Add a little hover effect for cards (already done in CSS, but we can add more)
    const cardsHover = document.querySelectorAll('.news-card');
    cardsHover.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transition = 'transform 0.2s ease, box-shadow 0.2s ease';
        });
    });
});