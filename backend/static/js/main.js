// ===== AURA FOODS — Main JavaScript =====

// Cart Management
let cart = JSON.parse(localStorage.getItem('auraCart') || '[]');

function saveCart() {
    localStorage.setItem('auraCart', JSON.stringify(cart));
    updateCartCount();
}

function updateCartCount() {
    const count = cart.reduce((sum, item) => sum + item.qty, 0);
    document.querySelectorAll('#cartCount').forEach(el => el.textContent = count);
}

function addToCart(productId, name, price, image, weight) {
    const existing = cart.find(item => item.id === productId && item.weight === weight);
    if (existing) {
        existing.qty += 1;
    } else {
        cart.push({ id: productId, name, price, image, weight, qty: 1 });
    }
    saveCart();
    showToast(`${name} added to cart!`);
}

function removeFromCart(productId, weight) {
    cart = cart.filter(item => !(item.id === productId && item.weight === weight));
    saveCart();
    renderCart();
}

function updateQty(productId, weight, delta) {
    const item = cart.find(i => i.id === productId && i.weight === weight);
    if (item) {
        item.qty = Math.max(1, item.qty + delta);
        saveCart();
        renderCart();
    }
}

function renderCart() {
    const container = document.getElementById('cartItems');
    const summary = document.getElementById('cartSummary');
    const empty = document.getElementById('emptyCart');
    if (!container) return;

    if (cart.length === 0) {
        if (empty) empty.style.display = 'block';
        if (container) container.style.display = 'none';
        if (summary) summary.style.display = 'none';
        return;
    }

    if (empty) empty.style.display = 'none';
    if (container) container.style.display = 'flex';
    if (summary) summary.style.display = 'block';

    container.innerHTML = cart.map(item => `
        <div class="cart-item fade-in">
            <img src="${item.image}" alt="${item.name}" class="cart-item-img" loading="lazy">
            <div class="cart-item-info">
                <div class="cart-item-name">${item.name}</div>
                <div class="cart-item-price">Rs.${item.price}</div>
                <div class="cart-item-qty">
                    <button class="qty-btn" onclick="updateQty('${item.id}','${item.weight}',-1)">−</button>
                    <span class="qty-value">${item.qty}</span>
                    <button class="qty-btn" onclick="updateQty('${item.id}','${item.weight}',1)">+</button>
                    <button onclick="removeFromCart('${item.id}','${item.weight}')" style="margin-left:1rem;background:none;border:none;color:#c0392b;cursor:pointer;font-size:.8125rem">Remove</button>
                </div>
            </div>
        </div>
    `).join('');

    const subtotal = cart.reduce((sum, i) => sum + i.price * i.qty, 0);
    const delivery = subtotal >= 500 ? 0 : 150;
    const total = subtotal + delivery;

    document.getElementById('cartSubtotal').textContent = `Rs.${subtotal.toLocaleString()}`;
    document.getElementById('cartDelivery').textContent = delivery === 0 ? 'Free' : `Rs.${delivery}`;
    document.getElementById('cartTotal').textContent = `Rs.${total.toLocaleString()}`;

    const checkoutBtn = document.getElementById('checkoutBtn');
    if (checkoutBtn) {
        checkoutBtn.href = `/checkout?total=${total}`;
    }
}

function showToast(message) {
    let toast = document.getElementById('toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast';
        toast.className = 'toast';
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add('show');
    clearTimeout(toast._timeout);
    toast._timeout = setTimeout(() => toast.classList.remove('show'), 2500);
}

// Mobile Menu Toggle
function toggleMenu() {
    document.querySelector('.nav-links').classList.toggle('active');
}

// Tab Switching
function switchTab(tabGroup, tabName) {
    document.querySelectorAll(`[data-tab-group="${tabGroup}"]`).forEach(el => {
        el.classList.toggle('active', el.dataset.tab === tabName);
    });
}

// Quantity on Product Page
function changeQty(delta) {
    const input = document.getElementById('qtyInput');
    if (input) {
        const val = Math.max(1, parseInt(input.textContent || '1') + delta);
        input.textContent = val;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    updateCartCount();
    renderCart();

    // Close mobile menu on link click
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            document.querySelector('.nav-links').classList.remove('active');
        });
    });

    // Stagger fade-up animations
    document.querySelectorAll('.fade-up').forEach((el, i) => {
        el.style.animationDelay = `${i * 0.1}s`;
    });
});
