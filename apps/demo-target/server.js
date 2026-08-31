import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// In-memory demo store
const products = [
  { id: '1', name: 'Apex Wireless Noise-Cancelling Headphones', price: 299, rating: 4.8, category: 'Audio' },
  { id: '2', name: 'Pro-Stream Ultra 4K Webcam', price: 149, rating: 4.6, category: 'Video' },
  { id: '3', name: 'Quantum Mechanical RGB Keyboard', price: 189, rating: 4.9, category: 'Accessories' },
  { id: '4', name: 'Precision Ergonomic Gaming Mouse', price: 89, rating: 4.7, category: 'Accessories' }
];

// API Endpoints
app.get('/api/products', (req, res) => {
  const query = (req.query.q || '').toString().toLowerCase();
  if (!query) return res.json(products);
  const filtered = products.filter(p => p.name.toLowerCase().includes(query) || p.category.toLowerCase().includes(query));
  res.json(filtered);
});

app.post('/api/login', (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(400).json({ error: 'Email and password are required' });
  }
  if (email === 'admin@example.com' && password === 'password123') {
    return res.json({ success: true, token: 'demo-jwt-token-998822', user: { name: 'Admin User', role: 'admin' } });
  }
  return res.status(401).json({ error: 'Invalid credentials. Try admin@example.com / password123' });
});

app.post('/api/contact', (req, res) => {
  const { name, email, message } = req.body;
  if (!email || !email.includes('@')) {
    return res.status(400).json({ error: 'Invalid email address format' });
  }
  if (!message || message.length < 5) {
    return res.status(400).json({ error: 'Message must be at least 5 characters' });
  }
  return res.json({ success: true, message: 'Your inquiry has been received!' });
});

// INTENTIONAL DEMO BUG: Payment endpoint throws HTTP 500 error to demonstrate real-world failure detection!
app.post('/api/payment', (req, res) => {
  console.log('[DemoTarget] Processing Payment Request:', req.body);
  // Deliberate 500 internal server error
  return res.status(500).json({
    error: 'PaymentGatewayTimeoutException',
    code: 'PAYMENT_PROCESSOR_500',
    message: 'Primary payment gateway timed out while processing credit card tokenization. Connection refused at upstream cluster.'
  });
});

// Serve frontend HTML pages
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>NovaStore — Modern Electronics Sandbox</title>
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: #0f172a; color: #f8fafc; padding-bottom: 60px; }
        nav { display: flex; justify-content: space-between; align-items: center; padding: 18px 48px; background: #1e293b; border-bottom: 1px solid #334155; }
        .logo { font-size: 22px; font-weight: 800; color: #38bdf8; text-decoration: none; display: flex; align-items: center; gap: 8px; }
        .nav-links { display: flex; gap: 24px; align-items: center; }
        .nav-links a { color: #cbd5e1; text-decoration: none; font-weight: 500; transition: color 0.2s; }
        .nav-links a:hover { color: #38bdf8; }
        .cart-badge { background: #3b82f6; color: white; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 700; }
        .hero { text-align: center; padding: 64px 20px; max-width: 800px; margin: 0 auto; }
        .hero h1 { font-size: 44px; font-weight: 800; line-height: 1.2; margin-bottom: 16px; background: linear-gradient(135deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .hero p { font-size: 18px; color: #94a3b8; margin-bottom: 28px; }
        .search-bar { display: flex; max-width: 540px; margin: 0 auto 48px auto; gap: 10px; }
        .search-bar input { flex: 1; padding: 14px 18px; border-radius: 8px; border: 1px solid #334155; background: #1e293b; color: white; font-size: 15px; }
        .search-bar button { padding: 14px 24px; border-radius: 8px; border: none; background: #3b82f6; color: white; font-weight: 600; cursor: pointer; }
        .products-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 24px; max-width: 1100px; margin: 0 auto; padding: 0 20px; }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 24px; display: flex; flex-direction: column; justify-content: space-between; }
        .card h3 { font-size: 18px; font-weight: 700; margin-bottom: 8px; }
        .price { font-size: 22px; font-weight: 800; color: #38bdf8; margin: 12px 0; }
        .btn-add { background: #2563eb; color: white; border: none; padding: 10px 16px; border-radius: 6px; font-weight: 600; cursor: pointer; width: 100%; transition: background 0.2s; }
        .btn-add:hover { background: #1d4ed8; }
        .toast { position: fixed; bottom: 24px; right: 24px; background: #10b981; color: white; padding: 12px 20px; border-radius: 8px; font-weight: 600; display: none; }
      </style>
    </head>
    <body>
      <nav>
        <a href="/" class="logo">⚡ NovaStore</a>
        <div class="nav-links">
          <a href="/" data-testid="nav-home">Home</a>
          <a href="/products" data-testid="nav-products">Products</a>
          <a href="/contact" data-testid="nav-contact">Contact</a>
          <a href="/login" data-testid="nav-login">Sign In</a>
          <a href="/cart" data-testid="nav-cart">Cart <span class="cart-badge" id="cartCount">1</span></a>
        </div>
      </nav>

      <div class="hero">
        <h1>Next-Generation Tech Gear</h1>
        <p>Explore high-performance hardware and developer tools designed for peak efficiency.</p>
        <form class="search-bar" onsubmit="event.preventDefault(); handleSearch();">
          <input type="search" placeholder="Search headphones, keyboards, webcams..." id="searchInput" data-testid="search-input" oninput="handleSearch()" onkeyup="handleSearch()" />
          <button type="submit" data-testid="search-btn">Search</button>
        </form>
      </div>

      <div class="products-grid" id="productsContainer">
        ${products.map(p => `
          <div class="card">
            <div>
              <span style="font-size: 12px; color: #94a3b8; text-transform: uppercase;">${p.category}</span>
              <h3>${p.name}</h3>
              <div style="color: #fbbf24; font-size: 13px;">★ ${p.rating} / 5.0</div>
            </div>
            <div>
              <div class="price">$${p.price}</div>
              <button class="btn-add" data-testid="add-to-cart" onclick="addToCart('${p.name}')">Add to Cart</button>
            </div>
          </div>
        `).join('')}
      </div>

      <div class="toast" id="toast">Item added to cart!</div>

      <script>
        let cartItems = 1;
        function addToCart(name) {
          cartItems++;
          document.getElementById('cartCount').innerText = cartItems;
          const toast = document.getElementById('toast');
          toast.innerText = name + ' added to cart!';
          toast.style.display = 'block';
          setTimeout(() => { toast.style.display = 'none'; }, 2000);
        }
        function handleSearch() {
          const q = (document.getElementById('searchInput').value || '').toLowerCase().trim();
          const cards = document.querySelectorAll('.card');
          let visibleCount = 0;
          cards.forEach(card => {
            if (!q || card.innerText.toLowerCase().includes(q)) {
              card.style.display = 'flex';
              visibleCount++;
            } else {
              card.style.display = 'none';
            }
          });
        }
      </script>
    </body>
    </html>
  `);
});

app.get('/products', (req, res) => {
  res.redirect('/');
});

app.get('/cart', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Shopping Cart — NovaStore</title>
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: #0f172a; color: #f8fafc; }
        nav { display: flex; justify-content: space-between; align-items: center; padding: 18px 48px; background: #1e293b; border-bottom: 1px solid #334155; }
        .logo { font-size: 22px; font-weight: 800; color: #38bdf8; text-decoration: none; }
        .nav-links a { color: #cbd5e1; text-decoration: none; margin-left: 20px; font-weight: 500; }
        .container { max-width: 800px; margin: 48px auto; padding: 0 20px; }
        .cart-box { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 32px; }
        .item-row { display: flex; justify-content: space-between; align-items: center; padding: 16px 0; border-bottom: 1px solid #334155; }
        .btn-checkout { background: #10b981; color: white; border: none; padding: 14px 24px; border-radius: 8px; font-size: 16px; font-weight: 700; width: 100%; margin-top: 24px; cursor: pointer; text-align: center; display: block; text-decoration: none; }
        .btn-checkout:hover { background: #059669; }
      </style>
    </head>
    <body>
      <nav>
        <a href="/" class="logo">⚡ NovaStore</a>
        <div class="nav-links"><a href="/">Home</a><a href="/cart">Cart (1)</a></div>
      </nav>
      <div class="container">
        <div class="cart-box">
          <h2 style="font-size: 24px; margin-bottom: 20px;">Your Shopping Cart</h2>
          <div class="item-row">
            <div>
              <strong style="font-size: 16px;">Apex Wireless Noise-Cancelling Headphones</strong>
              <div style="color: #94a3b8; font-size: 13px; margin-top: 4px;">Qty: 1 • Color: Matte Black</div>
            </div>
            <div style="font-size: 18px; font-weight: 700; color: #38bdf8;">$299.00</div>
          </div>
          <div style="display: flex; justify-content: space-between; margin-top: 20px; font-size: 18px; font-weight: 700;">
            <span>Subtotal:</span>
            <span>$299.00</span>
          </div>
          <a href="/checkout" class="btn-checkout" data-testid="btn-checkout">Proceed to Checkout →</a>
        </div>
      </div>
    </body>
    </html>
  `);
});

app.get('/checkout', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Secure Checkout — NovaStore</title>
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: #0f172a; color: #f8fafc; }
        nav { padding: 18px 48px; background: #1e293b; border-bottom: 1px solid #334155; }
        .logo { font-size: 22px; font-weight: 800; color: #38bdf8; text-decoration: none; }
        .container { max-width: 600px; margin: 48px auto; padding: 0 20px; }
        .form-card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 32px; }
        .form-group { margin-bottom: 18px; }
        label { display: block; font-size: 13px; color: #94a3b8; margin-bottom: 6px; font-weight: 600; text-transform: uppercase; }
        input { width: 100%; padding: 12px 14px; border-radius: 6px; border: 1px solid #334155; background: #0f172a; color: white; font-size: 15px; }
        .btn-pay { background: #ef4444; color: white; border: none; padding: 14px; border-radius: 8px; font-size: 16px; font-weight: 700; width: 100%; cursor: pointer; margin-top: 10px; }
        .btn-pay:hover { background: #dc2626; }
        .error-alert { background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; color: #fca5a5; padding: 14px; border-radius: 8px; margin-top: 20px; display: none; }
      </style>
    </head>
    <body>
      <nav><a href="/" class="logo">⚡ NovaStore Checkout</a></nav>
      <div class="container">
        <div class="form-card">
          <h2 style="margin-bottom: 24px;">Order Summary ($299.00)</h2>
          <div class="form-group">
            <label>Full Name</label>
            <input type="text" id="name" value="Jane Doe" placeholder="Jane Doe" />
          </div>
          <div class="form-group">
            <label>Card Number</label>
            <input type="text" id="cardNumber" value="4242 •••• •••• 4242" placeholder="Card Number" />
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
            <div class="form-group">
              <label>Expiry</label>
              <input type="text" value="12/28" placeholder="MM/YY" />
            </div>
            <div class="form-group">
              <label>CVC</label>
              <input type="text" value="888" placeholder="CVC" />
            </div>
          </div>
          <button class="btn-pay" id="btnPay" data-testid="btn-pay" onclick="submitPayment()">Complete Payment ($299.00)</button>
          <div class="error-alert" id="paymentError">
            <strong>❌ Payment Failed:</strong> Upstream Payment Gateway returned HTTP 500 Internal Server Error. Please contact support.
          </div>
        </div>
      </div>

      <script>
        async function submitPayment() {
          const btn = document.getElementById('btnPay');
          btn.innerText = 'Processing Payment...';
          btn.disabled = true;
          try {
            const resp = await fetch('/api/payment', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ amount: 299, orderId: 'ORD-9912' })
            });
            if (!resp.ok) {
              throw new Error('HTTP ' + resp.status + ' Server Error');
            }
            alert('Payment succeeded!');
          } catch (err) {
            console.error('Payment Processing Fatal Error:', err);
            document.getElementById('paymentError').style.display = 'block';
            btn.innerText = 'Complete Payment ($299.00)';
            btn.disabled = false;
          }
        }
      </script>
    </body>
    </html>
  `);
});

app.get('/login', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Sign In — NovaStore</title>
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: #0f172a; color: #f8fafc; display: flex; align-items: center; justify-content: center; min-height: 100vh; }
        .login-card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 36px; width: 100%; max-width: 420px; }
        .logo { font-size: 24px; font-weight: 800; color: #38bdf8; text-align: center; margin-bottom: 24px; display: block; text-decoration: none; }
        .form-group { margin-bottom: 18px; }
        label { display: block; font-size: 13px; color: #94a3b8; margin-bottom: 6px; font-weight: 600; }
        input { width: 100%; padding: 12px 14px; border-radius: 6px; border: 1px solid #334155; background: #0f172a; color: white; font-size: 15px; }
        .btn-submit { background: #3b82f6; color: white; border: none; padding: 14px; border-radius: 8px; font-size: 16px; font-weight: 700; width: 100%; cursor: pointer; margin-top: 10px; }
        .feedback { margin-top: 16px; padding: 12px; border-radius: 6px; font-size: 14px; display: none; }
        .feedback-error { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }
        .feedback-success { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; }
      </style>
    </head>
    <body>
      <div class="login-card">
        <a href="/" class="logo">⚡ NovaStore Sign In</a>
        <form id="loginForm" onsubmit="handleLogin(event)">
          <div class="form-group">
            <label>Email Address</label>
            <input type="email" id="email" placeholder="admin@example.com" required />
          </div>
          <div class="form-group">
            <label>Password</label>
            <input type="password" id="password" placeholder="••••••••" />
          </div>
          <button type="submit" class="btn-submit" data-testid="btn-login-submit">Sign In</button>
        </form>
        <div id="feedback" class="feedback"></div>
      </div>

      <script>
        async function handleLogin(e) {
          e.preventDefault();
          const email = document.getElementById('email').value;
          const password = document.getElementById('password').value;
          const fb = document.getElementById('feedback');

          if (!password) {
            fb.className = 'feedback feedback-error';
            fb.innerText = 'Password is required to authenticate.';
            fb.style.display = 'block';
            return;
          }

          try {
            const resp = await fetch('/api/login', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ email, password })
            });
            const data = await resp.json();
            if (resp.ok) {
              fb.className = 'feedback feedback-success';
              fb.innerText = 'Welcome back! Authentication successful.';
              fb.style.display = 'block';
              setTimeout(() => { window.location.href = '/'; }, 1000);
            } else {
              fb.className = 'feedback feedback-error';
              fb.innerText = data.error || 'Login failed';
              fb.style.display = 'block';
            }
          } catch (err) {
            fb.className = 'feedback feedback-error';
            fb.innerText = 'Network request failed';
            fb.style.display = 'block';
          }
        }
      </script>
    </body>
    </html>
  `);
});

app.get('/contact', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Contact Us — NovaStore</title>
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: #0f172a; color: #f8fafc; }
        nav { padding: 18px 48px; background: #1e293b; border-bottom: 1px solid #334155; }
        .logo { font-size: 22px; font-weight: 800; color: #38bdf8; text-decoration: none; }
        .container { max-width: 600px; margin: 48px auto; padding: 0 20px; }
        .form-card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 32px; }
        .form-group { margin-bottom: 18px; }
        label { display: block; font-size: 13px; color: #94a3b8; margin-bottom: 6px; font-weight: 600; }
        input, textarea { width: 100%; padding: 12px 14px; border-radius: 6px; border: 1px solid #334155; background: #0f172a; color: white; font-size: 15px; }
        .btn-submit { background: #3b82f6; color: white; border: none; padding: 14px; border-radius: 8px; font-size: 16px; font-weight: 700; width: 100%; cursor: pointer; }
        .feedback { margin-top: 16px; padding: 12px; border-radius: 6px; display: none; }
        .feedback-error { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }
        .feedback-success { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; }
      </style>
    </head>
    <body>
      <nav><a href="/" class="logo">⚡ NovaStore Contact</a></nav>
      <div class="container">
        <div class="form-card">
          <h2 style="margin-bottom: 24px;">Send us a message</h2>
          <form id="contactForm" onsubmit="handleContact(event)">
            <div class="form-group">
              <label>Your Name</label>
              <input type="text" id="name" placeholder="John Smith" required />
            </div>
            <div class="form-group">
              <label>Email Address</label>
              <input type="email" id="email" placeholder="john@example.com" required />
            </div>
            <div class="form-group">
              <label>Inquiry Message</label>
              <textarea id="message" rows="4" placeholder="How can we assist you?" required></textarea>
            </div>
            <button type="submit" class="btn-submit" data-testid="btn-contact-submit">Submit Message</button>
          </form>
          <div id="feedback" class="feedback"></div>
        </div>
      </div>

      <script>
        async function handleContact(e) {
          e.preventDefault();
          const name = document.getElementById('name').value;
          const email = document.getElementById('email').value;
          const message = document.getElementById('message').value;
          const fb = document.getElementById('feedback');

          if (!email.includes('@')) {
            fb.className = 'feedback feedback-error';
            fb.innerText = 'Please enter a valid email address.';
            fb.style.display = 'block';
            return;
          }

          try {
            const resp = await fetch('/api/contact', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ name, email, message })
            });
            const data = await resp.json();
            if (resp.ok) {
              fb.className = 'feedback feedback-success';
              fb.innerText = data.message || 'Message sent!';
              fb.style.display = 'block';
            } else {
              fb.className = 'feedback feedback-error';
              fb.innerText = data.error || 'Failed to submit form.';
              fb.style.display = 'block';
            }
          } catch (err) {
            fb.className = 'feedback feedback-error';
            fb.innerText = 'Network error occurred.';
            fb.style.display = 'block';
          }
        }
      </script>
    </body>
    </html>
  `);
});

app.listen(PORT, () => {
  console.log(`[DemoTarget] NovaStore Sandbox target server running on http://localhost:${PORT}`);
});
