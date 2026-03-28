// FreshMart Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Update cart count badge
    updateCartCount();
});

// Update cart count via API
function updateCartCount() {
    const cartBadge = document.querySelector('.cart-badge');
    if (cartBadge) {
        fetch('/api/cart/count')
            .then(response => response.json())
            .then(data => {
                cartBadge.textContent = data.count;
                if (data.count === 0) {
                    cartBadge.style.display = 'none';
                } else {
                    cartBadge.style.display = 'block';
                }
            })
            .catch(error => console.error('Error fetching cart count:', error));
    }
}

// Quantity increment/decrement for product detail
function incrementQty() {
    const input = document.getElementById('quantity');
    if (input) {
        const max = parseInt(input.max);
        const current = parseInt(input.value);
        if (current < max) {
            input.value = current + 1;
        }
    }
}

function decrementQty() {
    const input = document.getElementById('quantity');
    if (input) {
        const current = parseInt(input.value);
        if (current > 1) {
            input.value = current - 1;
        }
    }
}

// Confirm delete action
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item?');
}

// Format price display
function formatPrice(price) {
    return '$' + parseFloat(price).toFixed(2);
}

// Show loading spinner
function showLoading(element) {
    element.innerHTML = '<span class="loading"></span>';
    element.disabled = true;
}

// Hide loading spinner
function hideLoading(element, originalText) {
    element.innerHTML = originalText;
    element.disabled = false;
}

// Handle form submission with loading state
function handleFormSubmit(form, submitBtn) {
    const originalText = submitBtn.innerHTML;
    showLoading(submitBtn);
    
    form.addEventListener('submit', function() {
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
        submitBtn.disabled = true;
    });
}

// Initialize tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
});

// Initialize popovers
var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
});

// Search form enhancement
const searchForm = document.querySelector('form[action*="index"]');
if (searchForm) {
    const searchInput = searchForm.querySelector('input[name="search"]');
    if (searchInput) {
        searchInput.addEventListener('focus', function() {
            this.parentElement.classList.add('shadow-sm');
        });
        searchInput.addEventListener('blur', function() {
            this.parentElement.classList.remove('shadow-sm');
        });
    }
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add to cart animation
function animateAddToCart(button) {
    button.classList.add('btn-success');
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="bi bi-check-lg me-1"></i>Added!';
    
    setTimeout(() => {
        button.innerHTML = originalText;
    }, 1500);
}

// Category filter enhancement
const categoryLinks = document.querySelectorAll('.category-card, .category-card-large');
categoryLinks.forEach(link => {
    link.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-5px)';
    });
    link.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
    });
});
