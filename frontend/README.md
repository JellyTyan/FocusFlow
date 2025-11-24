# FocusFlow Frontend (Vue 3)

Vue 3 + Vite + TypeScript + Tailwind CSS frontend for FocusFlow.

## 🚀 Quick Start

### Install dependencies
```bash
npm install
```

### Run development server (port 3000)
```bash
npm run dev
```

### Build for production
```bash
npm run build
```

## 🏗 Tech Stack

- **Vue 3** - Composition API + TypeScript
- **Vite** - Fast dev server and build tool
- **Pinia** - State management
- **Vue Router** - Routing
- **Tailwind CSS** - Styling with custom Study Flow design tokens
- **Axios** - HTTP client with cookie-based auth

## 🎨 Design System

### Colors (Study Flow)
- Deep Indigo `#1E2A4A` - Background
- Soft Ice `#F0F4F8` - Cards (5-10% opacity)
- Sea Mint `#66CCB6` - Focus/Interactive
- Soft Coral `#FF8866` - Urgent/Now
- Text Primary `#FFFFFF`
- Text Secondary `#A8B3C4`

### Fonts
- Sans: Inter, Manrope
- Mono: ui-monospace (for timer)

## 📁 Project Structure

```
src/
├── components/       # Reusable components
│   ├── layout/      # Sidebar, Topbar
│   ├── common/      # Buttons, Cards
│   ├── timer/       # Timer components
│   └── chat/        # AI chat components
├── views/           # Page components
│   ├── auth/        # Login, Register
│   ├── dashboard/   # Dashboard, Projects
│   ├── timer/       # Timer page
│   ├── profile/     # Profile edit
│   └── stats/       # Statistics
├── stores/          # Pinia stores
├── router/          # Vue Router config
├── services/        # API services
├── utils/           # Utilities (priority calc)
└── design/          # Design tokens
```

## 🔌 API Integration

Backend runs on `http://localhost:8000` (FastAPI).

Set `VITE_API_BASE` in `.env` to override.

All requests use `withCredentials: true` for cookie-based auth.

## 🧪 Testing

```bash
npm run test
```

## 📝 Environment Variables

Copy `.env.example` to `.env`:

```bash
VITE_API_BASE=http://localhost:8000
```

## 🎯 Features

- ✅ Vue 3 + Vite scaffold
- ✅ Tailwind with Study Flow design tokens
- ✅ Pinia stores (auth, projects, timer, ui)
- ✅ Vue Router with protected routes
- ✅ Landing, Login, Register pages
- ⏳ Dashboard with Bento Grid
- ⏳ Pomodoro timer (25 min)
- ⏳ AI chat panel
- ⏳ Profile edit
- ⏳ Statistics

## 🔐 Authentication

Uses HTTP-only cookies. Frontend sends `withCredentials: true` on all API requests.

On app mount, calls `GET /api/user/me` to restore session.

Protected routes redirect to `/auth/login` if not authenticated.
