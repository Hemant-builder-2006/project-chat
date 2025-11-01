import { useState, useRef, useCallback, useEffect } from 'react';

/**
 * WebRTC Configuration
 * Uses public STUN servers for NAT traversal
 * In production, you should use your own TURN servers
 */
const ICE_SERVERS = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' },
  ],
};

export interface WebRTCSignalingCallbacks {
  sendOffer: (targetUserId: string, offer: RTCSessionDescriptionInit) => void;
  sendAnswer: (targetUserId: string, answer: RTCSessionDescriptionInit) => void;
  sendIceCandidate: (targetUserId: string, candidate: RTCIceCandidate) => void;
}

interface UseWebRTCProps {
  onSignal: WebRTCSignalingCallbacks;
}

/**
 * useWebRTC Hook
 * 
 * Manages WebRTC peer connections, media streams, and call state
 * Handles: 1:1 calls, group voice channels, screen sharing
 * 
 * This hook manages the RTCPeerConnection lifecycle:
 * 1. Creates peer connections for each remote user
 * 2. Handles ICE candidate gathering and exchange
 * 3. Manages local and remote media streams
 * 4. Provides controls for mute, video, screen sharing
 */
export const useWebRTC = ({ onSignal }: UseWebRTCProps) => {
  // Media stream state
  const [localStream, setLocalStream] = useState<MediaStream | null>(null);
  const [remoteStreams, setRemoteStreams] = useState<Record<string, MediaStream>>({});
  
  // Control state
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoEnabled, setIsVideoEnabled] = useState(true);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [isInCall, setIsInCall] = useState(false);
  const [callType, setCallType] = useState<'voice' | 'video' | null>(null);

  // Refs for peer connections and original video track
  const peerConnectionsRef = useRef<Record<string, RTCPeerConnection>>({});
  const originalVideoTrackRef = useRef<MediaStreamTrack | null>(null);
  const currentChannelRef = useRef<string | null>(null);

  /**
   * Get user media (audio/video)
   */
  const getUserMedia = useCallback(async (video: boolean = true) => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
        video: video ? {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user',
        } : false,
      });

      setLocalStream(stream);
      
      // Store original video track for screen share toggle
      if (video) {
        const videoTrack = stream.getVideoTracks()[0];
        if (videoTrack) {
          originalVideoTrackRef.current = videoTrack;
        }
      }

      return stream;
    } catch (error) {
      console.error('Error accessing media devices:', error);
      throw error;
    }
  }, []);

  /**
   * Create a peer connection for a specific user
   */
  const createPeerConnection = useCallback((userId: string, stream: MediaStream) => {
    const peerConnection = new RTCPeerConnection(ICE_SERVERS);

    // Add local tracks to peer connection
    stream.getTracks().forEach(track => {
      peerConnection.addTrack(track, stream);
    });

    // Handle ICE candidates
    peerConnection.onicecandidate = (event) => {
      if (event.candidate) {
        onSignal.sendIceCandidate(userId, event.candidate);
      }
    };

    // Handle remote stream
    peerConnection.ontrack = (event) => {
      console.log('Received remote track from:', userId);
      const [remoteStream] = event.streams;
      
      setRemoteStreams(prev => ({
        ...prev,
        [userId]: remoteStream,
      }));
    };

    // Handle connection state changes
    peerConnection.onconnectionstatechange = () => {
      console.log(`Connection state with ${userId}:`, peerConnection.connectionState);
      
      if (peerConnection.connectionState === 'disconnected' || 
          peerConnection.connectionState === 'failed' ||
          peerConnection.connectionState === 'closed') {
        // Remove remote stream
        setRemoteStreams(prev => {
          const newStreams = { ...prev };
          delete newStreams[userId];
          return newStreams;
        });
      }
    };

    peerConnectionsRef.current[userId] = peerConnection;
    return peerConnection;
  }, [onSignal]);

  /**
   * Join a voice channel (audio only)
   */
  const joinVoiceChannel = useCallback(async (channelId: string) => {
    try {
      const stream = await getUserMedia(false); // Audio only
      currentChannelRef.current = channelId;
      setIsInCall(true);
      setCallType('voice');
      
      // Notify server that we're joining the voice channel
      // The server will send us the list of users already in the channel
      // and notify other users that we've joined
      
      return stream;
    } catch (error) {
      console.error('Error joining voice channel:', error);
      throw error;
    }
  }, [getUserMedia]);

  /**
   * Start a 1:1 video call
   */
  const startCall = useCallback(async (targetUserId: string) => {
    try {
      const stream = await getUserMedia(true); // Audio + Video
      const peerConnection = createPeerConnection(targetUserId, stream);
      
      // Create offer
      const offer = await peerConnection.createOffer();
      await peerConnection.setLocalDescription(offer);
      
      // Send offer through signaling
      onSignal.sendOffer(targetUserId, offer);
      
      setIsInCall(true);
      setCallType('video');
      
      console.log('Call started with:', targetUserId);
    } catch (error) {
      console.error('Error starting call:', error);
      throw error;
    }
  }, [getUserMedia, createPeerConnection, onSignal]);

  /**
   * Accept an incoming call (handle offer)
   */
  const acceptCall = useCallback(async (offer: RTCSessionDescriptionInit, senderId: string) => {
    try {
      // Determine if this is video or audio based on offer
      const hasVideo = offer.sdp?.includes('m=video');
      const stream = await getUserMedia(hasVideo);
      
      const peerConnection = createPeerConnection(senderId, stream);
      
      // Set remote description (the offer)
      await peerConnection.setRemoteDescription(new RTCSessionDescription(offer));
      
      // Create answer
      const answer = await peerConnection.createAnswer();
      await peerConnection.setLocalDescription(answer);
      
      // Send answer through signaling
      onSignal.sendAnswer(senderId, answer);
      
      setIsInCall(true);
      setCallType(hasVideo ? 'video' : 'voice');
      
      console.log('Call accepted from:', senderId);
    } catch (error) {
      console.error('Error accepting call:', error);
      throw error;
    }
  }, [getUserMedia, createPeerConnection, onSignal]);

  /**
   * Handle incoming answer
   */
  const handleAnswer = useCallback(async (answer: RTCSessionDescriptionInit, senderId: string) => {
    try {
      const peerConnection = peerConnectionsRef.current[senderId];
      if (peerConnection) {
        await peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
        console.log('Answer processed from:', senderId);
      }
    } catch (error) {
      console.error('Error handling answer:', error);
    }
  }, []);

  /**
   * Handle incoming ICE candidate
   */
  const handleIceCandidate = useCallback(async (candidate: RTCIceCandidateInit, senderId: string) => {
    try {
      const peerConnection = peerConnectionsRef.current[senderId];
      if (peerConnection) {
        await peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
        console.log('ICE candidate added from:', senderId);
      }
    } catch (error) {
      console.error('Error handling ICE candidate:', error);
    }
  }, []);

  /**
   * End call and cleanup
   */
  const endCall = useCallback(() => {
    // Stop all local tracks
    if (localStream) {
      localStream.getTracks().forEach(track => track.stop());
      setLocalStream(null);
    }

    // Close all peer connections
    Object.values(peerConnectionsRef.current).forEach(pc => {
      pc.close();
    });
    peerConnectionsRef.current = {};

    // Clear remote streams
    setRemoteStreams({});
    
    // Reset state
    setIsInCall(false);
    setCallType(null);
    setIsScreenSharing(false);
    currentChannelRef.current = null;
    originalVideoTrackRef.current = null;

    console.log('Call ended');
  }, [localStream]);

  /**
   * Toggle microphone mute
   */
  const toggleMute = useCallback(() => {
    if (localStream) {
      const audioTrack = localStream.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        setIsMuted(!audioTrack.enabled);
      }
    }
  }, [localStream]);

  /**
   * Toggle video on/off
   */
  const toggleVideo = useCallback(() => {
    if (localStream) {
      const videoTrack = localStream.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        setIsVideoEnabled(videoTrack.enabled);
      }
    }
  }, [localStream]);

  /**
   * Start screen sharing
   */
  const startScreenShare = useCallback(async () => {
    try {
      const screenStream = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: false,
      });

      const screenTrack = screenStream.getVideoTracks()[0];

      // Replace video track in all peer connections
      Object.values(peerConnectionsRef.current).forEach(pc => {
        const sender = pc.getSenders().find(s => s.track?.kind === 'video');
        if (sender) {
          sender.replaceTrack(screenTrack);
        }
      });

      // Update local stream
      if (localStream) {
        const audioTrack = localStream.getAudioTracks()[0];
        const newStream = new MediaStream([audioTrack, screenTrack]);
        setLocalStream(newStream);
      }

      // Handle screen share stop
      screenTrack.onended = () => {
        stopScreenShare();
      };

      setIsScreenSharing(true);
      console.log('Screen sharing started');
    } catch (error) {
      console.error('Error starting screen share:', error);
      throw error;
    }
  }, [localStream]);

  /**
   * Stop screen sharing
   */
  const stopScreenShare = useCallback(async () => {
    if (!originalVideoTrackRef.current || !localStream) return;

    try {
      // Stop current screen track
      const screenTrack = localStream.getVideoTracks()[0];
      if (screenTrack) {
        screenTrack.stop();
      }

      // Get new camera stream or use original track
      const cameraStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user',
        },
      });

      const cameraTrack = cameraStream.getVideoTracks()[0];

      // Replace screen track with camera track in all peer connections
      Object.values(peerConnectionsRef.current).forEach(pc => {
        const sender = pc.getSenders().find(s => s.track?.kind === 'video');
        if (sender) {
          sender.replaceTrack(cameraTrack);
        }
      });

      // Update local stream
      const audioTrack = localStream.getAudioTracks()[0];
      const newStream = new MediaStream([audioTrack, cameraTrack]);
      setLocalStream(newStream);
      originalVideoTrackRef.current = cameraTrack;

      setIsScreenSharing(false);
      console.log('Screen sharing stopped');
    } catch (error) {
      console.error('Error stopping screen share:', error);
      throw error;
    }
  }, [localStream]);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      endCall();
    };
  }, [endCall]);

  return {
    // State
    localStream,
    remoteStreams,
    isMuted,
    isVideoEnabled,
    isScreenSharing,
    isInCall,
    callType,

    // Actions
    joinVoiceChannel,
    startCall,
    acceptCall,
    handleAnswer,
    handleIceCandidate,
    endCall,
    toggleMute,
    toggleVideo,
    startScreenShare,
    stopScreenShare,
  };
};
