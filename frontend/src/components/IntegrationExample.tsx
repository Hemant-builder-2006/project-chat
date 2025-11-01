/**
 * Example Component showing how to use the integrated API service
 * 
 * This demonstrates:
 * - Loading groups on component mount
 * - Loading channels when group is selected
 * - Connecting to WebSocket for real-time chat
 * - Sending messages
 * - Using AI features
 */

import React, { useState, useEffect } from 'react';
import { groupsAPI, channelsAPI, aiAPI } from '../services/apiService';
import { useWebSocket } from '../hooks/useWebSocket';
import { Group, Channel } from '../types';

export const IntegrationExample: React.FC = () => {
  // State
  const [groups, setGroups] = useState<Group[]>([]);
  const [selectedGroup, setSelectedGroup] = useState<string | null>(null);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [selectedChannel, setSelectedChannel] = useState<string | null>(null);
  const [messageInput, setMessageInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // WebSocket connection (only when channel is selected)
  const { messages, sendMessage, isConnected } = useWebSocket(
    selectedChannel ? { type: 'channel', id: selectedChannel } : null
  );

  // Load groups on mount
  useEffect(() => {
    loadGroups();
  }, []);

  // Load channels when group is selected
  useEffect(() => {
    if (selectedGroup) {
      loadChannels(selectedGroup);
    }
  }, [selectedGroup]);

  /**
   * Load all groups user is member of
   */
  const loadGroups = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await groupsAPI.getAll();
      setGroups(data);
      
      // Auto-select first group if available
      if (data.length > 0) {
        setSelectedGroup(data[0].id);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load groups');
      console.error('Error loading groups:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Load channels for selected group
   */
  const loadChannels = async (groupId: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await channelsAPI.getByGroup(groupId);
      setChannels(data);
      
      // Auto-select first text channel if available
      const textChannel = data.find(ch => ch.type === 'TEXT');
      if (textChannel) {
        setSelectedChannel(textChannel.id);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load channels');
      console.error('Error loading channels:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Send message via WebSocket
   */
  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!messageInput.trim() || !isConnected) {
      return;
    }

    sendMessage(messageInput);
    setMessageInput('');
  };

  /**
   * Example: Use AI to search documents
   */
  const handleAISearch = async () => {
    if (!selectedChannel) return;
    
    try {
      const results = await aiAPI.search('What was discussed?', [selectedChannel]);
      console.log('AI Search results:', results);
      alert(`AI Search found: ${results.documents?.length || 0} results`);
    } catch (err: any) {
      console.error('AI search failed:', err);
      alert('AI search failed: ' + err.message);
    }
  };

  /**
   * Example: Summarize channel messages
   */
  const handleSummarize = async () => {
    if (!selectedChannel) return;
    
    try {
      const summary = await aiAPI.summarize(selectedChannel, 'concise');
      console.log('Summary:', summary);
      alert('Channel Summary:\n\n' + summary.summary);
    } catch (err: any) {
      console.error('Summarize failed:', err);
      alert('Summarize failed: ' + err.message);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>Frontend-Backend Integration Example</h1>
      
      {/* Error Display */}
      {error && (
        <div style={{ padding: '10px', background: '#fee', color: '#c00', borderRadius: '5px', marginBottom: '10px' }}>
          Error: {error}
        </div>
      )}

      {/* Loading Indicator */}
      {loading && <div>Loading...</div>}

      {/* Groups List */}
      <div style={{ marginBottom: '20px' }}>
        <h2>Groups</h2>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          {groups.map(group => (
            <button
              key={group.id}
              onClick={() => setSelectedGroup(group.id)}
              style={{
                padding: '10px 20px',
                background: selectedGroup === group.id ? '#007bff' : '#f0f0f0',
                color: selectedGroup === group.id ? 'white' : 'black',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer',
              }}
            >
              {group.name}
            </button>
          ))}
        </div>
      </div>

      {/* Channels List */}
      {selectedGroup && (
        <div style={{ marginBottom: '20px' }}>
          <h2>Channels</h2>
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            {channels.map(channel => (
              <button
                key={channel.id}
                onClick={() => setSelectedChannel(channel.id)}
                style={{
                  padding: '10px 20px',
                  background: selectedChannel === channel.id ? '#28a745' : '#f0f0f0',
                  color: selectedChannel === channel.id ? 'white' : 'black',
                  border: 'none',
                  borderRadius: '5px',
                  cursor: 'pointer',
                }}
              >
                # {channel.name} ({channel.type})
              </button>
            ))}
          </div>
        </div>
      )}

      {/* WebSocket Status */}
      {selectedChannel && (
        <div style={{ marginBottom: '20px' }}>
          <h2>Chat</h2>
          <div style={{ marginBottom: '10px' }}>
            WebSocket Status:{' '}
            <span style={{ 
              color: isConnected ? 'green' : 'red',
              fontWeight: 'bold'
            }}>
              {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
            </span>
          </div>

          {/* Messages */}
          <div style={{
            height: '300px',
            overflowY: 'auto',
            border: '1px solid #ccc',
            borderRadius: '5px',
            padding: '10px',
            marginBottom: '10px',
            background: '#fafafa',
          }}>
            {messages.length === 0 && (
              <div style={{ color: '#999', textAlign: 'center', marginTop: '50px' }}>
                No messages yet. Send one!
              </div>
            )}
            {messages.map((msg, idx) => (
              <div
                key={msg.id || idx}
                style={{
                  marginBottom: '10px',
                  padding: '8px',
                  background: msg.isOwnMessage ? '#e3f2fd' : 'white',
                  borderRadius: '5px',
                  borderLeft: msg.isOwnMessage ? '3px solid #2196f3' : '3px solid #ccc',
                }}
              >
                <div style={{ fontWeight: 'bold', fontSize: '12px', color: '#666' }}>
                  {msg.senderName}
                </div>
                <div>{msg.content}</div>
                <div style={{ fontSize: '10px', color: '#999', marginTop: '4px' }}>
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ))}
          </div>

          {/* Message Input */}
          <form onSubmit={handleSendMessage} style={{ display: 'flex', gap: '10px' }}>
            <input
              type="text"
              value={messageInput}
              onChange={(e) => setMessageInput(e.target.value)}
              placeholder="Type a message... (try @AI hello)"
              disabled={!isConnected}
              style={{
                flex: 1,
                padding: '10px',
                border: '1px solid #ccc',
                borderRadius: '5px',
                fontSize: '14px',
              }}
            />
            <button
              type="submit"
              disabled={!isConnected || !messageInput.trim()}
              style={{
                padding: '10px 20px',
                background: isConnected ? '#007bff' : '#ccc',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: isConnected ? 'pointer' : 'not-allowed',
              }}
            >
              Send
            </button>
          </form>
        </div>
      )}

      {/* AI Features */}
      {selectedChannel && (
        <div style={{ marginTop: '20px' }}>
          <h2>AI Features</h2>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={handleAISearch}
              style={{
                padding: '10px 20px',
                background: '#6f42c1',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer',
              }}
            >
              🔍 AI Search
            </button>
            <button
              onClick={handleSummarize}
              style={{
                padding: '10px 20px',
                background: '#fd7e14',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer',
              }}
            >
              📝 Summarize Channel
            </button>
          </div>
          <p style={{ fontSize: '12px', color: '#666', marginTop: '10px' }}>
            💡 Tip: You can also use @AI commands in chat (e.g., "@AI summarize this")
          </p>
        </div>
      )}

      {/* Instructions */}
      <div style={{
        marginTop: '30px',
        padding: '15px',
        background: '#e7f3ff',
        borderRadius: '5px',
        fontSize: '14px',
      }}>
        <h3 style={{ marginTop: 0 }}>✅ Integration Working!</h3>
        <ul style={{ marginBottom: 0 }}>
          <li>✅ Authentication via AuthContext</li>
          <li>✅ REST API calls via apiService</li>
          <li>✅ WebSocket real-time messaging</li>
          <li>✅ AI features (search & summarize)</li>
        </ul>
      </div>
    </div>
  );
};

export default IntegrationExample;
