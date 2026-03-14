import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { History, MessageSquare, Trash2, Search, ArrowRight, Calendar, Leaf, Filter } from 'lucide-react';
import { v4 as uuidv4 } from 'uuid';
import { authService } from '../services/auth';

// Returns a stable per-user storage prefix so each account is isolated
const getUserPrefix = () => {
    const token = authService.getToken();
    if (!token) return 'guest';
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return `user_${payload.sub || payload.id || 'unknown'}`;
    } catch {
        return 'guest';
    }
};

const HistoryPage = () => {
    const [historyGroups, setHistoryGroups] = useState({});
    const [searchQuery, setSearchQuery] = useState('');
    const navigate = useNavigate();
    const userPrefix = getUserPrefix();

    useEffect(() => {
        loadHistory();
    }, []);

    const loadHistory = () => {
        const historyRaw = localStorage.getItem(`${userPrefix}_chat_history_index_v2`);
        if (historyRaw) {
            const historyList = JSON.parse(historyRaw);

            // Group by date (Today, Previous 7 Days, Older)
            const grouped = {
                'Today': [],
                'Previous 7 Days': [],
                'Older': []
            };

            const today = new Date();
            today.setHours(0, 0, 0, 0);

            const sevenDaysAgo = new Date(today);
            sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

            historyList.forEach(item => {
                const itemDate = new Date(item.updatedAt);
                itemDate.setHours(0, 0, 0, 0);

                if (itemDate.getTime() === today.getTime()) {
                    grouped['Today'].push(item);
                } else if (itemDate >= sevenDaysAgo) {
                    grouped['Previous 7 Days'].push(item);
                } else {
                    grouped['Older'].push(item);
                }
            });

            setHistoryGroups(grouped);
        }
    };

    const handleOpenChat = (id) => {
        localStorage.setItem(`${userPrefix}_active_chat_thread`, id);
        navigate('/chat');
    };

    const handleNewChat = () => {
        const newId = uuidv4();
        localStorage.setItem(`${userPrefix}_active_chat_thread`, newId);
        navigate('/chat');
    };

    const handleDeleteChat = (e, id) => {
        e.stopPropagation();

        // Remove from index
        const historyRaw = localStorage.getItem(`${userPrefix}_chat_history_index_v2`) || '[]';
        const historyMeta = JSON.parse(historyRaw).filter(item => item.id !== id);
        localStorage.setItem(`${userPrefix}_chat_history_index_v2`, JSON.stringify(historyMeta));

        // Remove actual messages
        localStorage.removeItem(`${userPrefix}_chat_messages_${id}`);

        // Refresh
        loadHistory();
    };

    const filterHistory = (list) => {
        if (!searchQuery) return list;
        return list.filter(item => item.title.toLowerCase().includes(searchQuery.toLowerCase()));
    };

    return (
        <div className="p-6 lg:p-10 max-w-5xl mx-auto min-h-full">
            <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 tracking-tight flex items-center gap-3">
                        <History className="w-8 h-8 text-emerald-600" />
                        Conversation History
                    </h1>
                    <p className="text-gray-500 mt-2">Resume past optimizations and calculations.</p>
                </div>

                <button
                    onClick={handleNewChat}
                    className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2.5 rounded-xl font-semibold shadow-sm transition-all"
                >
                    <MessageSquare className="w-5 h-5" />
                    New Conversation
                </button>
            </div>

            {/* Search and Filter */}
            <div className="bg-white p-2 rounded-2xl border border-gray-200 shadow-sm mb-8 flex items-center gap-2">
                <div className="relative flex-1">
                    <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search conversations..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-10 pr-4 py-2.5 bg-transparent border-none focus:ring-0 text-sm font-medium placeholder:text-gray-400 outline-none"
                    />
                </div>
                <div className="w-px h-6 bg-gray-200 mx-1" />
                <button className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-xl transition-colors">
                    <Filter className="w-4 h-4" />
                    <span className="hidden sm:inline">Filter</span>
                </button>
            </div>

            {/* History List */}
            <div className="space-y-8">
                {Object.keys(historyGroups).some(key => filterHistory(historyGroups[key]).length > 0) ? (
                    Object.entries(historyGroups).map(([groupName, items]) => {
                        const filteredItems = filterHistory(items);
                        if (filteredItems.length === 0) return null;

                        return (
                            <motion.div
                                key={groupName}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                            >
                                <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4 px-1">
                                    {groupName}
                                </h3>
                                <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden flex flex-col divide-y divide-gray-100">
                                    <AnimatePresence>
                                        {filteredItems.map(item => (
                                            <motion.div
                                                key={item.id}
                                                layout
                                                initial={{ opacity: 0 }}
                                                animate={{ opacity: 1 }}
                                                exit={{ opacity: 0, height: 0, overflow: 'hidden' }}
                                                onClick={() => handleOpenChat(item.id)}
                                                className="group p-5 hover:bg-gray-50 transition-colors cursor-pointer flex items-center justify-between"
                                            >
                                                <div className="flex items-center gap-4 min-w-0 pr-4">
                                                    <div className="w-10 h-10 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0 border border-emerald-100 group-hover:scale-110 transition-transform">
                                                        <MessageSquare className="w-4 h-4" />
                                                    </div>
                                                    <div className="min-w-0">
                                                        <h4 className="font-semibold text-gray-900 text-[15px] truncate mb-1">
                                                            {item.title}
                                                        </h4>
                                                        <div className="flex items-center gap-3 text-xs text-gray-500 font-medium">
                                                            <span className="flex items-center gap-1">
                                                                <Calendar className="w-3.5 h-3.5" />
                                                                {new Date(item.updatedAt).toLocaleDateString()}
                                                            </span>
                                                            <span className="flex items-center gap-1 text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">
                                                                <Leaf className="w-3 h-3" /> Cached
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>

                                                <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                    <button
                                                        onClick={(e) => handleDeleteChat(e, item.id)}
                                                        className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                                                        title="Delete conversation"
                                                    >
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
                                                    <div className="p-2 text-emerald-600 bg-emerald-50 rounded-lg transition-colors">
                                                        <ArrowRight className="w-4 h-4" />
                                                    </div>
                                                </div>
                                            </motion.div>
                                        ))}
                                    </AnimatePresence>
                                </div>
                            </motion.div>
                        );
                    })
                ) : (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="text-center py-20 bg-white rounded-3xl border border-gray-200 border-dashed"
                    >
                        <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4 border border-gray-100">
                            <History className="w-8 h-8 text-gray-300" />
                        </div>
                        <h3 className="text-lg font-bold text-gray-900 mb-1">No history found</h3>
                        <p className="text-sm text-gray-500 max-w-sm mx-auto mb-6">
                            Start a new conversation to see your history organized here.
                        </p>
                        <button
                            onClick={handleNewChat}
                            className="bg-gray-900 hover:bg-black text-white px-5 py-2.5 rounded-xl font-semibold shadow-sm transition-all inline-flex items-center gap-2"
                        >
                            <MessageSquare className="w-4 h-4" />
                            Start Optimizing
                        </button>
                    </motion.div>
                )}
            </div>
        </div>
    );
};

export default HistoryPage;
