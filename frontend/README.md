# Banking Frontend (React + Tailwind)

Modern banking frontend with glassmorphism UI, gradient backgrounds, responsive layout, JWT auth flow, and Flask API integration.

## Stack

- React + Vite
- Tailwind CSS
- React Router
- Axios
- Recharts

## Features

- Login / Register pages
- Protected Dashboard
- Deposit / Withdraw / Transfer flows
- Transaction History
- Mini Statement
- Responsive Navbar + Sidebar
- Balance cards, charts, notifications
- Dark mode toggle

## Setup

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

## Build

```bash
npm run build
npm run preview
```

## Flask API Expectations

Set `VITE_API_BASE_URL` in `.env`.

Expected endpoints:

- `POST /auth/login`
- `POST /auth/register`
- `GET /dashboard`
- `POST /transactions/deposit`
- `POST /transactions/withdraw`
- `POST /transactions/transfer`
- `GET /transactions/history`
- `GET /transactions/mini-statement`

JWT token should be returned from login payload as `token` (or `access_token`) and is sent as `Authorization: Bearer <token>`.
