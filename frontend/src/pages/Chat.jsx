import React, { useState, useEffect, useRef } from 'react';
import { ChatInterface } from '../components/chat/ChatInterface';
import { carbonSenseAPI } from '../services/api';
import { authService } from '../services/auth';
import { v4 as uuidv4 } from 'uuid';

// Returns a stable per-user storage prefix so each account is isolated
const getUserPrefix = () => {
    const token = authService.getToken();
    if (!token) return 'guest';
    try {
        // JWT payload is base64url-encoded — decode user id / email from it
        const payload = JSON.parse(atob(token.split('.')[1]));
        // FastAPI-issued tokens typically use 'sub' as the email/id
        return `user_${payload.sub || payload.id || 'unknown'}`;
    } catch {
        return 'guest';
    }
};

const Chat = () => {
    const userPrefix = getUserPrefix();

    const [currentThreadId, setCurrentThreadId] = useState(() => {
        return localStorage.getItem(`${userPrefix}_active_chat_thread`) || uuidv4();
    });

    const [messages, setMessages] = useState(() => {
        const activeThread = localStorage.getItem(`${userPrefix}_active_chat_thread`);
        const saved = activeThread
            ? localStorage.getItem(`${userPrefix}_chat_messages_${activeThread}`)
            : null;
        return saved ? JSON.parse(saved) : [
            { role: 'assistant', content: 'Hello! I am CarbonSense AI. How can I help you today while prioritizing sustainable computation?' }
        ];
    });

    const [isLoading, setIsLoading] = useState(false);
    const [liveMetrics, setLiveMetrics] = useState(null);
    const metricsIntervalRef = useRef(null);

    // Fetch live metrics from backend
    const fetchLiveMetrics = async () => {
        try {
            const data = await carbonSenseAPI.getMetrics();
            setLiveMetrics(data);
        } catch (e) {
            console.error('Failed to fetch live metrics:', e);
        }
    };

    // Poll metrics every 5 seconds
    useEffect(() => {
        fetchLiveMetrics();
        metricsIntervalRef.current = setInterval(fetchLiveMetrics, 5000);
        return () => clearInterval(metricsIntervalRef.current);
    }, []);

    // Save messages to current thread (scoped to this user)
    useEffect(() => {
        localStorage.setItem(`${userPrefix}_chat_messages_${currentThreadId}`, JSON.stringify(messages));

        const historyRaw = localStorage.getItem(`${userPrefix}_chat_history_index_v2`) || '[]';
        let historyMeta = JSON.parse(historyRaw);

        const existingIndex = historyMeta.findIndex(meta => meta.id === currentThreadId);
        const title = messages[messages.length > 1 ? 1 : 0].content.substring(0, 40) + '...';
        const timestamp = new Date().toISOString();

        if (existingIndex > -1) {
            historyMeta[existingIndex] = { ...historyMeta[existingIndex], updatedAt: timestamp };
        } else {
            historyMeta.unshift({ id: currentThreadId, title, updatedAt: timestamp });
        }

        localStorage.setItem(`${userPrefix}_chat_history_index_v2`, JSON.stringify(historyMeta));
        localStorage.setItem(`${userPrefix}_active_chat_thread`, currentThreadId);
    }, [messages, currentThreadId, userPrefix]);

    const handleSendMessage = async (text, fileContext = null) => {
        const userMsg = { role: 'user', content: text, context: fileContext };
        setMessages(prev => [...prev, userMsg]);
        setIsLoading(true);

        try {
            let combinedInput = text;
            if (fileContext) {
                combinedInput = `Context given: "${fileContext}"\n\nUser Question: ${text}`;
            }

            const response = await carbonSenseAPI.sendQuery(combinedInput);

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: response.text,
                metrics: { ...response }
            }]);

            fetchLiveMetrics();
        } catch (error) {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "Sorry, I encountered an error linking to the carbon-aware grid. Please try again."
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleFeedback = async (query, rating) => {
        try {
            await carbonSenseAPI.sendFeedback(query, rating);
        } catch (e) {
            console.error("Feedback failed", e);
        }
    };

    return (
        <div className="h-full flex bg-white">
            <ChatInterface
                messages={messages}
                onSendMessage={handleSendMessage}
                onFeedback={handleFeedback}
                isLoading={isLoading}
                liveMetrics={liveMetrics}
            />
        </div>
    );
};

export default Chat;
