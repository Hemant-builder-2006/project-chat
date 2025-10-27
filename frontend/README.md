# Workspace Frontend

A modern, real-time collaboration workspace built with React, TypeScript, and Vite. Features a Discord-style 3-column dark theme layout with groups, channels, and real-time messaging.

## 🚀 Features Implemented

### Phase 1: Authentication & Setup ✅
- **Vite + React + TypeScript** project structure
- **Tailwind CSS** for styling with custom dark theme
- **React Router** for client-side navigation
- **Authentication Context** with JWT token management
- **Axios** service with request/response interceptors
- **Login & Registration** pages with validation
- **Protected Routes** for authenticated content

### Phase 2: Multi-Group Layout & Navigation ✅
- **3-Column Layout**: Groups | Channels | Main Content
- **GroupList** with Discord-style server icons
- **ChannelColumn** with channel/DM list
- **Custom Hooks** for data fetching (`useGroups`, `useChannels`, `useDirectMessages`)
- **State Management** for navigation and selection
- **Loading & Error States** with proper UX

### Phase 3: Real-Time Chat ✅
- **Context-Aware WebSocket Hook** for channels and DMs
- **ChatView** component with message list and input
- **Message Components** with sender avatars and timestamps
- **Auto-scrolling** message list
- **Send on Enter** with Shift+Enter for new lines
- **Connection Status** indicator
- **Automatic Reconnection** on connection loss

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── AppLayout.tsx            # 3-column layout
│   │   ├── GroupList.tsx            # Server/group icons
│   │   ├── ChannelColumn.tsx        # Channel list container
│   │   ├── GroupHeader.tsx          # Column header
│   │   ├── ChannelList.tsx          # Channel/DM list
│   │   ├── MainContentView.tsx      # Main content area
│   │   ├── ChatView.tsx             # Chat interface
│   │   ├── MessageList.tsx          # Message display
│   │   ├── ChatMessage.tsx          # Individual message
│   │   ├── MessageInput.tsx         # Message composer
│   │   └── ProtectedRoute.tsx       # Auth guard
│   │
│   ├── contexts/             # React contexts
│   │   └── AuthContext.tsx          # Authentication state
│   │
│   ├── hooks/                # Custom React hooks
│   │   ├── useWebSocket.ts          # WebSocket connection
│   │   ├── useGroups.ts             # Fetch groups
│   │   ├── useChannels.ts           # Fetch channels
│   │   └── useDirectMessages.ts     # Fetch DMs
│   │
│   ├── pages/                # Page components
│   │   ├── LoginPage.tsx            # Login form
│   │   ├── RegistrationPage.tsx     # Registration form
│   │   └── ChatPage.tsx             # Main app page
│   │
│   ├── services/             # External services
│   │   └── api.ts                   # Axios instance & interceptors
│   │
│   ├── types/                # TypeScript definitions
│   │   └── index.ts                 # All type definitions
│   │
│   ├── App.tsx               # Main app with routing
│   ├── main.tsx              # Entry point
│   └── index.css             # Global styles + Tailwind
│
├── public/                   # Static assets
├── .env                      # Environment variables
├── .env.example              # Environment template
├── index.html                # HTML template
├── package.json              # Dependencies
├── tsconfig.json             # TypeScript config
├── tailwind.config.js        # Tailwind config
├── postcss.config.js         # PostCSS config
└── vite.config.ts            # Vite config

```

## 🛠️ Setup Instructions

### Prerequisites
- Node.js (v18 or higher)
- npm or yarn

### Installation

1. **Navigate to frontend directory:**
```powershell
cd frontend
```

2. **Install dependencies:**
```powershell
npm install
```

3. **Configure environment variables:**
Create a `.env` file (or use the provided `.env.example`):
```env
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000
```

4. **Start development server:**
```powershell
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

```powershell
npm run build
```

This creates an optimized production build in the `dist` directory.

## 🎨 Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool & dev server
- **React Router v6** - Client-side routing
- **Axios** - HTTP client
- **Tailwind CSS** - Utility-first styling
- **Zustand** - Lightweight state management
- **WebSocket API** - Real-time communication

## 🔑 Key Design Decisions

### Why Vite?
- ⚡ Lightning-fast HMR during development
- 🎯 Optimized production builds
- 🔧 Zero-config TypeScript support
- 📦 Much faster than Create React App

### Why Tailwind CSS?
- 🎨 Rapid UI development with utility classes
- 📱 Built-in responsive design
- 🌙 Easy dark mode implementation
- 📦 Purges unused CSS for minimal bundle size

### Why React Context for Auth?
- Global state accessible throughout the app
- Avoids prop drilling
- Centralized authentication logic
- Efficient re-rendering

### Security Considerations

**JWT Storage in localStorage:**
- ⚠️ Vulnerable to XSS attacks
- ✅ Mitigations implemented:
  - Input sanitization
  - Content Security Policy headers
  - Short-lived tokens
- 🔒 Production recommendation: Use httpOnly cookies

**API Interceptors:**
- Automatically add auth tokens to requests
- Global error handling for 401 responses
- Ready for token refresh implementation

## 📡 API Integration

### Expected Backend Endpoints

```
Authentication:
POST /api/token          - Login (username, password)
POST /api/register       - Register new user
GET  /api/users/me       - Get current user

Groups & Channels:
GET  /api/groups         - List user's groups
GET  /api/groups/{id}/channels - List group channels

Direct Messages:
GET  /api/dms            - List DM conversations

WebSocket:
WS   /ws/channel/{id}    - Connect to channel chat
WS   /ws/dm/{id}         - Connect to DM chat
```

### WebSocket Message Format

**Sending:**
```json
{
  "type": "message",
  "content": "Hello, world!"
}
```

**Receiving:**
```json
{
  "type": "message",
  "id": "msg123",
  "content": "Hello, world!",
  "sender_name": "John Doe",
  "sender_id": "user123",
  "timestamp": "2025-10-27T12:34:56Z",
  "is_own_message": false,
  "avatar_url": "https://..."
}
```

**History:**
```json
{
  "type": "history",
  "messages": [...]
}
```

## 🎯 Component Flow

### User Journey: Selecting a Channel

1. User clicks group icon in `GroupList`
2. `ChatPage.handleSelectGroup(groupId)` is called
3. State updates: `selectedGroupId`, `isDmView=false`
4. `useChannels(groupId)` hook fetches channels
5. `ChannelColumn` receives new channels and re-renders
6. User clicks channel name in `ChannelList`
7. `ChatPage.handleSelectChannel(channelId)` is called
8. State updates: `selectedChannelId`
9. `MainContentView` renders `ChatView`
10. `ChatView` creates WebSocket context
11. `useWebSocket` hook connects and fetches messages
12. `MessageList` displays messages
13. User types and sends via `MessageInput`
14. WebSocket sends message to server
15. Server broadcasts to all connected clients
16. Hook receives message and updates state
17. New message appears in `MessageList`

## 🚧 Future Enhancements

- [ ] PWA configuration for offline support
- [ ] Voice/Video channel support with WebRTC
- [ ] Todo list and Kanban board views
- [ ] File upload and image preview
- [ ] User presence indicators
- [ ] Typing indicators
- [ ] Message reactions and threads
- [ ] Search functionality
- [ ] Notification system
- [ ] Mobile responsive improvements
- [ ] Accessibility (ARIA labels, keyboard navigation)

## 🐛 Troubleshooting

**Build errors about missing modules:**
- Run `npm install` to ensure all dependencies are installed

**Connection errors:**
- Verify backend is running on port 8000
- Check `.env` file has correct API and WebSocket URLs
- Ensure CORS is configured on backend

**TypeScript errors:**
- These are expected before `npm install` is run
- All type definitions are provided in the codebase

**WebSocket not connecting:**
- Check browser console for connection errors
- Verify WebSocket URL in `.env`
- Ensure backend WebSocket endpoint is accessible

## 📝 License

This project is part of a larger workspace collaboration platform.

## 🤝 Contributing

This is the frontend implementation based on the detailed specification. For backend integration, ensure your API matches the expected endpoints and message formats documented above.
