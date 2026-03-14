import React, { useEffect, useState } from 'react';
import { NavLink, Link, useNavigate } from 'react-router-dom';
import { Leaf, User, Settings, BarChart3, Github, LogOut } from 'lucide-react';
import { authService } from '../../services/auth';

export const Header = () => {
    const [user, setUser] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const checkUser = async () => {
            const userData = await authService.getCurrentUser();
            setUser(userData);
        };
        checkUser();
    }, []);

    const handleLogout = () => {
        authService.logout();
        setUser(null);
        navigate('/auth');
    };

    return (
        <header className="h-16 border-b border-gray-200 bg-white/80 backdrop-blur-xl flex items-center justify-between px-6 sticky top-0 z-50 shadow-sm">
            <div className="flex items-center gap-3">
                <Link to="/" className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center shadow-lg shadow-emerald-500/20 ring-1 ring-black/5">
                        <Leaf className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <span className="font-bold text-lg tracking-tight text-gray-900 block leading-tight">
                            CarbonSense AI
                        </span>
                        <span className="text-[10px] uppercase tracking-wider font-semibold text-emerald-600">Enterprise Edition</span>
                    </div>
                </Link>
            </div>

            <nav className="flex items-center gap-2 p-1 bg-gray-100/50 rounded-xl border border-gray-200/50">
                <NavLink
                    to="/analytics"
                    className={({ isActive }) =>
                        `flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${isActive
                            ? 'bg-white text-emerald-700 shadow-sm ring-1 ring-black/5'
                            : 'text-gray-500 hover:text-gray-900 hover:bg-white/50'
                        }`
                    }
                >
                    <BarChart3 className="w-4 h-4" />
                    <span className="hidden sm:inline">Analytics</span>
                </NavLink>

                <div className="w-px h-6 bg-gray-200 mx-1" />

                {user ? (
                    <>
                        <Link to="/profile" className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-gray-700 hover:bg-white/50 transition-all">
                            <div className="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-700 font-bold border border-emerald-200">
                                {user.full_name?.charAt(0) || user.email.charAt(0).toUpperCase()}
                            </div>
                            <span className="hidden md:inline">{user.full_name || 'User'}</span>
                        </Link>
                        <button
                            onClick={handleLogout}
                            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-red-500 hover:bg-red-50 transition-all duration-200"
                        >
                            <LogOut className="w-4 h-4" />
                            <span className="hidden sm:inline">Logout</span>
                        </button>
                    </>
                ) : (
                    <Link to="/auth" className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-gray-500 hover:text-gray-900 hover:bg-white/50 transition-all duration-200">
                        Sign In
                    </Link>
                )}

                <a
                    href="https://github.com/yourusername/carbonsense"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-gray-500 hover:text-gray-900 hover:bg-white/50 transition-all duration-200"
                >
                    <Github className="w-4 h-4" />
                    <span className="hidden sm:inline">GitHub</span>
                </a>
            </nav>
        </header>
    );
};
