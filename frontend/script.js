// API base URL
const API_BASE = 'http://localhost:5000/api';

// Global variables
let cart = [];
let products = [];
let user = null;
let token = localStorage.getItem('token') || null;

// Sample product data
const sampleProducts = [
    {
        id: 1,
        name: "Organic Bananas",
        price: 2.99,
        category: "Fruits & Vegetables",
        icon: "fas fa-apple-alt",
        description: "Fresh organic bananas, perfect for smoothies"
    },
    {
        id: 2,
        name: "Whole Grain Bread",
        price: 3.49,
        category: "Bakery & Bread",
        icon: "fas fa-bread-slice",
        description: "Freshly baked whole grain bread"
    },
    {
        id: 3,
        name: "Farm Fresh Eggs",
        price: 4.99,
        category: "Dairy & Eggs",
        icon: "fas fa-egg",
        description: "Farm fresh organic eggs, 12 count"
    },
    {
        id: 4,
        name: "Chicken Breast",
        price: 8.99,
        category: "Meat & Fish",
        icon: "fas fa-drumstick-bite",
        description: "Premium boneless chicken breast"
    },
    {
        id: 5,
        name: "Sparkling Water",
        price: 1.99,
        category: "Beverages",
        icon: "fas fa-wine-bottle",
        description: "Refreshing sparkling water"
    },
    {
        id: 6,
        name: "Dark Chocolate",
        price: 3.99,
        category: "Snacks",
        icon: "fas fa-cookie-bite",
        description: "Premium dark chocolate bar"
    },
    {
        id: 7,
        name: "Vitamin C Supplements",
        price: 12.99,
        category: "Health & Beauty",
        icon: "fas fa-pills",
        description: "High-potency vitamin C supplements"
    },
    {
        id: 8,
        name: "Baby Formula",
        price: 24.99,
        category: "Baby Care",
        icon: "fas fa-baby",
        description: "Premium baby formula, stage 1"
    }
];

// DOM Elements
const cartSidebar = document.getElementById('cartSidebar');
const cartOverlay = document.getElementById('cartOverlay');
const closeCart = document.getElementById('closeCart');
const cartItems = document.getElementById('cartItems');
const cartCount = document.querySelector('.cart-count');
const totalAmount = document.querySelector('.total-amount');
const productGrid = document.getElementById('productGrid');

// --- API Helpers ---
async function apiGet(path, auth = false) {
    const headers = { 'Content-Type': 'application/json' };
    if (auth && token) headers['Authorization'] = 'Bearer ' + token;
    const res = await fetch(API_BASE + path, { headers });
    if (!res.ok) throw new Error(await res.text());
    return await res.json();
}

async function apiPost(path, data, auth = false) {
    const headers = { 'Content-Type': 'application/json' };
    if (auth && token) headers['Authorization'] = 'Bearer ' + token;
    const res = await fetch(API_BASE + path, {
        method: 'POST',
        headers,
        body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error(await res.text());
    return await res.json();
}

// --- Auth ---
async function registerUser(email, password, name) {
    const data = await apiPost('/auth/register', { email, password, name });
    token = data.token;
    user = data.user;
    localStorage.setItem('token', token);
    showNotification('Registration successful!');
}

async function loginUser(email, password) {
    const data = await apiPost('/auth/login', { email, password });
    token = data.token;
    user = data.user;
    localStorage.setItem('token', token);
    showNotification('Login successful!');
}

function logoutUser() {
    token = null;
    user = null;
    localStorage.removeItem('token');
    showNotification('Logged out.');
}

// --- Product Fetch ---
async function loadProducts() {
    try {
        showLoading();
        products = await apiGet('/products');
        renderProducts();
    } catch (e) {
        productGrid.innerHTML = `<div style="color:#f00; padding:40px;">Failed to load products.<br>${e.message}</div>`;
    }
}

// --- Cart/Order ---
async function placeOrder() {
    if (!user || !token) {
        showNotification('Please login to place an order.');
        return;
    }
    if (cart.length === 0) {
        showNotification('Cart is empty.');
        return;
    }
    // For demo, use a static address
    const delivery_address = user.address || '123 Main St, New York, NY';
    const items = cart.map(item => ({ product_id: item.id, quantity: item.quantity }));
    try {
        const res = await apiPost('/orders', { items, delivery_address }, true);
        showNotification('Order placed! ETA: ' + (res.estimated_delivery_time || 'soon'));
        cart = [];
        updateCartDisplay();
    } catch (e) {
        showNotification('Order failed: ' + e.message);
    }
}

// --- UI Logic (rest of your code, with product loading and cart logic updated) ---
function renderProducts() {
    productGrid.innerHTML = '';
    products.forEach(product => {
        const productCard = createProductCard(product);
        productGrid.appendChild(productCard);
    });
}

function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card fade-in-up';
    card.innerHTML = `
        <div class="product-image">
            <i class="${product.icon || 'fas fa-box'}"></i>
        </div>
        <div class="product-info">
            <h3>${product.name}</h3>
            <p>${product.description || ''}</p>
            <div class="product-price">$${product.price.toFixed(2)}</div>
            <button class="add-to-cart" onclick="addToCart(${product.id})">
                <i class="fas fa-plus"></i>
                Add to Cart
            </button>
        </div>
    `;
    return card;
}

function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    const existingItem = cart.find(item => item.id === productId);
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({ ...product, quantity: 1 });
    }
    updateCartDisplay();
    showNotification(`${product.name} added to cart!`);
    const cartButton = document.querySelector('.btn-primary');
    cartButton.style.transform = 'scale(1.1)';
    setTimeout(() => { cartButton.style.transform = 'scale(1)'; }, 200);
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    updateCartDisplay();
}

function updateQuantity(productId, change) {
    const item = cart.find(item => item.id === productId);
    if (!item) return;
    item.quantity += change;
    if (item.quantity <= 0) {
        removeFromCart(productId);
    } else {
        updateCartDisplay();
    }
}

function updateCartDisplay() {
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    cartCount.textContent = totalItems;
    cartItems.innerHTML = '';
    if (cart.length === 0) {
        cartItems.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #666;">
                <i class="fas fa-shopping-cart" style="font-size: 48px; margin-bottom: 20px; color: #333;"></i>
                <p>Your cart is empty</p>
            </div>
        `;
    } else {
        cart.forEach(item => {
            const cartItem = createCartItem(item);
            cartItems.appendChild(cartItem);
        });
    }
    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    totalAmount.textContent = `$${total.toFixed(2)}`;
}

function createCartItem(item) {
    const cartItem = document.createElement('div');
    cartItem.className = 'cart-item';
    cartItem.innerHTML = `
        <div class="cart-item-image">
            <i class="${item.icon || 'fas fa-box'}"></i>
        </div>
        <div class="cart-item-info">
            <div class="cart-item-name">${item.name}</div>
            <div class="cart-item-price">$${item.price.toFixed(2)}</div>
        </div>
        <div class="cart-item-quantity">
            <button class="quantity-btn" onclick="updateQuantity(${item.id}, -1)">-</button>
            <span>${item.quantity}</span>
            <button class="quantity-btn" onclick="updateQuantity(${item.id}, 1)">+</button>
        </div>
    `;
    return cartItem;
}

// --- Event Listeners ---
document.addEventListener('DOMContentLoaded', function() {
    loadProducts();
    setupEventListeners();
    setupAnimations();
    updateCartDisplay();
});

function setupEventListeners() {
    const cartButton = document.querySelector('.btn-primary');
    cartButton.addEventListener('click', toggleCart);
    closeCart.addEventListener('click', toggleCart);
    cartOverlay.addEventListener('click', toggleCart);
    // Cart checkout
    document.querySelector('.checkout-btn').addEventListener('click', placeOrder);
    // Search functionality
    const searchInput = document.querySelector('.search-bar input');
    const searchBtn = document.querySelector('.search-btn');
    
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
    
    searchBtn.addEventListener('click', performSearch);
    
    // Navigation
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            navItems.forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Category cards
    const categoryCards = document.querySelectorAll('.category-card');
    categoryCards.forEach(card => {
        card.addEventListener('click', function() {
            const category = this.querySelector('span').textContent;
            filterByCategory(category);
        });
    });
    
    // Smooth scrolling for anchor links
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
}

function toggleCart() {
    cartSidebar.classList.toggle('open');
    cartOverlay.classList.toggle('open');
    document.body.style.overflow = cartSidebar.classList.contains('open') ? 'hidden' : '';
}

function performSearch() {
    const searchTerm = document.querySelector('.search-bar input').value.toLowerCase();
    
    if (searchTerm.trim() === '') {
        renderProducts();
        return;
    }
    
    const filteredProducts = products.filter(product => 
        product.name.toLowerCase().includes(searchTerm) ||
        product.description.toLowerCase().includes(searchTerm) ||
        product.category.toLowerCase().includes(searchTerm)
    );
    
    renderFilteredProducts(filteredProducts);
}

function renderFilteredProducts(filteredProducts) {
    productGrid.innerHTML = '';
    
    if (filteredProducts.length === 0) {
        productGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #666;">
                <i class="fas fa-search" style="font-size: 48px; margin-bottom: 20px; color: #333;"></i>
                <p>No products found matching your search</p>
            </div>
        `;
        return;
    }
    
    filteredProducts.forEach(product => {
        const productCard = createProductCard(product);
        productGrid.appendChild(productCard);
    });
}

function filterByCategory(category) {
    const filteredProducts = products.filter(product => 
        product.category === category
    );
    
    renderFilteredProducts(filteredProducts);
    
    // Update navigation
    document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
    document.querySelector('.nav-item:nth-child(2)').classList.add('active'); // Trending
}

function setupAnimations() {
    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.category-card, .product-card, .tracking-step').forEach(el => {
        observer.observe(el);
    });
    
    // MFU tracking animation
    animateTrackingSteps();
}

function animateTrackingSteps() {
    const steps = document.querySelectorAll('.tracking-step');
    let currentStep = 0;
    
    setInterval(() => {
        steps.forEach((step, index) => {
            step.classList.remove('active');
        });
        
        steps[currentStep].classList.add('active');
        currentStep = (currentStep + 1) % steps.length;
    }, 2000);
}

function showNotification(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #8b5cf6, #a855f7);
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.3);
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        font-weight: 500;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Animate out and remove
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Escape key to close cart
    if (e.key === 'Escape' && cartSidebar.classList.contains('open')) {
        toggleCart();
    }
    
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.querySelector('.search-bar input').focus();
    }
});

// Performance optimization: Debounce search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Apply debouncing to search
const debouncedSearch = debounce(performSearch, 300);
document.querySelector('.search-bar input').addEventListener('input', debouncedSearch);

// Add loading states
function showLoading() {
    productGrid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 40px;">
            <div class="loading-spinner"></div>
            <p style="margin-top: 20px; color: #666;">Loading products...</p>
        </div>
    `;
}

// Add CSS for loading spinner
const style = document.createElement('style');
style.textContent = `
    .loading-spinner {
        width: 40px;
        height: 40px;
        border: 3px solid #333;
        border-top: 3px solid #8b5cf6;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);

// Export functions for global access
window.addToCart = addToCart;
window.updateQuantity = updateQuantity;
window.removeFromCart = removeFromCart; 
window.registerUser = registerUser;
window.loginUser = loginUser;
window.logoutUser = logoutUser; 