import React, { createContext, useContext, useCallback, useState, ReactNode } from 'react';

/**
 * WebRTC Signaling Context
 * 
 * This context bridges the gap between useWebSocket and useWebRTC hooks.
 * It allows:
 * 1. useWebSocket to deliver incoming WebRTC signals to useWebRTC
 * 2. useWebRTC to send outgoing signals through WebSocket
 * 
 * Flow:
 * - useWebRTC registers handlers for incoming signals (offer, answer, ICE)
 * - useWebSocket receives WebRTC messages and calls these handlers
 * - useWebRTC uses sendSignal to send messages through WebSocket
 */

export interface WebRTCSignal {
  type: 'webrtc_offer' | 'webrtc_answer' | 'webrtc_ice_candidate';
  senderId: string;
  targetId: string;
  data: RTCSessionDescriptionInit | RTCIceCandidateInit;
}

interface WebRTCContextType {
  // Handlers for incoming signals (set by useWebRTC)
  onOffer?: (offer: RTCSessionDescriptionInit, senderId: string) => void;
  onAnswer?: (answer: RTCSessionDescriptionInit, senderId: string) => void;
  onIceCandidate?: (candidate: RTCIceCandidateInit, senderId: string) => void;
  
  // Register handlers
  registerOfferHandler: (handler: (offer: RTCSessionDescriptionInit, senderId: string) => void) => void;
  registerAnswerHandler: (handler: (answer: RTCSessionDescriptionInit, senderId: string) => void) => void;
  registerIceCandidateHandler: (handler: (candidate: RTCIceCandidateInit, senderId: string) => void) => void;
  
  // Send signals (used by useWebRTC, implemented by WebSocket sender)
  sendSignal: (signal: WebRTCSignal) => void;
  registerSignalSender: (sender: (signal: WebRTCSignal) => void) => void;
}

const WebRTCContext = createContext<WebRTCContextType | undefined>(undefined);

interface WebRTCProviderProps {
  children: ReactNode;
}

/**
 * WebRTC Provider Component
 * 
 * Wraps the app to provide WebRTC signaling coordination
 * Place this in App.tsx, inside the Router but outside route components
 */
export const WebRTCProvider: React.FC<WebRTCProviderProps> = ({ children }) => {
  const [onOffer, setOnOffer] = useState<((offer: RTCSessionDescriptionInit, senderId: string) => void) | undefined>();
  const [onAnswer, setOnAnswer] = useState<((answer: RTCSessionDescriptionInit, senderId: string) => void) | undefined>();
  const [onIceCandidate, setOnIceCandidate] = useState<((candidate: RTCIceCandidateInit, senderId: string) => void) | undefined>();
  const [signalSender, setSignalSender] = useState<((signal: WebRTCSignal) => void) | undefined>();

  const registerOfferHandler = useCallback((handler: (offer: RTCSessionDescriptionInit, senderId: string) => void) => {
    setOnOffer(() => handler);
  }, []);

  const registerAnswerHandler = useCallback((handler: (answer: RTCSessionDescriptionInit, senderId: string) => void) => {
    setOnAnswer(() => handler);
  }, []);

  const registerIceCandidateHandler = useCallback((handler: (candidate: RTCIceCandidateInit, senderId: string) => void) => {
    setOnIceCandidate(() => handler);
  }, []);

  const registerSignalSender = useCallback((sender: (signal: WebRTCSignal) => void) => {
    setSignalSender(() => sender);
  }, []);

  const sendSignal = useCallback((signal: WebRTCSignal) => {
    if (signalSender) {
      signalSender(signal);
    } else {
      console.error('Signal sender not registered');
    }
  }, [signalSender]);

  const value: WebRTCContextType = {
    onOffer,
    onAnswer,
    onIceCandidate,
    registerOfferHandler,
    registerAnswerHandler,
    registerIceCandidateHandler,
    sendSignal,
    registerSignalSender,
  };

  return (
    <WebRTCContext.Provider value={value}>
      {children}
    </WebRTCContext.Provider>
  );
};

/**
 * Hook to access WebRTC signaling context
 */
export const useWebRTCContext = () => {
  const context = useContext(WebRTCContext);
  if (!context) {
    throw new Error('useWebRTCContext must be used within WebRTCProvider');
  }
  return context;
};
