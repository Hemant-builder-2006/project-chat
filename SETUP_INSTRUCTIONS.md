# Project Setup Instructions

## Phase 1: Vite Project Setup

### 1. Create Vite Project with TypeScript

Run the following commands in your terminal:

```powershell
# Create a new Vite project with React and TypeScript template
npm create vite@latest frontend -- --template react-ts

# Navigate to the project directory
cd frontend

# Install base dependencies
npm install
```

### 2. Install Core Dependencies

```powershell
# Install routing and HTTP client
npm install react-router-dom axios jwt-decode

# Install state management (using Zustand - lightweight and simple)
npm install zustand

# Install Tailwind CSS and its dependencies
npm install -D tailwindcss postcss autoprefixer

# Initialize Tailwind CSS
npx tailwindcss init -p
```

### 3. Install Additional Development Dependencies

```powershell
# Install type definitions
npm install -D @types/node
```

### Why These Technologies?

**Vite Benefits:**
- ⚡ Lightning-fast HMR (Hot Module Replacement) during development
- 🎯 Optimized production builds with Rollup
- 🔧 Zero-config for TypeScript and modern features
- 📦 Much faster than Create React App

**Tailwind CSS Benefits:**
- 🎨 Utility-first approach for rapid UI development
- 📱 Built-in responsive design utilities
- 🌙 Easy dark mode implementation
- 🔧 Highly customizable design system
- 📦 Purges unused CSS in production for minimal bundle size

**Zustand for State Management:**
- 🪶 Lightweight (~1KB)
- 🎯 Simple API with minimal boilerplate
- 🔄 Works seamlessly with React hooks
- 🧪 Easy to test and debug

## Environment Variables

Create a `.env` file in the frontend root directory:

```env
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000
```

## Project Structure

```
frontend/
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── ProtectedRoute.tsx
│   │   ├── AppLayout.tsx
│   │   ├── GroupList.tsx
│   │   └── ...
│   ├── contexts/          # React contexts
│   │   └── AuthContext.tsx
│   ├── hooks/             # Custom React hooks
│   │   ├── useWebSocket.ts
│   │   ├── useGroups.ts
│   │   └── ...
│   ├── pages/             # Page components
│   │   ├── LoginPage.tsx
│   │   ├── RegistrationPage.tsx
│   │   └── ChatPage.tsx
│   ├── services/          # API and external services
│   │   └── api.ts
│   ├── types/             # TypeScript type definitions
│   │   └── index.ts
│   ├── App.tsx            # Main app component with routing
│   ├── main.tsx           # Entry point
│   └── index.css          # Global styles with Tailwind imports
├── public/                # Static assets
├── .env                   # Environment variables
├── tailwind.config.js     # Tailwind configuration
├── postcss.config.js      # PostCSS configuration
├── tsconfig.json          # TypeScript configuration
└── vite.config.ts         # Vite configuration
```
