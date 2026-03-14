import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { carbonSenseAPI } from '../services/api';
import { Leaf, Zap, Database, Timer, Trees, ArrowRight, MessageSquare, Plus, Activity, Cpu } from 'lucide-react';
import { motion } from 'framer-motion';

export const Home = () => {
    const [metrics, setMetrics] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchMetrics = async () => {
            try {
                const data = await carbonSenseAPI.getMetrics();
                setMetrics(data);
            } catch (err) {
                console.error("Failed to load metrics", err);
            } finally {
                setIsLoading(false);
            }
        };
        fetchMetrics();
        const interval = setInterval(fetchMetrics, 5000);
        return () => clearInterval(interval);
    }, []);

    // Placeholder data for recent chats
    const recentChats = [
        { id: 1, title: 'Optimize Python Loop', date: '2 hours ago', icon: <Cpu className="w-4 h-4 text-emerald-500" /> },
        { id: 2, title: 'React Performance Issues', date: '5 hours ago', icon: <MessageSquare className="w-4 h-4 text-emerald-500" /> },
        { id: 3, title: 'Database Indexing Query', date: 'Yesterday', icon: <Database className="w-4 h-4 text-emerald-500" /> },
    ];

    return (
        <div className="p-6 lg:p-10 space-y-8 max-w-7xl mx-auto">
            {/* Welcome Banner */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="relative overflow-hidden rounded-3xl bg-emerald-950 p-8 sm:p-10 shadow-xl shadow-emerald-900/10 border border-emerald-900/50"
            >
                {/* Background Graphics */}
                <div className="absolute inset-0 z-0">
                    <div className="absolute right-0 top-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-[80px] -translate-y-1/2 translate-x-1/3" />
                    <div className="absolute left-0 bottom-0 w-96 h-96 bg-teal-500/10 rounded-full blur-[80px] translate-y-1/2 -translate-x-1/3" />
                    <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 mix-blend-overlay"></div>
                </div>

                <div className="relative z-10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
                    <div>
                        <div className="flex items-center gap-2 mb-4">
                            <span className="px-3 py-1 bg-white/10 text-emerald-200 text-xs font-bold uppercase tracking-wider rounded-full border border-white/10 backdrop-blur-md">
                                Enterprise Dashboard
                            </span>
                        </div>
                        <h1 className="text-3xl sm:text-4xl font-bold text-white mb-3 tracking-tight">
                            Welcome back
                        </h1>
                        <p className="text-emerald-100/70 text-lg max-w-xl leading-relaxed">
                            Your sustainable coding environment is primed and ready. You've helped save {metrics?.carbon_saved_today || '0'}g of CO2 today.
                        </p>
                    </div>

                    <button
                        onClick={() => navigate('/chat')}
                        className="group flex items-center justify-center gap-2 bg-white text-emerald-950 px-6 py-4 rounded-xl font-bold text-sm shadow-[0_0_20px_rgba(255,255,255,0.1)] hover:shadow-[0_0_30px_rgba(255,255,255,0.2)] hover:scale-105 transition-all shrink-0 w-full sm:w-auto"
                    >
                        <Plus className="w-5 h-5" />
                        New Optimization
                    </button>
                </div>
            </motion.div>

            {/* Metrics Overview */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <motion.div
                    initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
                    className="bg-white p-6 rounded-3xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group"
                >
                    <div className="absolute right-0 top-0 p-4 opacity-0 group-hover:opacity-5 transition-opacity duration-500">
                        <Trees className="w-24 h-24 text-emerald-900" />
                    </div>
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2.5 bg-emerald-50 rounded-xl text-emerald-600">
                            <Leaf className="w-5 h-5" />
                        </div>
                        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Carbon Saved</h3>
                    </div>
                    <div>
                        <div className="flex items-baseline gap-2">
                            <span className="text-4xl justify-center font-bold text-gray-900 tracking-tight">
                                {isLoading ? '-' : metrics?.carbon_saved_today || 0}
                            </span>
                            <span className="text-sm font-semibold text-gray-400">gCO2</span>
                        </div>
                        <p className="text-xs text-gray-500 mt-2 font-medium">Total saved today</p>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
                    className="bg-white p-6 rounded-3xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group"
                >
                    <div className="absolute right-0 top-0 p-4 opacity-0 group-hover:opacity-5 transition-opacity duration-500">
                        <Database className="w-24 h-24 text-teal-900" />
                    </div>
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2.5 bg-teal-50 rounded-xl text-teal-600">
                            <Database className="w-5 h-5" />
                        </div>
                        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Token Efficiency</h3>
                    </div>
                    <div>
                        <div className="flex items-baseline gap-2">
                            <span className="text-4xl font-bold text-gray-900 tracking-tight">
                                {isLoading ? '-' : metrics?.tokens_saved_percent || 0}
                            </span>
                            <span className="text-sm font-semibold text-gray-400">%</span>
                        </div>
                        <p className="text-xs text-gray-500 mt-2 font-medium">
                            {isLoading ? 'Loading' : (metrics?.tokens_saved?.toLocaleString() || '0')} tokens saved
                        </p>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
                    className="bg-white p-6 rounded-3xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group"
                >
                    <div className="absolute right-0 top-0 p-4 opacity-0 group-hover:opacity-5 transition-opacity duration-500">
                        <Zap className="w-24 h-24 text-teal-900" />
                    </div>
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2.5 bg-teal-50 rounded-xl text-teal-600">
                            <Zap className="w-5 h-5 fill-current" />
                        </div>
                        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Energy Saved</h3>
                    </div>
                    <div>
                        <div className="flex items-baseline gap-2">
                            <span className="text-4xl font-bold text-gray-900 tracking-tight">
                                {isLoading ? '-' : metrics?.energy_saved_kwh || 0}
                            </span>
                            <span className="text-sm font-semibold text-gray-400">kWh</span>
                        </div>
                        <p className="text-xs text-gray-500 mt-2 font-medium">Compared to baseline</p>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
                    className="bg-white p-6 rounded-3xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group"
                >
                    <div className="absolute right-0 top-0 p-4 opacity-0 group-hover:opacity-5 transition-opacity duration-500">
                        <Timer className="w-24 h-24 text-violet-900" />
                    </div>
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2.5 bg-violet-50 rounded-xl text-violet-600">
                            <Timer className="w-5 h-5" />
                        </div>
                        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Avg Latency</h3>
                    </div>
                    <div>
                        <div className="flex items-baseline gap-2">
                            <span className="text-4xl font-bold text-gray-900 tracking-tight">
                                {isLoading ? '-' : metrics?.response_times?.length > 0
                                    ? Math.round(metrics.response_times.reduce((a, b) => a + b.latency, 0) / metrics.response_times.length)
                                    : '--'}
                            </span>
                            <span className="text-sm font-semibold text-gray-400">ms</span>
                        </div>
                        <p className="text-xs text-gray-500 mt-2 font-medium">System response time</p>
                    </div>
                </motion.div>
            </div>

            {/* Main Content Area */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Getting Started Guide / System Status */}
                <div className="lg:col-span-2 space-y-6">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
                        className="bg-white rounded-3xl border border-gray-100 shadow-sm p-8"
                    >
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-xl font-bold text-gray-900">System Activity</h2>
                            <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 border border-emerald-100 rounded-full text-xs font-bold text-emerald-700 shadow-sm">
                                <Activity className="w-3.5 h-3.5 animate-pulse" />
                                OPTIMAL
                            </div>
                        </div>

                        <div className="space-y-6">
                            <div className="p-4 rounded-2xl bg-gray-50 border border-gray-100 flex items-start sm:items-center gap-4 flex-col sm:flex-row">
                                <div className="w-12 h-12 rounded-full bg-white flex items-center justify-center shadow-sm shrink-0 border border-gray-100">
                                    <Zap className="w-6 h-6 text-yellow-500 fill-current" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <h4 className="font-semibold text-gray-900">Current Grid Intensity</h4>
                                    <p className="text-sm text-gray-500 truncate">The power grid is running efficiently at <span className="font-mono">{metrics?.carbon_intensity || '150'} gCO2/kWh</span>. High-demand queries will be balanced.</p>
                                </div>
                            </div>

                            <div className="p-4 rounded-2xl bg-gray-50 border border-gray-100 flex items-start sm:items-center gap-4 flex-col sm:flex-row">
                                <div className="w-12 h-12 rounded-full bg-white flex items-center justify-center shadow-sm shrink-0 border border-gray-100">
                                    <Cpu className="w-6 h-6 text-teal-500" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <h4 className="font-semibold text-gray-900">Model Selection Engine</h4>
                                    <p className="text-sm text-gray-500 truncate">Automatically selecting the most efficient LLM based on your prompt's complexity and current grid load.</p>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </div>

                {/* Recent Chats Sidebar */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
                    className="bg-white rounded-3xl border border-gray-100 shadow-sm flex flex-col"
                >
                    <div className="p-6 border-b border-gray-100 flex items-center justify-between">
                        <h2 className="text-lg font-bold text-gray-900">Recent Chats</h2>
                        <button onClick={() => navigate('/history')} className="text-sm font-semibold text-emerald-600 hover:text-emerald-700">View All</button>
                    </div>

                    <div className="flex-1 p-4 space-y-2">
                        {recentChats.map((chat) => (
                            <button
                                key={chat.id}
                                className="w-full text-left p-4 rounded-2xl hover:bg-gray-50 transition-colors flex items-center gap-4 group"
                            >
                                <div className="w-10 h-10 rounded-full bg-emerald-50 flex items-center justify-center shrink-0 border border-emerald-100 group-hover:scale-110 transition-transform">
                                    {chat.icon}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <h4 className="font-semibold text-gray-900 truncate text-sm">{chat.title}</h4>
                                    <p className="text-xs text-gray-500">{chat.date}</p>
                                </div>
                                <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-emerald-500 opacity-0 group-hover:opacity-100 transition-all -translate-x-2 group-hover:translate-x-0" />
                            </button>
                        ))}
                    </div>

                    <div className="p-6 border-t border-gray-100 bg-gray-50/50 rounded-b-3xl">
                        <button
                            onClick={() => navigate('/chat')}
                            className="w-full py-3.5 px-4 bg-white border border-gray-200 rounded-xl shadow-sm text-sm font-semibold text-gray-700 hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
                        >
                            <MessageSquare className="w-4 h-4" />
                            Start New Conversation
                        </button>
                    </div>
                </motion.div>
            </div>
        </div>
    );
};
