# Mahi Store — Project Summary

A production-deployed, full-stack e-commerce platform (Django REST + React + Vite) demonstrating end-to-end feature ownership across authentication, payments, analytics, and testing.

---

## Technical Highlights

- **Built a dual-role e-commerce platform** (Buyer/Seller) with Django REST Framework and React 19 + Vite, featuring JWT-based auth with role-embedded tokens, protected routes, and role-specific UIs — from a public product catalog to a private seller analytics dashboard rendered with Recharts.

- **Implemented secure Razorpay payment integration** using HMAC-SHA256 server-side signature verification (`hmac.compare_digest` for constant-time comparison), with a `unique=True` database constraint on `razorpay_payment_id` to prevent race-condition duplicate payments and `IntegrityError`-based `409 Conflict` handling.

- **Engineered a stateful JWT security model**: on password reset, all active `OutstandingToken` records are bulk-blacklisted via `simplejwt`, invalidating every existing session — preventing account takeover via stolen refresh tokens even after a credential change.

- **Designed strict data isolation at the API layer**: per-user cart filtering prevents cross-user cart access regardless of known UUIDs; custom `IsSellerOrReadOnly` / `IsBuyerOrReadOnly` permission classes enforce role boundaries; order address text is snapshotted at checkout to preserve historical accuracy independent of future address mutations.

- **Built a real-time seller analytics API** using complex Django ORM queries — `annotate`, `TruncMonth`, `Sum(F('price') * F('quantity'))` — delivering total revenue (excluding cancelled items), top-5 best-selling products, and a 6-month monthly revenue trend in a single authenticated endpoint.

- **Wrote 73+ backend tests** with `APITestCase` covering security-critical paths: HMAC signature verification (valid + tampered), JWT invalidation on password reset, cart ownership isolation, duplicate payment handling, seller analytics accuracy, and role-based permission enforcement across all apps.

---

## Stack

**Backend:** Django 4.2, Django REST Framework, SimpleJWT, django-simple-history, PostgreSQL, Gunicorn, WhiteNoise, Render
**Frontend:** React 19, Vite 8, React Router v7, Axios, Recharts, Framer Motion, Vercel
**Integrations:** Razorpay payment gateway

---

## Links

- **Live Demo (Frontend):** [https://mahi-store-frontend.vercel.app](https://mahi-store-frontend.vercel.app)
- **API URL (Backend):** [https://mahi-store-backend.onrender.com](https://mahi-store-backend.onrender.com)
- **GitHub Repository:** [https://github.com/mahi06159/Ecommarce](https://github.com/mahi06159/Ecommarce)
