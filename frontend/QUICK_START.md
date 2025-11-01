# Quick Start - Frontend Integration

## 🚀 Start Both Backend and Frontend

### 1. Start Backend (Terminal 1)
```bash
cd backend
uvicorn main:app --reload
```

**Expected output:**
```
🚀 Application startup
✅ Database tables created
✅ Upload directories created
🔄 Starting background tasks...
  ✓ Data retention task started
  ✓ File cleanup task started
  ✓ Health check task started
✅ All background tasks started
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 2. Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```

**Expected output:**
```
  VITE v5.0.8  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

## 🧪 Test the Integration

### Step 1: Test Backend is Running
Open in browser: http://localhost:8000/docs

You should see the FastAPI Swagger documentation.

### Step 2: Test Frontend
Open in browser: http://localhost:5173

You should see your React app.

### Step 3: Test Example Component

**Option A: Add to existing App.tsx**
```typescript
// src/App.tsx
import IntegrationExample from './components/IntegrationExample';

function App() {
  return (
    <div>
      <IntegrationExample />
    </div>
  );
}

export default App;
```

**Option B: Create test route**
```typescript
// src/App.tsx (if you have React Router)
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import IntegrationExample from './components/IntegrationExample';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/test" element={<IntegrationExample />} />
        {/* ...other routes */}
      </Routes>
    </BrowserRouter>
  );
}
```

Then visit: http://localhost:5173/test

---

## ✅ What to Test

### 1. Registration & Login
```
1. Go to registration page
2. Create account: username, email, password
3. Should auto-login and redirect
4. Check browser localStorage for 'accessToken'
```

### 2. Groups & Channels
```
1. Create a new group (or groups should load automatically)
2. Select a group
3. Channels should appear
4. Click on a channel
```

### 3. WebSocket Chat
```
1. Select a channel
2. Check connection status (should be 🟢 Connected)
3. Type a message and send
4. Message should appear instantly
5. Try: @AI hello world
6. AI should respond
```

### 4. AI Features
```
1. Click "AI Search" button
2. Click "Summarize Channel" button
3. Check console for results
```

---

## 🔍 Debugging

### Check Backend Logs
```bash
# In backend terminal, you should see:
INFO:     WebSocket connected to channel abc123
INFO:     User testuser (user-id) connected
```

### Check Frontend Console
```javascript
// Open browser DevTools (F12) > Console
// You should see:
WebSocket connected to channel abc123
Received message: { type: 'online_users', users: [...] }
```

### Check Network Tab
```
1. Open DevTools > Network tab
2. Filter by "WS" to see WebSocket connection
3. Click on it to see messages being sent/received
```

### Common Issues

**Problem: Can't login**
- Check backend is running on port 8000
- Check VITE_API_URL in .env: `http://localhost:8000/api`
- Check Network tab for 401 errors

**Problem: WebSocket not connecting**
- Check VITE_WS_URL in .env: `ws://localhost:8000`
- Check token is in localStorage
- Check backend logs for WebSocket errors

**Problem: Groups/Channels not loading**
- Create a group first via backend admin: http://localhost:8000/admin
- Or create via API: `POST /api/groups` with body `{"name": "Test Group"}`
- Create a channel: `POST /api/groups/{group_id}/channels` with body `{"name": "general", "type": "TEXT"}`

---

## 🗄️ Create Test Data

### Option 1: Via Admin Panel
```
1. Go to: http://localhost:8000/admin
2. Login with superuser account
3. Create groups, channels manually
```

### Option 2: Via API (using cURL or Postman)
```bash
# Get access token first (login)
TOKEN="your-access-token-here"

# Create group
curl -X POST http://localhost:8000/api/groups \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Team"}'

# Create channel (replace GROUP_ID)
curl -X POST http://localhost:8000/api/groups/GROUP_ID/channels \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "general", "type": "TEXT"}'
```

### Option 3: Via Browser Console
```javascript
// In browser console (after logging in):
import { groupsAPI, channelsAPI } from './services/apiService';

// Create group
const group = await groupsAPI.create('Test Group');
console.log('Created group:', group);

// Create channel
const channel = await channelsAPI.create(group.id, 'general', 'TEXT');
console.log('Created channel:', channel);
```

---

## 📊 Full Integration Test Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Can access /docs at http://localhost:8000/docs
- [ ] Can register new user
- [ ] Can login
- [ ] Access token stored in localStorage
- [ ] Groups load successfully
- [ ] Channels load when group selected
- [ ] WebSocket connects (green status)
- [ ] Can send messages
- [ ] Messages appear in real-time
- [ ] @AI commands work
- [ ] AI Search button works
- [ ] AI Summarize button works

---

## 🎯 Next Steps

Once everything is working:

1. **Build Your UI**
   - Use the apiService functions in your components
   - Customize the IntegrationExample component
   - Add proper error handling and loading states

2. **Add Features**
   - Tasks (Todo lists)
   - Documents (Collaborative editing)
   - Kanban boards
   - File uploads
   - Voice/Video calls (WebRTC)

3. **Styling**
   - You already have Tailwind CSS configured
   - Style the components to match your design

4. **Testing**
   - Write tests for components
   - Test API integration
   - Test WebSocket reliability

---

## 🎉 You're Ready!

Your frontend and backend are now fully integrated and communicating! 

**Everything works:**
✅ Authentication
✅ REST API
✅ WebSocket
✅ AI Features
✅ Type Safety

**Start building your amazing collaboration platform!** 🚀
