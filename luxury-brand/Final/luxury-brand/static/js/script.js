// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functionality
    initNavigation();
    initProductDropdowns();
    initTestimonialSlider();
    initCountdown();
    initVideoPlaceholders();
    initForms();
    initWishlistCart(); // NEW: Initialize wishlist and cart functionality
    
    // Initialize animations last to ensure everything is loaded
    setTimeout(initAnimations, 100);
    
    // Update cart count on page load
    updateCartCount();
});

// Navigation
function initNavigation() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    if (hamburger) {
        hamburger.addEventListener('click', function() {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
    }
    
    // Close mobile menu when clicking on a nav link
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            hamburger.classList.remove('active');
            navMenu.classList.remove('active');
        });
    });
    
    // Navbar scroll effect
    window.addEventListener('scroll', function() {
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

// Product Dropdowns - ENHANCED VERSION
function initProductDropdowns() {
    const dropdownBtns = document.querySelectorAll('.dropdown-btn');
    
    // If no dropdown buttons found, exit early
    if (dropdownBtns.length === 0) {
        return;
    }
    
    dropdownBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const dropdownContent = this.nextElementSibling;
            const icon = this.querySelector('i');
            
            // Toggle active class for dropdown content and button
            dropdownContent.classList.toggle('active');
            this.classList.toggle('active');
            
            // Rotate chevron icon
            if (dropdownContent.classList.contains('active')) {
                icon.style.transform = 'rotate(180deg)';
                // Close all other dropdowns
                closeOtherDropdowns(this);
            } else {
                icon.style.transform = 'rotate(0deg)';
            }
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.product-dropdown')) {
            closeAllDropdowns();
        }
    });
    
    // Close dropdowns when pressing Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeAllDropdowns();
        }
    });
    
    // Function to close all other dropdowns
    function closeOtherDropdowns(currentBtn) {
        dropdownBtns.forEach(btn => {
            if (btn !== currentBtn) {
                const dropdownContent = btn.nextElementSibling;
                const icon = btn.querySelector('i');
                dropdownContent.classList.remove('active');
                btn.classList.remove('active');
                icon.style.transform = 'rotate(0deg)';
            }
        });
    }
    
    // Function to close all dropdowns
    function closeAllDropdowns() {
        dropdownBtns.forEach(btn => {
            const dropdownContent = btn.nextElementSibling;
            const icon = btn.querySelector('i');
            dropdownContent.classList.remove('active');
            btn.classList.remove('active');
            icon.style.transform = 'rotate(0deg)';
        });
    }
}

// Testimonial Slider
function initTestimonialSlider() {
    const slides = document.querySelectorAll('.testimonial-slide');
    const prevBtn = document.querySelector('.testimonial-prev');
    const nextBtn = document.querySelector('.testimonial-next');
    
    // If no slides exist, exit early
    if (slides.length === 0) return;
    
    let currentSlide = 0;
    
    // Show specific slide
    function showSlide(index) {
        slides.forEach(slide => slide.classList.remove('active'));
        slides[index].classList.add('active');
    }
    
    // Next slide
    function nextSlide() {
        currentSlide = (currentSlide + 1) % slides.length;
        showSlide(currentSlide);
    }
    
    // Previous slide
    function prevSlide() {
        currentSlide = (currentSlide - 1 + slides.length) % slides.length;
        showSlide(currentSlide);
    }
    
    // Set up event listeners
    if (nextBtn && prevBtn) {
        nextBtn.addEventListener('click', nextSlide);
        prevBtn.addEventListener('click', prevSlide);
    }
    
    // Auto slide every 5 seconds only if there are multiple slides
    if (slides.length > 1) {
        setInterval(nextSlide, 5000);
    }
}

// Countdown Timer
function initCountdown() {
    const daysElement = document.getElementById('days');
    const hoursElement = document.getElementById('hours');
    const minutesElement = document.getElementById('minutes');
    const secondsElement = document.getElementById('seconds');
    
    // If no giveaway is active, exit
    if (!daysElement) return;
    
    // Set the date we're counting down to (from server data)
    const countDownDate = new Date();
    countDownDate.setDate(countDownDate.getDate() + 7);
    
    // Update the countdown every 1 second
    const countdownFunction = setInterval(function() {
        // Get today's date and time
        const now = new Date().getTime();
        
        // Find the distance between now and the count down date
        const distance = countDownDate - now;
        
        // Time calculations for days, hours, minutes and seconds
        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);
        
        // Display the results
        if (daysElement) daysElement.textContent = days.toString().padStart(2, '0');
        if (hoursElement) hoursElement.textContent = hours.toString().padStart(2, '0');
        if (minutesElement) minutesElement.textContent = minutes.toString().padStart(2, '0');
        if (secondsElement) secondsElement.textContent = seconds.toString().padStart(2, '0');
        
        // If the count down is over, write some text
        if (distance < 0) {
            clearInterval(countdownFunction);
            if (daysElement) daysElement.textContent = '00';
            if (hoursElement) hoursElement.textContent = '00';
            if (minutesElement) minutesElement.textContent = '00';
            if (secondsElement) secondsElement.textContent = '00';
        }
    }, 1000);
}

// Scroll Animations
function initAnimations() {
    const fadeElements = document.querySelectorAll('.fade-in');
    
    // If no fade elements, exit early
    if (fadeElements.length === 0) return;
    
    // Check if element is in viewport
    function isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top <= (window.innerHeight || document.documentElement.clientHeight) * 0.8 &&
            rect.bottom >= 0
        );
    }
    
    // Check elements on scroll and resize
    function checkElements() {
        fadeElements.forEach(element => {
            if (isInViewport(element)) {
                element.classList.add('visible');
            }
        });
    }
    
    // Initial check
    checkElements();
    
    // Listen for scroll and resize events
    window.addEventListener('scroll', checkElements);
    window.addEventListener('resize', checkElements);
}

// Video Placeholders
function initVideoPlaceholders() {
    const videoPlaceholders = document.querySelectorAll('.video-placeholder');
    const videoModal = document.querySelector('.video-modal');
    const closeModal = document.querySelector('.close-modal');
    const videoPlayer = document.getElementById('video-player');
    
    // If no video placeholders, exit early
    if (videoPlaceholders.length === 0) return;
    
    videoPlaceholders.forEach(placeholder => {
        placeholder.addEventListener('click', function() {
            const videoUrl = this.getAttribute('data-video');
            if (videoUrl) {
                // Set iframe source
                videoPlayer.src = videoUrl;
                // Show modal
                videoModal.classList.add('active');
            }
        });
    });
    
    // Close modal
    if (closeModal) {
        closeModal.addEventListener('click', function() {
            videoModal.classList.remove('active');
            videoPlayer.src = '';
        });
    }
    
    // Close modal when clicking outside
    if (videoModal) {
        videoModal.addEventListener('click', function(e) {
            if (e.target === videoModal) {
                videoModal.classList.remove('active');
                videoPlayer.src = '';
            }
        });
    }
}

// Form Submissions
function initForms() {
    // Newsletter form
    const newsletterForm = document.getElementById('newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = this.querySelector('input[type="email"]').value;
            
            fetch('/api/subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email: email })
            })
            .then(response => response.json())
            .then(data => {
                showNotification(data.message, data.success ? 'success' : 'error');
                if (data.success) {
                    this.reset();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('An error occurred. Please try again.', 'error');
            });
        });
    }
    
    // Contact form
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const name = this.querySelector('input[type="text"]').value;
            const email = this.querySelector('input[type="email"]').value;
            const message = this.querySelector('textarea').value;
            
            fetch('/api/contact', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name: name, email: email, message: message })
            })
            .then(response => response.json())
            .then(data => {
                showNotification(data.message, data.success ? 'success' : 'error');
                if (data.success) {
                    this.reset();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('An error occurred. Please try again.', 'error');
            });
        });
    }
    
    // Giveaway form
    const giveawayForm = document.getElementById('giveaway-form');
    if (giveawayForm) {
        giveawayForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = this.querySelector('input[type="email"]').value;
            
            fetch('/api/enter-giveaway', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email: email })
            })
            .then(response => response.json())
            .then(data => {
                showNotification(data.message, data.success ? 'success' : 'error');
                if (data.success) {
                    this.reset();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('An error occurred. Please try again.', 'error');
            });
        });
    }
}

// ===== WISHLIST AND CART FUNCTIONALITY =====

// Wishlist and Cart functionality
function initWishlistCart() {
    // Wishlist functionality
    document.querySelectorAll('.action-btn.wishlist').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const productCard = this.closest('.product-card');
            const productId = productCard.dataset.productId;
            const productName = productCard.querySelector('.product-title').textContent;
            
            toggleWishlist(productId, productName, this);
        });
    });
    
    // Cart functionality
    document.querySelectorAll('.action-btn.cart').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const productCard = this.closest('.product-card');
            const productId = productCard.dataset.productId;
            const productName = productCard.querySelector('.product-title').textContent;
            const productPrice = productCard.querySelector('.action-btn.cart').textContent.match(/\$([\d.]+)/)[1];
            
            addToCart(productId, productName, productPrice, this);
        });
    });
}

// Toggle wishlist item
function toggleWishlist(productId, productName, button) {
    let wishlist = JSON.parse(localStorage.getItem('wishlist')) || [];
    
    const existingIndex = wishlist.findIndex(item => item.id === productId);
    
    if (existingIndex > -1) {
        // Remove from wishlist
        wishlist.splice(existingIndex, 1);
        button.innerHTML = '<i class="far fa-heart"></i> Wishlist';
        showNotification(`Removed ${productName} from wishlist`, 'info');
    } else {
        // Add to wishlist
        wishlist.push({ id: productId, name: productName, date: new Date().toISOString() });
        button.innerHTML = '<i class="fas fa-heart"></i> In Wishlist';
        showNotification(`Added ${productName} to wishlist`, 'success');
    }
    
    localStorage.setItem('wishlist', JSON.stringify(wishlist));
    updateWishlistIndicator();
}

// Add item to cart
function addToCart(productId, productName, productPrice, button) {
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    
    const existingItem = cart.find(item => item.id === productId);
    
    if (existingItem) {
        existingItem.quantity += 1;
        showNotification(`Increased quantity of ${productName} in cart`, 'info');
    } else {
        cart.push({ 
            id: productId, 
            name: productName, 
            price: parseFloat(productPrice), 
            quantity: 1,
            date: new Date().toISOString()
        });
        showNotification(`Added ${productName} to cart`, 'success');
    }
    
    // Add animation effect
    button.classList.add('adding');
    setTimeout(() => {
        button.classList.remove('adding');
    }, 500);
    
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
}

// Update cart count indicator
function updateCartCount() {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    const totalItems = cart.reduce((total, item) => total + item.quantity, 0);
    
    let cartIndicator = document.getElementById('cart-indicator');
    if (!cartIndicator) {
        // Create cart indicator if it doesn't exist
        const cartLink = document.querySelector('a[href="/cart"]');
        if (cartLink) {
            cartIndicator = document.createElement('span');
            cartIndicator.id = 'cart-indicator';
            cartIndicator.className = 'cart-indicator';
            cartLink.appendChild(cartIndicator);
        }
    }
    
    if (cartIndicator) {
        if (totalItems > 0) {
            cartIndicator.textContent = totalItems;
            cartIndicator.style.display = 'flex';
        } else {
            cartIndicator.style.display = 'none';
        }
    }
}

// Update wishlist indicator
function updateWishlistIndicator() {
    const wishlist = JSON.parse(localStorage.getItem('wishlist')) || [];
    
    let wishlistIndicator = document.getElementById('wishlist-indicator');
    if (!wishlistIndicator) {
        // Create wishlist indicator if it doesn't exist
        const wishlistLink = document.querySelector('a[href="/wishlist"]');
        if (wishlistLink) {
            wishlistIndicator = document.createElement('span');
            wishlistIndicator.id = 'wishlist-indicator';
            wishlistIndicator.className = 'wishlist-indicator';
            wishlistLink.appendChild(wishlistIndicator);
        }
    }
    
    if (wishlistIndicator) {
        if (wishlist.length > 0) {
            wishlistIndicator.textContent = wishlist.length;
            wishlistIndicator.style.display = 'flex';
        } else {
            wishlistIndicator.style.display = 'none';
        }
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => {
        notification.remove();
    });
    
    // Create new notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button class="notification-close">&times;</button>
    `;
    
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Auto hide after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
    
    // Close button event
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    });
}