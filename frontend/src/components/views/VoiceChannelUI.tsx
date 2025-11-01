import React, { useState, useEffect } from 'react';
import { useWebRTC } from '../../hooks/useWebRTC';
import { useWebRTCContext } from '../../contexts/WebRTCContext';

interface VoiceChannelUIProps {
  channelId: string;
}

interface VoiceParticipant {
  id: string;
  username: string;
  avatarUrl?: string;
  isMuted: boolean;
  isSpeaking: boolean;
}

/**
 * VoiceChannelUI Component
 * 
 * Audio-focused persistent voice channel interface
 * 
 * Key differences from VideoCallView:
 * 1. Audio-only (no video streams)
 * 2. Persistent - stays visible while user browses other channels
 * 3. Shows participant list with speaking indicators
 * 4. Lightweight UI that doesn't block the main content area
 * 5. Can be minimized to a floating widget
 * 
 * Flow:
 * 1. User clicks "Join Voice" button
 * 2. joinVoiceChannel() gets audio stream
 * 3. User can browse text channels while in voice
 * 4. Voice connection persists until "Leave Voice" is clicked
 */
const VoiceChannelUI: React.FC<VoiceChannelUIProps> = ({ channelId }) => {
  const webrtcContext = useWebRTCContext();
  const [participants, setParticipants] = useState<VoiceParticipant[]>([]);
  const [channelName, setChannelName] = useState('Voice Channel');

  // Initialize WebRTC with signaling callbacks
  const webrtc = useWebRTC({
    onSignal: {
      sendOffer: (userId, offer) => {
        webrtcContext.sendSignal({
          type: 'webrtc_offer',
          senderId: 'current_user',
          targetId: userId,
          data: offer,
        });
      },
      sendAnswer: (userId, answer) => {
        webrtcContext.sendSignal({
          type: 'webrtc_answer',
          senderId: 'current_user',
          targetId: userId,
          data: answer,
        });
      },
      sendIceCandidate: (userId, candidate) => {
        webrtcContext.sendSignal({
          type: 'webrtc_ice_candidate',
          senderId: 'current_user',
          targetId: userId,
          data: candidate,
        });
      },
    },
  });

  // Register WebRTC handlers with context
  useEffect(() => {
    webrtcContext.registerOfferHandler(webrtc.acceptCall);
    webrtcContext.registerAnswerHandler(webrtc.handleAnswer);
    webrtcContext.registerIceCandidateHandler(webrtc.handleIceCandidate);
  }, [webrtcContext, webrtc]);

  // Fetch channel info and participants
  useEffect(() => {
    // TODO: Fetch from API
    setChannelName('🎧 General Voice');
    setParticipants([
      { id: '1', username: 'Alice', isMuted: false, isSpeaking: false },
      { id: '2', username: 'Bob', isMuted: true, isSpeaking: false },
    ]);
  }, [channelId]);

  // Update participants when remote streams change
  useEffect(() => {
    // Update participants list based on remote streams
    // TODO: Fetch user info for each remote user and update participants state
    console.log('Remote streams updated:', Object.keys(webrtc.remoteStreams));
  }, [webrtc.remoteStreams]);

  // Handle join voice channel
  const handleJoinVoice = async () => {
    try {
      await webrtc.joinVoiceChannel(channelId);
    } catch (error) {
      console.error('Failed to join voice channel:', error);
      alert('Failed to join voice channel. Please check your microphone permissions.');
    }
  };

  // Handle leave voice channel
  const handleLeaveVoice = () => {
    webrtc.endCall();
  };

  return (
    <div className="flex flex-col h-full bg-dark-bg">
      {/* Header */}
      <div className="px-6 py-4 bg-dark-surface border-b border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-semibold text-white">{channelName}</h2>
              <p className="text-sm text-gray-400">
                {webrtc.isInCall ? `${participants.length + 1} in voice` : 'Voice channel'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col items-center justify-center p-8">
        {!webrtc.isInCall ? (
          /* Not Connected State */
          <div className="text-center space-y-6 max-w-md">
            <div className="w-24 h-24 mx-auto bg-gray-700 rounded-full flex items-center justify-center">
              <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
              </svg>
            </div>
            <div>
              <h3 className="text-2xl font-semibold text-white mb-2">Voice Channel</h3>
              <p className="text-gray-400">
                Join this voice channel to talk with others. Your camera will stay off.
              </p>
            </div>
            <button
              onClick={handleJoinVoice}
              className="px-8 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-semibold text-lg"
            >
              Join Voice Channel
            </button>
            {participants.length > 0 && (
              <div className="mt-6">
                <p className="text-sm text-gray-400 mb-2">{participants.length} member{participants.length > 1 ? 's' : ''} in voice:</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {participants.map(p => (
                    <span key={p.id} className="text-sm text-gray-300">{p.username}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          /* Connected State */
          <div className="w-full max-w-2xl space-y-6">
            {/* Participants List */}
            <div className="bg-dark-surface rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">
                In Voice — {participants.length + 1}
              </h3>
              <div className="space-y-3">
                {/* Current User */}
                <div className="flex items-center gap-3 p-3 rounded-lg bg-gray-700">
                  <div className="w-10 h-10 bg-accent-primary rounded-full flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <p className="text-white font-medium">You</p>
                  </div>
                  <div className="flex items-center gap-2">
                    {webrtc.isMuted ? (
                      <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                      </svg>
                    ) : (
                      <div className="flex items-center gap-1">
                        <div className="w-1 h-3 bg-green-500 rounded-full animate-pulse"></div>
                        <div className="w-1 h-4 bg-green-500 rounded-full animate-pulse delay-75"></div>
                        <div className="w-1 h-2 bg-green-500 rounded-full animate-pulse delay-150"></div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Other Participants */}
                {participants.map(participant => (
                  <div key={participant.id} className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-700 transition-colors">
                    <div className="w-10 h-10 bg-gray-600 rounded-full flex items-center justify-center">
                      {participant.avatarUrl ? (
                        <img src={participant.avatarUrl} alt={participant.username} className="w-full h-full rounded-full object-cover" />
                      ) : (
                        <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                        </svg>
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="text-white">{participant.username}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      {participant.isMuted ? (
                        <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                        </svg>
                      ) : participant.isSpeaking ? (
                        <div className="flex items-center gap-1">
                          <div className="w-1 h-3 bg-green-500 rounded-full animate-pulse"></div>
                          <div className="w-1 h-4 bg-green-500 rounded-full animate-pulse delay-75"></div>
                          <div className="w-1 h-2 bg-green-500 rounded-full animate-pulse delay-150"></div>
                        </div>
                      ) : (
                        <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                        </svg>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Voice Controls */}
            <div className="bg-dark-surface rounded-lg p-6">
              <div className="flex items-center justify-center gap-4">
                <button
                  onClick={webrtc.toggleMute}
                  className={`p-4 rounded-full transition-colors ${
                    webrtc.isMuted
                      ? 'bg-red-600 hover:bg-red-700'
                      : 'bg-gray-700 hover:bg-gray-600'
                  }`}
                  title={webrtc.isMuted ? 'Unmute' : 'Mute'}
                >
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    {webrtc.isMuted ? (
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                    ) : (
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    )}
                  </svg>
                </button>

                <button
                  onClick={handleLeaveVoice}
                  className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors font-semibold"
                >
                  Leave Voice Channel
                </button>
              </div>
            </div>

            {/* Info */}
            <div className="text-center">
              <p className="text-sm text-gray-400">
                You can browse other channels while staying connected to voice
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VoiceChannelUI;
