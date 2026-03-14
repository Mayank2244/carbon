import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
    Send, Cpu, Leaf, Star, Mic, Download, RefreshCw,
    Paperclip, FileText, X, User, Plus,
    Zap, Activity, TrendingDown, Database, Gauge,
    ChevronDown
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { carbonSenseAPI } from '../../services/api';

// ─────────────────────────────────────────────────────────
// Suggested Prompt Cards (shown on empty / welcome state)
// ─────────────────────────────────────────────────────────
const SUGGESTED_PROMPTS = [
    {
        icon: Leaf,
        title: 'Carbon footprint',
        sub: 'How can I reduce my AI workload\'s carbon impact?',
    },
    {
        icon: Zap,
        title: 'Grid intensity',
        sub: 'What does carbon intensity mean and why does it matter?',
    },
    {
        icon: Activity,
        title: 'Energy savings',
        sub: 'Compare energy usage between GPT-4o-mini vs Gemini Flash',
    },
    {
        icon: TrendingDown,
        title: 'Token optimization',
        sub: 'How does prompt compression improve sustainability?',
    },
];

// ─────────────────────────────────────────────────────────
// Welcome Screen
// ─────────────────────────────────────────────────────────
const WelcomeScreen = ({ onPromptClick }) => (
    <div className="flex flex-col items-center justify-center flex-1 px-4 pb-40">
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="flex flex-col items-center text-center max-w-2xl"
        >
            {/* Logo */}
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center mb-5 shadow-2xl shadow-emerald-500/30">
                <SparklesIcon className="w-8 h-8 text-white" />
            </div>

            <h1 className="text-3xl font-bold text-gray-900 mb-2">
                How can I help you today?
            </h1>
            <p className="text-gray-500 text-base mb-10">
                CarbonSense AI — sustainable intelligence for every query.
            </p>

            {/* Suggested prompts */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full">
                {SUGGESTED_PROMPTS.map((p, i) => {
                    const Icon = p.icon;
                    return (
                        <motion.button
                            key={i}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 + i * 0.07 }}
                            onClick={() => onPromptClick(p.sub)}
                            className="flex items-start gap-3 p-4 text-left rounded-2xl border border-gray-200 bg-white hover:border-emerald-300 hover:bg-emerald-50/50 transition-all group shadow-sm hover:shadow-md"
                        >
                            <div className="p-2 rounded-xl bg-gray-100 group-hover:bg-emerald-100 transition-colors shrink-0">
                                <Icon className="w-4 h-4 text-gray-500 group-hover:text-emerald-600 transition-colors" />
                            </div>
                            <div>
                                <div className="text-sm font-semibold text-gray-800 mb-0.5">{p.title}</div>
                                <div className="text-xs text-gray-500 leading-snug">{p.sub}</div>
                            </div>
                        </motion.button>
                    );
                })}
            </div>
        </motion.div>
    </div>
);

// ─────────────────────────────────────────────────────────
// Carbon metrics pill shown under AI messages
// ─────────────────────────────────────────────────────────
const MetricsPill = ({ metrics, idx, ratedMessages, onRate }) => (
    <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="mt-4 flex flex-wrap items-center gap-2"
    >
        <span className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-50 border border-emerald-200/80 rounded-full text-xs font-semibold text-emerald-700">
            <Leaf className="w-3 h-3" />
            {Number(metrics.saved_gco2 || 0).toFixed(2)}g CO₂ saved
        </span>
        <span className="flex items-center gap-1.5 px-2.5 py-1 bg-gray-100 border border-gray-200 rounded-full text-xs font-medium text-gray-600">
            <Cpu className="w-3 h-3 text-gray-400" />
            {metrics.model || 'Optimal Model'}
        </span>
        {metrics.metadata && metrics.metadata.rag_context_used && (
            <span className="flex items-center gap-1.5 px-2.5 py-1 bg-teal-50 border border-teal-200/80 rounded-full text-xs font-semibold text-teal-700" title="Answered using verified knowledge base factual data">
                <Database className="w-3 h-3 text-teal-500" />
                Knowledge Base
            </span>
        )}
        {/* Stars */}
        <div className="ml-auto flex items-center gap-0.5">
            {[1, 2, 3, 4, 5].map((star) => (
                <button
                    key={star}
                    onClick={() => onRate(idx, star)}
                    disabled={!!ratedMessages[idx]}
                    className={`p-0.5 rounded transition-all hover:scale-110
                        ${(ratedMessages[idx] || 0) >= star
                            ? 'text-yellow-400'
                            : 'text-gray-300 hover:text-yellow-400'}`}
                >
                    <Star className="w-3.5 h-3.5 fill-current" />
                </button>
            ))}
        </div>
    </motion.div>
);

// ─────────────────────────────────────────────────────────
// Markdown styles
// ─────────────────────────────────────────────────────────
const mdComponents = {
    code({ node, inline, className, children, ...props }) {
        const match = /language-(\w+)/.exec(className || '');
        return !inline && match ? (
            <div className="relative my-4 overflow-hidden rounded-xl bg-[#0D1117] border border-gray-800">
                <div className="flex items-center justify-between px-4 py-2 bg-[#161B22] border-b border-gray-800">
                    <span className="text-xs font-mono text-gray-400">{match[1]}</span>
                    <button
                        onClick={() => navigator.clipboard.writeText(String(children))}
                        className="text-xs text-gray-500 hover:text-white transition-colors"
                    >Copy</button>
                </div>
                <code className={`${className} block p-4 overflow-x-auto font-mono text-[13px] leading-relaxed text-gray-100`} {...props}>{children}</code>
            </div>
        ) : (
            <code className={`${className} bg-gray-100 text-pink-600 rounded px-1.5 py-0.5 font-mono text-sm`} {...props}>{children}</code>
        );
    },
    ul: ({ node, ...p }) => <ul className="list-disc pl-6 space-y-1.5 my-3" {...p} />,
    ol: ({ node, ...p }) => <ol className="list-decimal pl-6 space-y-1.5 my-3" {...p} />,
    li: ({ node, ...p }) => <li className="text-[15px] text-gray-700" {...p} />,
    h1: ({ node, ...p }) => <h1 className="text-2xl font-bold mt-6 mb-3 text-gray-900 border-b border-gray-200 pb-2" {...p} />,
    h2: ({ node, ...p }) => <h2 className="text-xl font-bold mt-5 mb-2 text-gray-900" {...p} />,
    h3: ({ node, ...p }) => <h3 className="text-lg font-semibold mt-4 mb-1.5 text-gray-900" {...p} />,
    blockquote: ({ node, ...p }) => <blockquote className="border-l-4 border-emerald-400 bg-emerald-50/60 pl-4 py-2 italic text-gray-600 my-4 rounded-r-xl" {...p} />,
    a: ({ node, ...p }) => <a className="text-emerald-600 hover:underline font-medium" target="_blank" rel="noopener noreferrer" {...p} />,
    p: ({ node, ...p }) => <p className="mb-3 text-[15px] leading-7 text-gray-700 last:mb-0" {...p} />,
    strong: ({ node, ...p }) => <strong className="font-semibold text-gray-900" {...p} />,
    table: ({ node, ...p }) => <div className="overflow-x-auto my-4"><table className="w-full text-sm border-collapse" {...p} /></div>,
    th: ({ node, ...p }) => <th className="border border-gray-200 bg-gray-50 px-3 py-2 text-left font-semibold text-gray-800" {...p} />,
    td: ({ node, ...p }) => <td className="border border-gray-200 px-3 py-2 text-gray-700" {...p} />,
};

// ─────────────────────────────────────────────────────────
// Main ChatInterface
// ─────────────────────────────────────────────────────────
export const ChatInterface = ({ messages, onSendMessage, onFeedback, isLoading, liveMetrics }) => {
    const [input, setInput] = useState('');
    const [ratedMessages, setRatedMessages] = useState({});
    const [isRecording, setIsRecording] = useState(false);
    const [attachedFile, setAttachedFile] = useState(null);
    const [fileContext, setFileContext] = useState(null);
    const [showScrollBtn, setShowScrollBtn] = useState(false);

    const messagesEndRef = useRef(null);
    const scrollAreaRef = useRef(null);
    const fileInputRef = useRef(null);
    const textareaRef = useRef(null);

    // Only the greeting message = "empty" for welcome screen purposes
    const isWelcome = messages.length <= 1;

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(scrollToBottom, [messages]);

    // Show/hide scroll-to-bottom button
    useEffect(() => {
        const el = scrollAreaRef.current;
        if (!el) return;
        const handleScroll = () => {
            setShowScrollBtn(el.scrollHeight - el.scrollTop - el.clientHeight > 200);
        };
        el.addEventListener('scroll', handleScroll);
        return () => el.removeEventListener('scroll', handleScroll);
    }, []);

    // Auto-resize textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
        }
    }, [input]);

    const handleSubmit = (e) => {
        e?.preventDefault();
        if ((input.trim() || fileContext) && !isLoading) {
            onSendMessage(input, fileContext);
            setInput('');
            setAttachedFile(null);
            setFileContext(null);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    const handleRate = (idx, rating) => {
        if (!ratedMessages[idx]) {
            setRatedMessages(prev => ({ ...prev, [idx]: rating }));
            onFeedback(messages[idx - 1]?.content || '', rating);
        }
    };

    const handlePromptClick = (text) => {
        onSendMessage(text, null);
    };

    const handleExport = () => {
        const report = messages.map(m =>
            `[${m.role.toUpperCase()}]\n${m.content}\n${m.metrics ? `METRICS: ${JSON.stringify(m.metrics)}` : ''}\n`
        ).join('\n---\n');
        const blob = new Blob([report], { type: 'text/plain' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `carbonsense-${new Date().toISOString()}.txt`;
        a.click();
    };

    const startListening = () => {
        if (!('webkitSpeechRecognition' in window)) { alert('Speech API not supported.'); return; }
        const r = new window.webkitSpeechRecognition();
        r.lang = 'en-US';
        r.onstart = () => setIsRecording(true);
        r.onresult = (e) => { setInput(prev => prev + (prev ? ' ' : '') + e.results[0][0].transcript); setIsRecording(false); };
        r.onerror = r.onend = () => setIsRecording(false);
        r.start();
    };

    const handleFileSelect = async (e) => {
        const file = e.target.files?.[0];
        if (!file) return;
        if (file.type !== 'application/pdf') { alert('Only PDF files are supported.'); return; }
        try {
            setAttachedFile({ name: file.name, status: 'uploading' });
            const resp = await carbonSenseAPI.uploadFile(file);
            setAttachedFile({ name: file.name, status: 'ready' });
            setFileContext(resp.text_content);
        } catch {
            setAttachedFile({ name: file.name, status: 'error' });
        }
    };

    return (
        <div className="flex flex-col h-full w-full bg-white relative">

            {/* ── Top bar ── */}
            <div className="h-12 px-6 border-b border-gray-100 flex items-center justify-between bg-white z-20 shrink-0">
                <div className="flex items-center gap-2.5">
                    <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-100">
                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                        <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-700">CarbonSense AI</span>
                    </div>
                    {liveMetrics && (
                        <span className="hidden sm:inline text-xs text-gray-400 font-medium">
                            Grid: <span className={`font-semibold ${liveMetrics.carbon_intensity < 150 ? 'text-emerald-500' : liveMetrics.carbon_intensity < 300 ? 'text-amber-500' : 'text-rose-500'}`}>
                                {liveMetrics.carbon_intensity?.toFixed(0)} gCO₂/kWh
                            </span>
                        </span>
                    )}
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={handleExport}
                        className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-900 hover:bg-gray-100 px-3 py-1.5 rounded-lg transition-colors font-medium"
                    >
                        <Download className="w-3.5 h-3.5" /> Export
                    </button>
                </div>
            </div>

            {/* ── Messages / Welcome ── */}
            <div ref={scrollAreaRef} className="flex-1 overflow-y-auto">
                {isWelcome ? (
                    <WelcomeScreen onPromptClick={handlePromptClick} />
                ) : (
                    <div className="pb-40">
                        <AnimatePresence>
                            {messages.map((msg, idx) => {
                                const isUser = msg.role === 'user';
                                return (
                                    <motion.div
                                        key={idx}
                                        initial={{ opacity: 0, y: 8 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ duration: 0.25 }}
                                        className={`flex w-full px-4 py-3 ${isUser ? 'justify-end' : 'justify-start'}`}
                                    >
                                        {/* AI Avatar */}
                                        {!isUser && (
                                            <div className="shrink-0 mt-0.5 mr-3">
                                                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-sm shadow-emerald-400/30">
                                                    <SparklesIcon className="w-4 h-4 text-white" />
                                                </div>
                                            </div>
                                        )}

                                        {/* Bubble / content */}
                                        <div className={`max-w-[80%] ${isUser ? 'max-w-[70%]' : 'flex-1 max-w-3xl'}`}>
                                            {isUser ? (
                                                /* User bubble */
                                                <div className="bg-gray-100 text-gray-900 px-4 py-3 rounded-2xl rounded-tr-sm text-[15px] leading-relaxed whitespace-pre-wrap font-medium">
                                                    {msg.content}
                                                    {msg.context && (
                                                        <div className="mt-2 flex items-center gap-1.5 text-xs text-gray-500">
                                                            <FileText className="w-3.5 h-3.5" />
                                                            <span>Document attached</span>
                                                        </div>
                                                    )}
                                                </div>
                                            ) : (
                                                /* AI response */
                                                <div>
                                                    <div className="prose prose-emerald max-w-none">
                                                        <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
                                                            {msg.content}
                                                        </ReactMarkdown>
                                                    </div>
                                                    {msg.metrics && (
                                                        <MetricsPill
                                                            metrics={msg.metrics}
                                                            idx={idx}
                                                            ratedMessages={ratedMessages}
                                                            onRate={handleRate}
                                                        />
                                                    )}
                                                </div>
                                            )}
                                        </div>

                                        {/* User Avatar */}
                                        {isUser && (
                                            <div className="shrink-0 mt-0.5 ml-3">
                                                <div className="w-8 h-8 rounded-full bg-gray-800 flex items-center justify-center shadow-sm">
                                                    <User className="w-4 h-4 text-white" />
                                                </div>
                                            </div>
                                        )}
                                    </motion.div>
                                );
                            })}
                        </AnimatePresence>

                        {/* Loading indicator */}
                        {isLoading && (
                            <motion.div
                                initial={{ opacity: 0, y: 8 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="flex items-start gap-3 px-4 py-3"
                            >
                                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-sm shadow-emerald-400/30 shrink-0">
                                    <SparklesIcon className="w-4 h-4 text-white" />
                                </div>
                                <div className="flex items-center gap-1.5 pt-2">
                                    {[0, 150, 300].map(delay => (
                                        <span
                                            key={delay}
                                            className="w-2 h-2 rounded-full bg-emerald-500 animate-bounce"
                                            style={{ animationDelay: `${delay}ms` }}
                                        />
                                    ))}
                                </div>
                            </motion.div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>
                )}
            </div>

            {/* Scroll to bottom button */}
            <AnimatePresence>
                {showScrollBtn && (
                    <motion.button
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.8 }}
                        onClick={scrollToBottom}
                        className="absolute bottom-36 left-1/2 -translate-x-1/2 z-30 bg-white border border-gray-200 shadow-md rounded-full px-4 py-1.5 text-xs font-semibold text-gray-600 hover:bg-gray-50 flex items-center gap-1.5 transition-colors"
                    >
                        <ChevronDown className="w-3.5 h-3.5" /> Scroll to bottom
                    </motion.button>
                )}
            </AnimatePresence>

            {/* ── Input Area (sticky bottom, ChatGPT-style) ── */}
            <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-white via-white/95 to-transparent pt-8 pb-5 px-4 pointer-events-none">
                <div className="max-w-3xl mx-auto pointer-events-auto">
                    {/* Attached file chip */}
                    {attachedFile && (
                        <div className="mb-2 flex">
                            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-semibold border shadow-sm ${attachedFile.status === 'error' ? 'bg-red-50 text-red-600 border-red-200' :
                                attachedFile.status === 'ready' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                                    'bg-white text-gray-600 border-gray-200'
                                }`}>
                                <FileText className="w-3.5 h-3.5" />
                                {attachedFile.name}
                                {attachedFile.status === 'uploading' && <RefreshCw className="w-3 h-3 animate-spin ml-1" />}
                                <button onClick={() => { setAttachedFile(null); setFileContext(null); }} className="ml-1.5 hover:text-red-500 transition-colors">
                                    <X className="w-3 h-3" />
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Input box */}
                    <form
                        onSubmit={handleSubmit}
                        className="relative flex flex-col bg-white border border-gray-300 rounded-2xl shadow-[0_4px_24px_rgba(0,0,0,0.08)] focus-within:border-emerald-400 focus-within:ring-4 focus-within:ring-emerald-500/10 transition-all overflow-hidden"
                    >
                        <textarea
                            ref={textareaRef}
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder={isLoading ? 'Waiting for response...' : 'Message CarbonSense AI…'}
                            disabled={isLoading}
                            rows={1}
                            className="w-full bg-transparent text-gray-900 placeholder:text-gray-400 px-4 pt-4 pb-2 pr-14 focus:outline-none resize-none font-medium max-h-[200px] text-[15px]"
                        />

                        {/* Toolbar row */}
                        <div className="flex items-center justify-between px-3 pb-3 pt-0.5">
                            <div className="flex items-center gap-1">
                                <input
                                    type="file"
                                    ref={fileInputRef}
                                    onChange={handleFileSelect}
                                    accept=".pdf"
                                    className="hidden"
                                />
                                <button
                                    type="button"
                                    onClick={() => fileInputRef.current?.click()}
                                    title="Attach PDF"
                                    className="p-1.5 rounded-lg text-gray-400 hover:text-emerald-600 hover:bg-emerald-50 transition-colors"
                                >
                                    <Paperclip className="w-4.5 h-4.5" />
                                </button>
                                <button
                                    type="button"
                                    onClick={isRecording ? () => setIsRecording(false) : startListening}
                                    title="Voice input"
                                    className={`p-1.5 rounded-lg transition-colors ${isRecording
                                        ? 'text-red-500 bg-red-50 animate-pulse'
                                        : 'text-gray-400 hover:text-emerald-600 hover:bg-emerald-50'
                                        }`}
                                >
                                    <Mic className="w-4.5 h-4.5" />
                                </button>
                            </div>

                            {/* Send button */}
                            <button
                                type="submit"
                                disabled={(!input.trim() && !fileContext) || isLoading}
                                className="w-8 h-8 rounded-xl flex items-center justify-center bg-gray-900 text-white disabled:opacity-30 disabled:bg-gray-200 disabled:text-gray-400 hover:bg-emerald-600 transition-colors shadow-sm"
                            >
                                <Send className="w-4 h-4" />
                            </button>
                        </div>
                    </form>

                    <p className="text-center mt-2 text-[11px] text-gray-400">
                        CarbonSense AI optimises for carbon efficiency. Always verify critical information.
                    </p>
                </div>
            </div>
        </div>
    );
};

// Helper sparkle icon
function SparklesIcon(props) {
    return (
        <svg fill="currentColor" viewBox="0 0 24 24" {...props}>
            <path d="M12 2L14.2625 9.73754L22 12L14.2625 14.2625L12 22L9.73754 14.2625L2 12L9.73754 9.73754L12 2Z" />
        </svg>
    );
}
