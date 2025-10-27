# Project Chat - Real-Time Collaboration Workspace

A modern, real-time collaboration platform built with React, TypeScript, Vite, and WebSockets. Features a Discord-style interface with groups, channels, direct messaging, and real-time chat capabilities.

## 🚀 Features

- **Authentication System** with JWT tokens
- **3-Column Discord-Style Layout** (Groups | Channels | Main Content)
- **Real-Time Messaging** via WebSockets
- **Group & Channel Management**
- **Direct Messages**
- **Dark Theme UI** with Tailwind CSS
- **TypeScript** for type safety
- **Responsive Design**

## 📁 Project Structure

```
project-chat/
├── frontend/              # React + TypeScript frontend
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── contexts/     # React contexts (Auth)
│   │   ├── hooks/        # Custom hooks (WebSocket, data fetching)
│   │   ├── pages/        # Page components
│   │   ├── services/     # API services
│   │   └── types/        # TypeScript definitions
│   ├── public/           # Static assets
│   └── package.json      # Dependencies
├── SETUP_INSTRUCTIONS.md # Detailed setup guide
└── README.md             # This file
```

## 🛠️ Tech Stack

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool & dev server
- **React Router v6** - Client-side routing
- **Axios** - HTTP client
- **Tailwind CSS** - Utility-first styling
- **WebSocket API** - Real-time communication
- **Zustand** - State management

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Backend API server (running on port 8000)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Hemant-builder-2006/project-chat.git
cd project-chat
```

2. **Install frontend dependencies:**
```bash
cd frontend
npm install
```

3. **Configure environment variables:**
Create a `.env` file in the `frontend` directory:
```env
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000
```

4. **Start the development server:**
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
cd frontend
npm run build
```

## 📖 Documentation

- See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for detailed setup instructions
- See [frontend/README.md](frontend/README.md) for frontend-specific documentation

## 🎯 Implemented Features

### Phase 1: Authentication ✅
- JWT-based authentication
- Login & Registration pages
- Protected routes
- Token management with interceptors

### Phase 2: Multi-Group Layout ✅
- 3-column responsive layout
- Group/Server navigation
- Channel lists by type
- Direct message interface
- Custom data fetching hooks

### Phase 3: Real-Time Chat ✅
- WebSocket connection management
- Real-time message delivery
- Message history
- Auto-scrolling chat
- Connection status indicators
- Automatic reconnection

## 🔑 Key Components

- **AppLayout** - 3-column layout structure
- **GroupList** - Server/group icons with tooltips
- **ChannelColumn** - Channel and DM navigation
- **ChatView** - Real-time chat interface
- **MessageList** - Scrollable message display
- **MessageInput** - Message composer with Enter-to-send

## 🌐 API Integration

### Expected Backend Endpoints

```
Authentication:
POST /api/token          - Login
POST /api/register       - Register
GET  /api/users/me       - Get current user

Groups & Channels:
GET  /api/groups         - List user's groups
GET  /api/groups/{id}/channels - List channels

Direct Messages:
GET  /api/dms            - List DM conversations

WebSocket:
WS   /ws/channel/{id}    - Connect to channel
WS   /ws/dm/{id}         - Connect to DM
```

## 🚧 Future Enhancements

- [ ] PWA support for offline mode
- [ ] Voice/Video channels with WebRTC
- [ ] Todo list and Kanban board views
- [ ] File upload and sharing
- [ ] User presence indicators
- [ ] Typing indicators
- [ ] Message reactions
- [ ] Thread support
- [ ] Search functionality
- [ ] Push notifications

## 🐛 Troubleshooting

**Port already in use:**
```bash
# Change port in vite.config.ts or kill the process
npx kill-port 3000
```

**Module not found errors:**
```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**WebSocket connection issues:**
- Verify backend is running on port 8000
- Check CORS configuration on backend
- Ensure `.env` file has correct URLs

## 📝 License

This project is created for educational and demonstration purposes.

## 👤 Author

**Hemant**
- GitHub: [@Hemant-builder-2006](https://github.com/Hemant-builder-2006)

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

---

Built with ❤️ using React, TypeScript, and Vite
