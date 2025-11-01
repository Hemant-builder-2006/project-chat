import React, { useEffect, useRef } from 'react';
import { useWebRTC } from '../../hooks/useWebRTC';
import { useWebRTCContext } from '../../contexts/WebRTCContext';

interface VideoCallViewProps {
  targetUserId?: string;
  channelId?: string;
  onClose: () => void;
}

/**
 * VideoCallView Component
 * 
 * Displays video feeds for 1:1 or group video calls
 * Features:
 * - Grid layout for multiple participants
 * - Local and remote video streams
 * - Controls for mute, video, screen share, and end call
 * - Responsive grid layout (1-2-3-4 participants)
 * 
 * The component uses the ontrack event from RTCPeerConnection (managed in useWebRTC)
 * to dynamically add new video feeds when participants join.
 * 
 * Flow:
 * 1. useWebRTC creates peer connections for each participant
 * 2. ontrack event fires when remote stream is received
 * 3. remoteStreams state updates with new MediaStream
 * 4. React re-renders and creates new video element
 * 5. useEffect attaches the stream to the video element's srcObject
 */
const VideoCallView: React.FC<VideoCallViewProps> = ({ targetUserId, channelId, onClose }) => {
  const webrtcContext = useWebRTCContext();
  
  // Initialize WebRTC with signaling callbacks
  const webrtc = useWebRTC({
    onSignal: {
      sendOffer: (userId, offer) => {
        webrtcContext.sendSignal({
          type: 'webrtc_offer',
          senderId: 'current_user', // This should come from auth context
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

  // Refs for video elements
  const localVideoRef = useRef<HTMLVideoElement>(null);
  const remoteVideoRefs = useRef<Record<string, HTMLVideoElement | null>>({});

  // Attach local stream to video element
  useEffect(() => {
    if (localVideoRef.current && webrtc.localStream) {
      localVideoRef.current.srcObject = webrtc.localStream;
    }
  }, [webrtc.localStream]);

  // Start call on mount
  useEffect(() => {
    if (targetUserId) {
      // 1:1 video call
      webrtc.startCall(targetUserId);
    } else if (channelId) {
      // Join voice/video channel
      webrtc.joinVoiceChannel(channelId);
    }
  }, [targetUserId, channelId]);

  // Handle close
  const handleEndCall = () => {
    webrtc.endCall();
    onClose();
  };

  // Get array of remote stream entries
  const remoteStreamEntries = Object.entries(webrtc.remoteStreams);
  const participantCount = remoteStreamEntries.length + 1; // +1 for local

  // Determine grid layout
  const getGridClass = () => {
    if (participantCount === 1) return 'grid-cols-1';
    if (participantCount === 2) return 'grid-cols-2';
    if (participantCount === 3) return 'grid-cols-2';
    return 'grid-cols-2 lg:grid-cols-3';
  };

  return (
    <div className="fixed inset-0 bg-black z-50 flex flex-col">
      {/* Header */}
      <div className="bg-gray-900 px-6 py-4 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white">
            {channelId ? 'Group Call' : '1:1 Video Call'}
          </h2>
          <p className="text-sm text-gray-400">
            {participantCount} participant{participantCount > 1 ? 's' : ''}
          </p>
        </div>
      </div>

      {/* Video Grid */}
      <div className="flex-1 p-4 overflow-auto">
        <div className={`grid ${getGridClass()} gap-4 h-full`}>
          {/* Local Video */}
          <div className="relative bg-gray-800 rounded-lg overflow-hidden aspect-video">
            <video
              ref={localVideoRef}
              autoPlay
              muted
              playsInline
              className="w-full h-full object-cover"
            />
            <div className="absolute bottom-4 left-4 bg-black bg-opacity-60 px-3 py-1 rounded-full">
              <span className="text-white text-sm font-medium">You {webrtc.isScreenSharing && '(Screen)'}</span>
            </div>
            {!webrtc.isVideoEnabled && (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-700">
                <div className="w-20 h-20 bg-gray-600 rounded-full flex items-center justify-center">
                  <svg className="w-10 h-10 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
            )}
          </div>

          {/* Remote Videos */}
          {remoteStreamEntries.map(([userId, stream]) => (
            <div key={userId} className="relative bg-gray-800 rounded-lg overflow-hidden aspect-video">
              <video
                ref={(el) => {
                  if (el && stream) {
                    el.srcObject = stream;
                    remoteVideoRefs.current[userId] = el;
                  }
                }}
                autoPlay
                playsInline
                className="w-full h-full object-cover"
              />
              <div className="absolute bottom-4 left-4 bg-black bg-opacity-60 px-3 py-1 rounded-full">
                <span className="text-white text-sm font-medium">User {userId}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Controls */}
      <div className="bg-gray-900 px-6 py-6 flex items-center justify-center gap-4">
        {/* Mute Button */}
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

        {/* Video Button */}
        {webrtc.callType === 'video' && (
          <button
            onClick={webrtc.toggleVideo}
            className={`p-4 rounded-full transition-colors ${
              !webrtc.isVideoEnabled
                ? 'bg-red-600 hover:bg-red-700'
                : 'bg-gray-700 hover:bg-gray-600'
            }`}
            title={webrtc.isVideoEnabled ? 'Turn off video' : 'Turn on video'}
          >
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {webrtc.isVideoEnabled ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
              )}
            </svg>
          </button>
        )}

        {/* Screen Share Button */}
        {webrtc.callType === 'video' && (
          <button
            onClick={webrtc.isScreenSharing ? webrtc.stopScreenShare : webrtc.startScreenShare}
            className={`p-4 rounded-full transition-colors ${
              webrtc.isScreenSharing
                ? 'bg-accent-primary hover:bg-accent-primary/90'
                : 'bg-gray-700 hover:bg-gray-600'
            }`}
            title={webrtc.isScreenSharing ? 'Stop sharing' : 'Share screen'}
          >
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </button>
        )}

        {/* End Call Button */}
        <button
          onClick={handleEndCall}
          className="p-4 rounded-full bg-red-600 hover:bg-red-700 transition-colors"
          title="End call"
        >
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 8l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2M5 3a2 2 0 00-2 2v1c0 8.284 6.716 15 15 15h1a2 2 0 002-2v-3.28a1 1 0 00-.684-.948l-4.493-1.498a1 1 0 00-1.21.502l-1.13 2.257a11.042 11.042 0 01-5.516-5.517l2.257-1.128a1 1 0 00.502-1.21L9.228 3.683A1 1 0 008.279 3H5z" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default VideoCallView;
