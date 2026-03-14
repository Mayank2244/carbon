import React, { useState, useEffect } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import {
    Leaf,
    LayoutDashboard,
    MessageSquare,
    History,
    BarChart3,
    Activity,
    User,
    LogOut,
    Menu,
    X,
    Bell,
    Search
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { authService } from '../../services/auth';

export const Layout = ({ children }) => {
    const [user, setUser] = useState(null);
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        // Read user info directly from the JWT token stored in localStorage.
        const token = authService.getToken();
        if (token) {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                setUser({
                    email: payload.email || '',
                    full_name: payload.full_name || payload.email || 'User',
                });
            } catch {
                setUser(null);
            }
        }
    }, []);

    const handleLogout = () => {
        authService.logout();
        setUser(null);
        navigate('/auth');
    };

    const navItems = [
        { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
        { path: '/chat', icon: MessageSquare, label: 'AI Chat' },
        { path: '/history', icon: History, label: 'Chat History' },
        { path: '/analytics', icon: BarChart3, label: 'Analytics' },
        { path: '/live-metrics', icon: Activity, label: 'Live Metrics' },
    ];

    return (
        <div className="flex h-screen bg-[#FAFAFA] text-gray-900 overflow-hidden font-sans selection:bg-emerald-500/20 selection:text-emerald-900">
            {/* Mobile Sidebar Overlay */}
            <AnimatePresence>
                {!isSidebarOpen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/20 z-40 lg:hidden backdrop-blur-sm"
                        onClick={() => setIsSidebarOpen(true)}
                    />
                )}
            </AnimatePresence>

            {/* Sidebar */}
            <motion.aside
                className={`fixed lg:static inset-y-0 left-0 z-50 w-72 bg-white border-r border-gray-200/60 shadow-[4px_0_24px_rgba(0,0,0,0.02)] flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0 ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}
            >
                {/* Logo Area */}
                <div className="h-20 flex items-center px-6 border-b border-gray-100">
                    <div className="flex items-center gap-3 w-full">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center shadow-lg shadow-emerald-500/20 border border-emerald-100">
                            <Leaf className="w-5 h-5 text-white" />
                        </div>
                        <div className="flex-1">
                            <span className="font-bold text-lg tracking-tight text-gray-900 block leading-tight">
                                CarbonSense AI
                            </span>
                            <span className="text-[10px] uppercase tracking-wider font-semibold text-emerald-600">Enterprise Edition</span>
                        </div>
                        <button className="lg:hidden text-gray-400 hover:text-gray-900" onClick={() => setIsSidebarOpen(false)}>
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                {/* Navigation Links */}
                <div className="flex-1 overflow-y-auto py-6 px-4 space-y-1 scrollbar-none">
                    <div className="mb-4 px-3 text-[11px] font-bold tracking-wider text-gray-400 uppercase">Menu</div>
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = location.pathname === item.path;
                        return (
                            <NavLink
                                key={item.path}
                                to={item.path}
                                className={`relative flex items-center gap-3 px-3 py-3 rounded-xl text-sm font-medium transition-all group ${isActive
                                    ? 'text-emerald-700 bg-emerald-50/50'
                                    : 'text-gray-500 hover:text-gray-900 hover:bg-gray-50'
                                    }`}
                            >
                                {isActive && (
                                    <motion.div
                                        layoutId="active-navIndicator"
                                        className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-emerald-500 rounded-r-full"
                                    />
                                )}
                                <Icon className={`w-5 h-5 transition-colors ${isActive ? 'text-emerald-600' : 'text-gray-400 group-hover:text-gray-600'}`} />
                                {item.label}
                            </NavLink>
                        );
                    })}
                </div>

                {/* User Area Footer */}
                <div className="p-4 border-t border-gray-100">
                    <div className="bg-gray-50 rounded-2xl p-2 flex items-center gap-3 border border-gray-200/50">
                        <div className="w-10 h-10 rounded-xl bg-white flex items-center justify-center text-gray-700 font-bold border border-gray-200 shadow-sm shrink-0">
                            {user?.full_name?.charAt(0) || user?.email?.charAt(0).toUpperCase() || <User className="w-5 h-5" />}
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-semibold text-gray-900 truncate">
                                {user?.full_name || 'Guest User'}
                            </p>
                            <p className="text-xs text-gray-500 truncate">
                                {user?.email || 'Not logged in'}
                            </p>
                        </div>
                        <button
                            onClick={handleLogout}
                            className="w-10 h-10 rounded-xl flex items-center justify-center text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                            title="Logout"
                        >
                            <LogOut className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </motion.aside>

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
                {/* Top Header */}
                <header className="h-20 bg-white/80 backdrop-blur-xl border-b border-gray-200/50 flex items-center justify-between px-6 lg:px-10 z-30 sticky top-0">
                    <div className="flex items-center gap-4">
                        <button
                            className="lg:hidden p-2 -ml-2 text-gray-500 hover:text-gray-900 rounded-lg hover:bg-gray-100"
                            onClick={() => setIsSidebarOpen(true)}
                        >
                            <Menu className="w-5 h-5" />
                        </button>

                        {/* Page Title based on route */}
                        <div>
                            <h1 className="text-xl font-bold text-gray-900">
                                {location.pathname === '/' && 'Overview'}
                                {location.pathname === '/chat' && 'AI Assistant'}
                                {location.pathname === '/history' && 'Conversation History'}
                                {location.pathname === '/analytics' && 'System Analytics'}
                                {location.pathname === '/live-metrics' && 'Live Metrics'}
                                {location.pathname === '/profile' && 'User Settings'}
                            </h1>
                            <p className="text-xs text-gray-500 mt-0.5">
                                {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <div className="hidden md:flex relative group">
                            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                            <input
                                type="text"
                                placeholder="Search queries..."
                                className="w-64 pl-9 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all font-medium"
                            />
                            <div className="absolute inset-y-0 right-2 flex items-center">
                                <span className="text-[10px] font-bold text-gray-400 border border-gray-200 rounded px-1.5 py-0.5 max-h-5 flex items-center bg-white shadow-sm">⌘K</span>
                            </div>
                        </div>

                        <button className="relative p-2 text-gray-400 hover:text-gray-600 bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors">
                            <Bell className="w-5 h-5" />
                            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-red-500 border-2 border-white"></span>
                        </button>

                        <button
                            onClick={() => navigate('/profile')}
                            className="hidden sm:flex items-center gap-2 p-1 pl-3 pr-1 bg-white border border-gray-200 rounded-full hover:border-gray-300 transition-colors shadow-sm"
                        >
                            <span className="text-sm font-semibold text-gray-700">Profile</span>
                            <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center border border-gray-200">
                                <User className="w-4 h-4 text-gray-500" />
                            </div>
                        </button>
                    </div>
                </header>

                {/* Page Content */}
                <main className={`flex-1 relative ${location.pathname === '/chat' ? 'overflow-hidden flex flex-col' : 'overflow-y-auto scrollbar-thin scrollbar-thumb-gray-200 scrollbar-track-transparent'}`}>
                    {children}
                </main>
            </div>
        </div>
    );
};
