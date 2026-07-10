# 🛍️ Mahi Store — Full-Stack E-Commerce Platform

> A production-ready, full-stack e-commerce platform with dual buyer/seller roles, Razorpay payment integration, JWT authentication, and a real-time seller analytics dashboard.

---

## 📖 About

Mahi Store is a complete e-commerce web application built from scratch, featuring a **Django REST Framework** backend and a **React + Vite** frontend. It supports two distinct user roles — **Buyers** (browse, cart, checkout, track orders) and **Sellers** (list products, manage inventory, view analytics) — with a clean separation of concerns enforced at the API permission level.

The project demonstrates real-world engineering practices: HMAC-based payment verification, JWT blacklisting on password reset, soft-delete patterns, per-user cart isolation, address snapshots at checkout, and a 73+ test suite covering security-critical flows.

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend Framework** | React 19 + Vite 8 |
| **Frontend Routing** | React Router v7 |
| **Frontend HTTP Client** | Axios |
| **Frontend Charts** | Recharts |
| **Frontend Animations** | Framer Motion |
| **Frontend Icons** | Lucide React |
| **Backend Framework** | Django 4.2 + Django REST Framework 3.16 |
| **Authentication** | JWT via `djangorestframework-simplejwt` + custom blacklisting |
| **Payment Gateway** | Razorpay (HMAC-SHA256 signature verification) |
| **Database (Production)** | PostgreSQL (via `psycopg2-binary`) |
| **Database (Local Dev)** | SQLite |
| **ORM Audit Trails** | `django-simple-history` |
| **Environment Config** | `django-environ` |
| **Static Files (Production)** | WhiteNoise |
| **WSGI Server (Production)** | Gunicorn |
| **Frontend Deployment** | Vercel |
| **Backend Deployment** | Render (with managed PostgreSQL) |
| **CORS** | `django-cors-headers` |
| **Image Handling** | Pillow |

---

## ✨ Key Features

### 👤 User & Auth
- **Dual role registration** — separate buyer and seller registration flows with auto-created profiles
- **JWT authentication** — custom token pair with role embedded in payload
- **Password reset via JWT** — single-use token with 1-hour expiry; all active JWT sessions are invalidated on successful reset
- **Soft-delete accounts** — deleted users have emails/usernames anonymised, enabling clean re-registration
- **Profile management** — avatar upload (buyers), store logo + description (sellers)

### 🛒 Shopping
- **Product catalog** — full search and multi-criteria filtering (category, price range, seller)
- **Product images** — multiple images per product with a primary flag and ordering
- **Shopping cart** — persistent per-user cart (UUID primary key), add/update/remove items, cross-user access prevention
- **Secure checkout** — shipping address selection with snapshot of address text at time of order
- **Razorpay integration** — create Razorpay order → frontend payment modal → backend HMAC-SHA256 verification → order confirmation

### 📦 Order Management
- **Order tracking** — buyers can track order and individual item statuses (`Pending`, `Completed`, `Cancelled`)
- **Seller order fulfilment** — sellers can update status of their own order items
- **Historical records** — full audit trail on `Order`, `OrderItem`, and `Address` via `django-simple-history`
- **Address management** — CRUD with default address support (enforced at model save level)

### 📊 Seller Dashboard
- **Real-time analytics** — total revenue, total orders, pending orders count, product count
- **Low stock alerts** — products with stock < 5 flagged automatically
- **Top 5 best sellers** — ranked by quantity sold, with total sales value
- **Monthly revenue trend** — last 6 months, grouped by calendar month
- **My Products** — CRUD for seller's own products with image management
- **Received Orders** — view and update status of orders containing seller's products

### ⭐ Reviews & Ratings
- **Product reviews** — buyers can leave reviews and ratings on products
- **Review management** — edit/delete own reviews with seller-level read access

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                  FRONTEND                       │
│            React 19 + Vite (Vercel)             │
│                                                 │
│  Pages: Home, Products, ProductDetail,          │
│         Checkout, Profile, Register, Login,     │
│         Seller/Dashboard, Seller/MyProducts,    │
│         Seller/ReceivedOrders, ForgotPassword   │
│                                                 │
│  Context: AuthContext (JWT tokens, user role)   │
│  HTTP:    Axios (Bearer token headers)          │
└──────────────────┬──────────────────────────────┘
                   │ HTTPS REST API
                   ▼
┌─────────────────────────────────────────────────┐
│                  BACKEND                        │
│        Django REST Framework (Render)           │
│                                                 │
│  Apps:                                          │
│  ├── authentication  (JWT, profiles, reset)     │
│  ├── products        (catalog, categories)      │
│  ├── orders          (cart, orders, payments)   │
│  ├── dashboard       (API dir, seller stats)    │
│  └── reviews         (ratings, reviews)         │
│                                                 │
│  Middleware: CORS, WhiteNoise, SimpleJWT        │
└──────┬──────────────────────┬───────────────────┘
       │ Django ORM           │ Razorpay API calls
       ▼                      ▼
┌─────────────┐      ┌─────────────────────────┐
│  PostgreSQL │      │   Razorpay Gateway      │
│  (Render)   │      │                         │
│             │      │  1. Create order (API)  │
│  Tables:    │      │  2. Frontend modal      │
│  - users    │      │  3. Verify signature    │
│  - products │      │     (HMAC-SHA256)       │
│  - orders   │      │  4. Mark Payment Paid   │
│  - payments │      └─────────────────────────┘
│  - carts    │
│  - reviews  │
│  - history* │
└─────────────┘

* django-simple-history audit tables for Order, OrderItem, Address, Product
```

### Razorpay Payment Flow

```
Browser                     Backend                    Razorpay
   │                           │                           │
   │── POST /payments/create/ ─►│                           │
   │                           │── Create Order ──────────►│
   │                           │◄─ razorpay_order_id ──────│
   │◄── razorpay_order_id ─────│                           │
   │                           │                           │
   │── Open Razorpay Modal ───────────────────────────────►│
   │◄── payment_id + signature ───────────────────────────│
   │                           │                           │
   │── POST /payments/verify/ ─►│                           │
   │                  HMAC-SHA256 verification             │
   │                  (order_id + payment_id → signature)  │
   │                  Mark Payment.status = 'Paid'         │
   │                  Mark Order.status = 'Completed'      │
   │◄── 200 OK, order confirmed│                           │
```

---

## ⚙️ Local Development Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- (Optional) PostgreSQL — SQLite is used by default locally

### 1. Backend Setup

```bash
# Clone the repository
git clone https://github.com/mahi06159/Ecommarce.git
cd Ecommarce

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your values (see table below)

# Run database migrations
python manage.py migrate

# Start the development server
python manage.py runserver
# API available at http://127.0.0.1:8000/
```

#### Required `.env` Variables

| Variable | Example Value | Description |
|---|---|---|
| `SECRET_KEY` | `django-insecure-xxxxxxxxxxxxxxxxxxxx` | Django secret key (generate a new one for production) |
| `DEBUG` | `True` | Set `False` in production |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated list of allowed hosts |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | Frontend origin for CORS |
| `RAZORPAY_KEY_ID` | `rzp_test_XXXXXXXXXXXXXXXX` | Razorpay API key ID (test or live) |
| `RAZORPAY_KEY_SECRET` | `XXXXXXXXXXXXXXXXXXXXXXXX` | Razorpay API key secret |
| `DATABASE_URL` | *(leave blank for SQLite)* | PostgreSQL connection string (production only) |

> **Note:** `DATABASE_URL` is only required for PostgreSQL. If omitted, the app defaults to SQLite for local development.

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
# App available at http://localhost:5173/
```

> Ensure the backend is running at `http://127.0.0.1:8000` before starting the frontend, or update the base URL in `src/api/`.

---

## 📡 API Endpoints

All endpoints are prefixed with `/api/`.

### 🔐 Authentication — `/api/auth/`

| Method | Path | Description | Auth Required |
|---|---|---|---|
| `POST` | `/auth/register/buyer/` | Register a new buyer account | No |
| `POST` | `/auth/register/seller/` | Register a new seller account | No |
| `POST` | `/auth/login/` | Obtain JWT access + refresh tokens | No |
| `POST` | `/auth/token/refresh/` | Refresh access token | No |
| `POST` | `/auth/logout/` | Blacklist refresh token (logout) | Yes |
| `GET/PUT/PATCH/DELETE` | `/auth/profile/` | Retrieve or update authenticated user profile | Yes |
| `POST` | `/auth/password-reset/request/` | Send password reset token via email | No |
| `POST` | `/auth/password-reset/confirm/` | Confirm reset with token + new password | No |

### 📦 Products — `/api/`

| Method | Path | Description | Auth Required |
|---|---|---|---|
| `GET` | `/categories/` | List all categories | No |
| `POST` | `/categories/` | Create a new category | Yes (Seller) |
| `GET/PUT/PATCH/DELETE` | `/categories/<id>/` | Retrieve or manage a category | Partial |
| `GET` | `/products/` | List products (search, filter, paginate) | No |
| `POST` | `/products/` | Create a new product listing | Yes (Seller) |
| `GET` | `/products/dropdown/` | Lightweight product list for dropdowns | Yes (Seller) |
| `GET/PUT/PATCH/DELETE` | `/products/<id>/` | Retrieve or manage a product | Partial |

### 🛒 Cart & Orders — `/api/`

| Method | Path | Description | Auth Required |
|---|---|---|---|
| `GET/POST` | `/cart/` | View cart or add item to cart | Yes |
| `PATCH/DELETE` | `/cart/items/<id>/` | Update quantity or remove cart item | Yes |
| `GET/POST` | `/addresses/` | List or create shipping addresses | Yes |
| `GET/PUT/PATCH/DELETE` | `/addresses/<id>/` | Retrieve or manage an address | Yes |
| `GET/POST` | `/orders/` | List buyer's orders or place a new order | Yes |
| `GET` | `/orders/<id>/` | Retrieve order details with items | Yes |
| `PATCH` | `/orders/items/<id>/status/` | Update order item status (seller only) | Yes (Seller) |

### 💳 Payments — `/api/`

| Method | Path | Description | Auth Required |
|---|---|---|---|
| `POST` | `/payments/create/` | Create a Razorpay order, return `razorpay_order_id` | Yes |
| `POST` | `/payments/verify/` | Verify HMAC signature and mark payment as paid | Yes |

### 📊 Dashboard — `/api/`

| Method | Path | Description | Auth Required |
|---|---|---|---|
| `GET` | `/dashboard/` | API directory listing all available endpoints | No |
| `GET` | `/dashboard/seller-stats/` | Real-time seller analytics (revenue, orders, products, trend) | Yes (Seller) |

### ⭐ Reviews — `/api/`

| Method | Path | Description | Auth Required |
|---|---|---|---|
| `GET/POST` | `/reviews/` | List reviews or submit a new review | Partial |
| `GET/PUT/PATCH/DELETE` | `/reviews/<id>/` | Retrieve or manage a specific review | Partial |

---

## 🧪 Testing

The project includes **73+ backend tests** across all Django apps, using Django REST Framework's `APITestCase`.

### Run All Tests

```bash
# Activate your virtual environment first
source venv/bin/activate

# Run the full test suite
python manage.py test

# Run tests for a specific app
python manage.py test authentication
python manage.py test products
python manage.py test orders
python manage.py test dashboard
python manage.py test reviews

# Verbose output (shows each test name)
python manage.py test --verbosity=2
```

### Test Coverage Areas

| Area | What's Tested |
|---|---|
| **Authentication** | Buyer/seller registration, login, logout, profile CRUD, phone number uniqueness, soft-delete and re-registration flow |
| **Password Reset Security** | Single-use token enforcement, token expiry validation, JWT session invalidation after reset, rejection of reused/invalid tokens |
| **Cart Ownership Isolation** | Cross-user cart access prevention — a buyer cannot view, modify, or delete another buyer's cart items |
| **Payment Signature Verification** | Valid HMAC-SHA256 signature acceptance, tampered/invalid signature rejection, duplicate `razorpay_payment_id` handling (race-condition safety) |
| **Order Logic** | Order creation from cart contents, stock decrement on placement, seller-only item status updates, buyer-only order visibility |
| **Seller Analytics Accuracy** | Revenue calculation excludes cancelled items, correct monthly trend grouping, accurate top-product ranking by quantity |
| **Product Permissions** | Seller-only creation and editing, cross-seller product modification prevention |
| **Reviews** | Review creation by buyers only, edit/delete own review, duplicate review prevention per product per user |

---

## 🔒 Security Highlights

### 1. JWT Blacklisting on Password Reset
When a user resets their password via `password-reset/confirm/`, **all existing JWT refresh tokens are blacklisted** using `simplejwt`'s `OutstandingToken` and `BlacklistedToken` models. No previously issued session can remain valid after a credential change — protecting against account takeover via stolen refresh tokens.

### 2. HMAC-SHA256 Payment Verification
Razorpay payments are verified server-side using HMAC-SHA256 signature validation:
```
expected_signature = HMAC-SHA256(
    key     = RAZORPAY_KEY_SECRET,
    message = razorpay_order_id + "|" + razorpay_payment_id
)
```
Computed vs. received signatures are compared using `hmac.compare_digest` — a constant-time function that prevents timing-based side-channel attacks. Payments are marked `Paid` only after verification succeeds.

### 3. Race-Condition-Safe Duplicate Payment Handling
`Payment.razorpay_payment_id` carries a `unique=True` database constraint. Concurrent duplicate verify requests are handled at the DB level — an `IntegrityError` returns `409 Conflict` instead of processing the payment twice.

### 4. Cross-User Cart Access Prevention
`CartView` and `CartItemUpdateDeleteView` filter all querysets by `request.user`. A user can never read or mutate another user's cart items, regardless of knowing the cart's UUID.

### 5. Role-Based Permissions
Custom permission classes (`IsSellerOrReadOnly`, `IsBuyerOrReadOnly`) are applied at the view level:
- Only **sellers** can create/edit/delete products and update order item statuses
- Only **buyers** can place orders and manage carts
- Seller analytics endpoints reject non-seller requests with `403 Forbidden`

### 6. Address Snapshot at Checkout
At order creation, the full shipping address is **snapshotted** into `Order.shipping_address_text`. Historical orders retain accurate address data even if the user later modifies or deletes the original address record.

---

## 📸 Screenshots

> *Screenshots will be added after UI is finalised. Replace placeholders below with actual images.*

| View | Preview |
|---|---|
| Home / Product Catalog | *(coming soon)* |
| Product Detail + Reviews | *(coming soon)* |
| Shopping Cart | *(coming soon)* |
| Checkout + Razorpay Modal | *(coming soon)* |
| Buyer Order Tracking | *(coming soon)* |
| Seller Analytics Dashboard | *(coming soon)* |
| Seller — My Products | *(coming soon)* |
| Seller — Received Orders | *(coming soon)* |
| Login / Register | *(coming soon)* |

---

## 🚀 Live Demo

| Service | URL |
|---|---|
| **Frontend (Vercel)** | [https://mahi-store-frontend.vercel.app](https://mahi-store-frontend.vercel.app) |
| **Backend API (Render)** | [https://mahi-store-backend.onrender.com](https://mahi-store-backend.onrender.com) |
| **API Directory** | [https://mahi-store-backend.onrender.com/api/dashboard/](https://mahi-store-backend.onrender.com/api/dashboard/) |

---

## 📂 Project Structure

```
mahi-store/
├── authentication/         # User model, JWT views, password reset
├── products/               # Product & category CRUD, image handling
├── orders/                 # Cart, orders, addresses, Razorpay payments
├── dashboard/              # API directory + seller analytics views
├── reviews/                # Product reviews and ratings
├── ecom_project/           # Django settings, URL routing, shared mixins/utils
├── frontend/               # React + Vite SPA
│   └── src/
│       ├── api/            # Axios instance and API call functions
│       ├── components/     # Reusable UI components
│       ├── context/        # AuthContext (JWT + user state management)
│       ├── pages/          # Page components (buyer + seller flows)
│       └── utils/          # Shared utility functions
├── requirements.txt        # Python dependencies
├── render.yaml             # Render.com deployment configuration
└── Procfile                # Gunicorn start command
```

---

## 📜 License

This project is licensed under the **MIT License**. See `LICENSE` for details.

---

## 📬 Contact

- **Name:** Mahi Panara
- **GitHub:** [github.com/mahi06159](https://github.com/mahi06159)
- **LinkedIn:** [linkedin.com/in/mahipanara](https://www.linkedin.com/in/mahipanara/) *(replace/verify with your URL)*
- **Email:** `mahipanara06159@gmail.com` *(replace/verify with your URL)*

---

*Built with ❤️ as a full-stack portfolio project demonstrating real-world Django REST + React engineering.*
