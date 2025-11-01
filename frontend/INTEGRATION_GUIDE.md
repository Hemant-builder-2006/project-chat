# Frontend-Backend Integration Guide

## 🔗 Integration Complete!

Your React frontend is now properly configured to communicate with the FastAPI backend.

---

## ✅ What Was Updated

### 1. **Authentication Context** (`src/contexts/AuthContext.tsx`)
- ✅ Updated login endpoint to `/api/auth/login`
- ✅ Changed to FormData format (OAuth2PasswordRequestForm)
- ✅ Updated register endpoint to `/api/auth/register`
- ✅ Updated user endpoint to `/api/auth/me`
- ✅ Fetches user data after login

### 2. **API Service** (`src/services/apiService.ts`) - NEW
- ✅ Complete API wrapper for all backend endpoints
- ✅ Organized by feature: Auth, Groups, Channels, Messages, Tasks, Documents, Kanban, AI, WebRTC
- ✅ Type-safe with TypeScript interfaces
- ✅ Ready to use in components

### 3. **WebSocket Hook** (`src/hooks/useWebSocket.ts`)
- ✅ Updated message handling for backend message format
- ✅ Added support for all backend WebSocket message types:
  - `message` - Chat messages
  - `dm_message` - Direct messages
  - `user_joined` / `user_left` - Presence events
  - `online_users` - Online user list
  - `typing` / `dm_typing` - Typing indicators
  - `webrtc_offer` / `webrtc_answer` / `webrtc_ice_candidate` - WebRTC signaling
  - `error` - Error messages
- ✅ Proper message/DM type selection based on context

---

## 📁 File Structure

```
frontend/src/
├── contexts/
│   ├── AuthContext.tsx          ✅ Updated
│   └── WebRTCContext.tsx         (existing)
├── services/
│   ├── api.ts                    (existing - axios instance)
│   └── apiService.ts             ✅ NEW - All API functions
├── hooks/
│   └── useWebSocket.ts           ✅ Updated
├── types/
│   └── index.ts                  (existing - type definitions)
└── ...
```

---

## 🚀 How to Use the API Service

### Example 1: Login
```typescript
import { authAPI } from '../services/apiService';

const handleLogin = async () => {
  try {
    const response = await authAPI.login({
      username: 'testuser',
      password: 'password123'
    });
    console.log('Logged in:', response);
  } catch (error) {
    console.error('Login failed:', error);
  }
};
```

### Example 2: Get Groups
```typescript
import { groupsAPI } from '../services/apiService';

const loadGroups = async () => {
  try {
    const groups = await groupsAPI.getAll();
    console.log('Groups:', groups);
  } catch (error) {
    console.error('Failed to load groups:', error);
  }
};
```

### Example 3: Send Message via WebSocket
```typescript
// Already works with useWebSocket hook!
const { sendMessage, messages, isConnected } = useWebSocket({
  type: 'channel',
  id: 'channel-id-here'
});

// Send message
sendMessage('Hello, world!');

// Messages automatically appear in the messages array
console.log('Messages:', messages);
```

### Example 4: AI Search
```typescript
import { aiAPI } from '../services/apiService';

const searchDocuments = async () => {
  try {
    const results = await aiAPI.search('What is our project roadmap?', [channelId]);
    console.log('Search results:', results);
  } catch (error) {
    console.error('Search failed:', error);
  }
};
```

### Example 5: WebRTC
```typescript
import { webrtcAPI } from '../services/apiService';

const setupCall = async () => {
  try {
    // Get ICE servers configuration
    const iceConfig = await webrtcAPI.getIceServers();
    
    // Create peer connection
    const peerConnection = new RTCPeerConnection(iceConfig);
    
    // ... rest of WebRTC setup
  } catch (error) {
    console.error('WebRTC setup failed:', error);
  }
};
```

---

## 🔌 WebSocket Integration

### Channel Messages
```typescript
const { messages, sendMessage, isConnected } = useWebSocket({
  type: 'channel',
  id: channelId
});

// Messages are automatically synced
// Send with: sendMessage('Hello!')
```

### Direct Messages
```typescript
const { messages, sendMessage, isConnected } = useWebSocket({
  type: 'dm',
  id: otherUserId
});

// DM messages work the same way
```

### Message Types Handled
- ✅ Regular chat messages
- ✅ AI responses (with `is_ai: true`)
- ✅ User presence (joined/left)
- ✅ Typing indicators
- ✅ WebRTC signaling
- ✅ Error messages

---

## 🌐 Environment Configuration

Make sure your `.env` file is set up correctly:

```env
# Frontend .env
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000
```

**For production:**
```env
VITE_API_URL=https://yourdomain.com/api
VITE_WS_URL=wss://yourdomain.com
```

---

## 📝 Complete API Reference

### Authentication
```typescript
authAPI.login(credentials)           // POST /api/auth/login
authAPI.register(credentials)        // POST /api/auth/register
authAPI.getCurrentUser()             // GET /api/auth/me
authAPI.refreshToken(refreshToken)   // POST /api/auth/refresh
```

### Groups
```typescript
groupsAPI.getAll()                   // GET /api/groups
groupsAPI.getById(groupId)           // GET /api/groups/{id}
groupsAPI.create(name)               // POST /api/groups
groupsAPI.getMembers(groupId)        // GET /api/groups/{id}/members
groupsAPI.addMember(groupId, userId) // POST /api/groups/{id}/members
```

### Channels
```typescript
channelsAPI.getByGroup(groupId)      // GET /api/groups/{id}/channels
channelsAPI.create(groupId, name, type) // POST /api/groups/{id}/channels
```

### Messages
```typescript
messagesAPI.getByChannel(channelId)  // GET /api/channels/{id}/messages
messagesAPI.send(channelId, content) // POST /api/channels/{id}/messages
messagesAPI.delete(messageId)        // DELETE /api/messages/{id}
```

### Tasks (Todo Lists)
```typescript
tasksAPI.getByChannel(channelId)     // GET /api/channels/{id}/tasks
tasksAPI.create(channelId, content)  // POST /api/channels/{id}/tasks
tasksAPI.update(taskId, updates)     // PUT /api/tasks/{id}
tasksAPI.delete(taskId)              // DELETE /api/tasks/{id}
```

### Documents
```typescript
documentsAPI.get(channelId)          // GET /api/channels/{id}/document
documentsAPI.update(channelId, content) // PUT /api/channels/{id}/document
```

### Kanban
```typescript
kanbanAPI.getBoard(channelId)        // GET /api/channels/{id}/kanban
kanbanAPI.createColumn(channelId, title, order) // POST /api/channels/{id}/kanban/columns
kanbanAPI.createCard(columnId, content, order)  // POST /api/kanban/columns/{id}/cards
kanbanAPI.updateCard(cardId, updates)           // PUT /api/kanban/cards/{id}
kanbanAPI.moveCard(cardId, columnId, order)     // PUT /api/kanban/cards/{id}/move
```

### AI Features
```typescript
aiAPI.search(query, channelIds?)     // POST /api/ai/search
aiAPI.summarize(channelId, style)    // POST /api/ai/summarize/{id}
aiAPI.uploadDocument(channelId, file) // POST /api/ai/upload/{id}
aiAPI.chat(message, model?)          // POST /api/ai/chat
aiAPI.checkHealth()                  // GET /api/ai/health
aiAPI.listModels()                   // GET /api/ai/models
```

### WebRTC
```typescript
webrtcAPI.getTurnCredentials()       // GET /api/webrtc/turn-credentials
webrtcAPI.getIceServers()            // GET /api/webrtc/ice-servers
```

### Files
```typescript
filesAPI.upload(file, type)          // POST /api/files/upload
```

### Health
```typescript
healthAPI.check()                    // GET /health
```

---

## 🧪 Testing the Integration

### 1. Start Backend
```bash
cd backend
uvicorn main:app --reload
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

### 3. Test Authentication
1. Open http://localhost:5173
2. Register a new account
3. Login with credentials
4. Check browser console for successful authentication

### 4. Test WebSocket
1. Join a channel
2. Send a message
3. Check browser console for WebSocket events
4. Try @AI commands to test AI integration

### 5. Test AI Features
```typescript
// In browser console:
import { aiAPI } from './services/apiService';

// Check AI health
await aiAPI.checkHealth();

// List models
await aiAPI.listModels();

// Search
await aiAPI.search('test query');
```

---

## 🐛 Common Issues & Solutions

### Issue: CORS Errors
```
Solution: Make sure backend CORS_ORIGINS includes your frontend URL
Backend .env: CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Issue: 401 Unauthorized
```
Solution: Check that access token is being stored and sent
- Check localStorage for 'accessToken'
- Check Network tab > Headers > Authorization: Bearer ...
```

### Issue: WebSocket Connection Failed
```
Solution: 
1. Check WebSocket URL in .env: VITE_WS_URL=ws://localhost:8000
2. Ensure backend is running
3. Check token is valid
4. Look for errors in browser console
```

### Issue: API Calls Return 404
```
Solution: 
1. Check VITE_API_URL includes /api: http://localhost:8000/api
2. Verify backend endpoint exists
3. Check backend logs for routing errors
```

### Issue: TypeScript Errors
```
Solution: 
1. Ensure types are imported correctly
2. Run: npm install (to ensure dependencies are updated)
3. Restart TypeScript server in VS Code
```

---

## 📊 Network Traffic Example

### Successful Login Flow
```
1. POST http://localhost:8000/api/auth/login
   Headers: Content-Type: application/x-www-form-urlencoded
   Body: username=testuser&password=testpass123
   Response: { access_token: "...", refresh_token: "...", token_type: "bearer" }

2. GET http://localhost:8000/api/auth/me
   Headers: Authorization: Bearer <access_token>
   Response: { id: "...", username: "testuser", email: "..." }
```

### WebSocket Connection
```
1. Connect: ws://localhost:8000/ws/channel/abc123?token=<access_token>
2. Server sends: { "type": "online_users", "users": [...] }
3. Client sends: { "type": "message", "content": "Hello!" }
4. Server broadcasts: { "type": "message", "id": "...", "content": "Hello!", ... }
```

---

## 🎯 Next Steps

1. **Update Components** - Use the new apiService in your React components
2. **Add Error Handling** - Wrap API calls in try-catch blocks
3. **Add Loading States** - Show spinners while API calls are in progress
4. **Test All Features** - Try each API endpoint
5. **WebRTC Integration** - Implement voice/video calls using webrtcAPI
6. **AI Features** - Add UI for document search and chat with AI

---

## 📚 Additional Resources

- Backend API Docs: http://localhost:8000/docs
- Backend Admin Panel: http://localhost:8000/admin
- Backend Health: http://localhost:8000/health

---

## 🎉 Summary

Your frontend is now fully integrated with the backend!

✅ Authentication working with JWT tokens  
✅ WebSocket real-time messaging configured  
✅ Complete API service for all backend endpoints  
✅ Type-safe TypeScript interfaces  
✅ Error handling and automatic token refresh  
✅ WebRTC signaling support  
✅ AI features integration  

**Everything is ready to build your UI components!** 🚀
