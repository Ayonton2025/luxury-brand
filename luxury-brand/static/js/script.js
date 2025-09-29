// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functionality
    initNavigation();
    initProductDropdowns();
    initTestimonialSlider();
    initCountdown();
    initVideoPlaceholders();
    initForms();
    initWishlistCart(); // Wishlist and cart functionality
    
    // Initialize animations after all else
    setTimeout(initAnimations, 100);
    
    // Update counters on page load
    updateCartCount();
    updateWishlistIndicator();

    // Fetch counts from backend if logged in
    fetchCartCountFromBackend();
    fetchWishlistCountFromBackend();
});

// Navigation handling
function initNavigation() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    if (hamburger) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
    }
    
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            navMenu.classList.remove('active');
        });
    });
    
    window.addEventListener('scroll', () => {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 100) {
            navbar.style.padding = '10px 0';
            navbar.style.backgroundColor = 'rgba(26, 26, 26, 0.98)';
        } else {
            navbar.style.padding = '15px 0';
            navbar.style.backgroundColor = 'rgba(26, 26, 26, 0.95)';
        }
    });
}

// Product dropdown toggles
function initProductDropdowns() {
    const dropdownBtns = document.querySelectorAll('.dropdown-btn');
    if (!dropdownBtns.length) return;

    dropdownBtns.forEach(btn => {
        btn.addEventListener('click', e => {
            e.preventDefault();
            e.stopPropagation();
            const dropdownContent = btn.nextElementSibling;
            const icon = btn.querySelector('i');
            dropdownContent.classList.toggle('active');
            btn.classList.toggle('active');
            if (dropdownContent.classList.contains('active')) {
                icon.style.transform = 'rotate(180deg)';
                closeOtherDropdowns(btn);
            } else {
                icon.style.transform = 'rotate(0deg)';
            }
        });
    });

    document.addEventListener('click', e => {
        if (!e.target.closest('.product-dropdown')) {
            closeAllDropdowns();
        }
    });

    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') {
            closeAllDropdowns();
        }
    });

    function closeOtherDropdowns(currentBtn) {
        dropdownBtns.forEach(btn => {
            if (btn !== currentBtn) {
                btn.nextElementSibling.classList.remove('active');
                btn.classList.remove('active');
                btn.querySelector('i').style.transform = 'rotate(0deg)';
            }
        });
    }

    function closeAllDropdowns() {
        dropdownBtns.forEach(btn => {
            btn.nextElementSibling.classList.remove('active');
            btn.classList.remove('active');
            btn.querySelector('i').style.transform = 'rotate(0deg)';
        });
    }
}

// Testimonial slider logic
function initTestimonialSlider() {
    const slides = document.querySelectorAll('.testimonial-slide');
    const prevBtn = document.querySelector('.testimonial-prev');
    const nextBtn = document.querySelector('.testimonial-next');

    if (!slides.length) return;

    let currentSlide = 0;
    function showSlide(index) {
        slides.forEach(slide => slide.classList.remove('active'));
        slides[index].classList.add('active');
    }
    function nextSlide() {
        currentSlide = (currentSlide + 1) % slides.length;
        showSlide(currentSlide);
    }
    function prevSlide() {
        currentSlide = (currentSlide - 1 + slides.length) % slides.length;
        showSlide(currentSlide);
    }
    if (nextBtn && prevBtn) {
        nextBtn.addEventListener('click', nextSlide);
        prevBtn.addEventListener('click', prevSlide);
    }
    if (slides.length > 1) {
        setInterval(nextSlide, 5000);
    }
}

// Countdown timer
function initCountdown() {
    const daysEl = document.getElementById('days');
    const hoursEl = document.getElementById('hours');
    const minutesEl = document.getElementById('minutes');
    const secondsEl = document.getElementById('seconds');

    if (!daysEl) return;

    // Ideally pass timestamp from server for exact countdown
    const countDownDate = new Date();
    countDownDate.setDate(countDownDate.getDate() + 7);

    const intervalId = setInterval(() => {
        const now = Date.now();
        const distance = countDownDate - now;

        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        daysEl.textContent = days.toString().padStart(2, '0');
        hoursEl.textContent = hours.toString().padStart(2, '0');
        minutesEl.textContent = minutes.toString().padStart(2, '0');
        secondsEl.textContent = seconds.toString().padStart(2, '0');

        if (distance < 0) {
            clearInterval(intervalId);
            daysEl.textContent = hoursEl.textContent = minutesEl.textContent = secondsEl.textContent = '00';
        }
    }, 1000);
}

// Animations on scroll
function initAnimations() {
    const fadeElems = document.querySelectorAll('.fade-in');
    if (!fadeElems.length) return;

    function isInViewport(el) {
        const rect = el.getBoundingClientRect();
        return rect.top <= window.innerHeight * 0.8 && rect.bottom >= 0;
    }
    function checkFade() {
        fadeElems.forEach(el => {
            if (isInViewport(el)) el.classList.add('visible');
        });
    }
    checkFade();
    window.addEventListener('scroll', checkFade);
    window.addEventListener('resize', checkFade);
}

// Video play modal
function initVideoPlaceholders() {
    const placeholders = document.querySelectorAll('.video-placeholder');
    const modal = document.querySelector('.video-modal');
    const closeBtn = document.querySelector('.close-modal');
    const player = document.getElementById('video-player');

    if (!placeholders.length) return;

    placeholders.forEach(el => {
        el.addEventListener('click', () => {
            const url = el.getAttribute('data-video');
            if (url) {
                player.src = url;
                modal.classList.add('active');
            }
        });
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            modal.classList.remove('active');
            player.src = '';
        });
    }
    if (modal) {
        modal.addEventListener('click', e => {
            if (e.target === modal) {
                modal.classList.remove('active');
                player.src = '';
            }
        });
    }
}

// Form submissions: newsletter, contact, giveaway
function initForms() {
    const newsletterForm = document.getElementById('newsletter-form');
    if (newsletterForm) newsletterForm.addEventListener('submit', handleNewsletter);

    const contactForm = document.getElementById('contact-form');
    if (contactForm) contactForm.addEventListener('submit', handleContact);

    const giveawayForm = document.getElementById('giveaway-form');
    if (giveawayForm) giveawayForm.addEventListener('submit', handleGiveaway);
}

function handleNewsletter(e) {
    e.preventDefault();
    const form = e.target;
    const email = form.querySelector('input[type="email"]').value.trim();
    fetch('/api/subscribe', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email}),
    })
    .then(res => res.json())
    .then(data => {
        showNotification(data.message, data.success ? 'success' : 'error');
        if (data.success) form.reset();
    })
    .catch(() => showNotification('An error occurred. Please try again.', 'error'));
}

function handleContact(e) {
    e.preventDefault();
    const form = e.target;
    const name = form.querySelector('input[type="text"]').value.trim();
    const email = form.querySelector('input[type="email"]').value.trim();
    const message = form.querySelector('textarea').value.trim();
    fetch('/api/contact', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, email, message}),
    })
    .then(res => res.json())
    .then(data => {
        showNotification(data.message, data.success ? 'success' : 'error');
        if (data.success) form.reset();
    })
    .catch(() => showNotification('An error occurred. Please try again.', 'error'));
}

function handleGiveaway(e) {
    e.preventDefault();
    const form = e.target;
    const email = form.querySelector('input[type="email"]').value.trim();
    fetch('/api/enter-giveaway', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email}),
    })
    .then(res => res.json())
    .then(data => {
        showNotification(data.message, data.success ? 'success' : 'error');
        if (data.success) form.reset();
    })
    .catch(() => showNotification('An error occurred. Please try again.', 'error'));
}

// Wishlist & Cart

function initWishlistCart() {
    document.querySelectorAll('.action-btn.wishlist').forEach(btn =>
        btn.addEventListener('click', e => {
            e.preventDefault();
            e.stopPropagation();
            const card = btn.closest('.product-card');
            const id = card.getAttribute('data-product-id');
            const name = card.querySelector('.product-title').textContent;
            toggleWishlist(id, name, btn);
        })
    );

    document.querySelectorAll('.action-btn.cart').forEach(btn =>
        btn.addEventListener('click', e => {
            e.preventDefault();
            e.stopPropagation();
            const card = btn.closest('.product-card');
            const id = card.getAttribute('data-product-id');
            const name = card.querySelector('.product-title').textContent;
            const price = btn.dataset.price || parseFloat(btn.textContent.match(/\$([\d.]+)/)[1]);
            addToCart(id, name, price, btn);
        })
    );
}

function toggleWishlist(id, name, btn) {
    let wishlist = JSON.parse(localStorage.getItem('wishlist')) || [];
    const index = wishlist.findIndex(i => i.id === id);
    if (index !== -1) {
        wishlist.splice(index, 1);
        btn.innerHTML = '<i class="far fa-heart"></i> Wishlist';
        showNotification(`Removed ${name} from wishlist`, 'info');
    } else {
        wishlist.push({id, name, date: new Date().toISOString()});
        btn.innerHTML = '<i class="fas fa-heart"></i> In Wishlist';
        showNotification(`Added ${name} to wishlist`, 'success');
    }
    localStorage.setItem('wishlist', JSON.stringify(wishlist));
    updateWishlistIndicator();
}

function addToCart(id, name, price, btn) {
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    const existing = cart.find(i => i.id === id);
    if (existing) {
        existing.quantity++;
        showNotification(`Increased quantity of ${name} in cart`, 'info');
    } else {
        cart.push({id, name, price, quantity: 1, date: new Date().toISOString()});
        showNotification(`Added ${name} to cart`, 'success');
    }
    btn.classList.add('adding');
    setTimeout(() => btn.classList.remove('adding'), 500);
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
}

function updateCartCount() {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    const total = cart.reduce((acc, i) => acc + i.quantity, 0);
    let indicator = document.getElementById('cart-indicator');
    if (!indicator) {
        const link = document.querySelector('a[href="/cart"]');
        if (!link) return;
        indicator = document.createElement('span');
        indicator.id = 'cart-indicator';
        indicator.className = 'cart-indicator';
        link.appendChild(indicator);
    }
    if (total > 0) {
        indicator.textContent = total;
        indicator.style.display = 'flex';
    } else {
        indicator.style.display = 'none';
    }
}

function updateWishlistIndicator() {
    const wishlist = JSON.parse(localStorage.getItem('wishlist')) || [];
    let indicator = document.getElementById('wishlist-indicator');
    if (!indicator) {
        const link = document.querySelector('a[href="/wishlist"]');
        if (!link) return;
        indicator = document.createElement('span');
        indicator.id = 'wishlist-indicator';
        indicator.className = 'wishlist-indicator';
        link.appendChild(indicator);
    }
    if (wishlist.length > 0) {
        indicator.textContent = wishlist.length;
        indicator.style.display = 'flex';
    } else {
        indicator.style.display = 'none';
    }
}

// Notification popup
function showNotification(message, type = 'info') {
    document.querySelectorAll('.notification').forEach(n => n.remove());

    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button class="notification-close">&times;</button>
    `;
    document.body.appendChild(notification);

    setTimeout(() => notification.classList.add('show'), 10);
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);

    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    });
}

// Backend API calls to update cart counts if logged in
function fetchCartCountFromBackend() {
    fetch('/api/cart/count')
    .then(res => res.json())
    .then(data => {
        if ('count' in data) {
            let indicator = document.getElementById('cart-indicator');
            if (!indicator) {
                const link = document.querySelector('a[href="/cart"]');
                if (!link) return;
                indicator = document.createElement('span');
                indicator.id = 'cart-indicator';
                indicator.className = 'cart-indicator';
                link.appendChild(indicator);
            }
            if (data.count > 0) {
                indicator.textContent = data.count;
                indicator.style.display = 'flex';
            } else {
                indicator.style.display = 'none';
            }
        }
    })
    .catch(err => console.error('Failed to fetch cart count:', err));
}

function fetchWishlistCountFromBackend() {
    // Implement when backend API for wishlist count is ready
    /*
    fetch('/api/wishlist/count')
    .then(res => res.json())
    .then(data => {
        if ('count' in data) {
            let indicator = document.getElementById('wishlist-indicator');
            if (!indicator) {
                const link = document.querySelector('a[href="/wishlist"]');
                if (!link) return;
                indicator = document.createElement('span');
                indicator.id = 'wishlist-indicator';
                indicator.className = 'wishlist-indicator';
                link.appendChild(indicator);
            }
            if (data.count > 0) {
                indicator.textContent = data.count;
                indicator.style.display = 'flex';
            } else {
                indicator.style.display = 'none';
            }
        }
    })
    .catch(err => console.error('Failed to fetch wishlist count:', err));
    */
}
