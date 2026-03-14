import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, Lock, User, ArrowLeft, Github, Chrome, Leaf, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { authService } from '../services/auth';

export function Auth() {
    const [isLogin, setIsLogin] = useState(true);
    const navigate = useNavigate();
    const location = useLocation();
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        fullName: ''
    });

    const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

    useEffect(() => {
        if (authService.isAuthenticated()) {
            navigate(location.state?.from?.pathname || '/chat', { replace: true });
        }
    }, [navigate, location]);

    useEffect(() => {
        const handleMouseMove = (e) => {
            setMousePosition({
                x: e.clientX,
                y: e.clientY
            });
        };
        window.addEventListener('mousemove', handleMouseMove);
        return () => window.removeEventListener('mousemove', handleMouseMove);
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');
        setSuccess('');

        try {
            if (isLogin) {
                await authService.login(formData.email, formData.password);
            } else {
                await authService.register(formData.email, formData.password, formData.fullName);
                setSuccess('Account created successfully! Logging you in...');
                await authService.login(formData.email, formData.password);
            }
            navigate(location.state?.from?.pathname || '/chat', { replace: true });
        } catch (err) {
            setError(err.message || 'An unexpected error occurred. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#FAFAFA] flex items-center justify-center relative overflow-hidden font-sans selection:bg-emerald-500/20 selection:text-emerald-900">
            {/* Ambient Background Effects */}
            <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
                <div
                    className="absolute w-[800px] h-[800px] rounded-full bg-emerald-400/5 blur-[120px] transition-transform duration-[3s] ease-out -translate-x-1/2 -translate-y-1/2"
                    style={{ left: `${mousePosition.x * 0.5}px`, top: `${mousePosition.y * 0.5}px` }}
                />
                <div className="absolute top-0 right-0 w-[600px] h-[600px] rounded-full bg-teal-400/5 blur-[100px] -translate-y-1/2 translate-x-1/3" />
            </div>

            <Link to="/" className="absolute top-8 left-8 z-50 text-gray-500 hover:text-gray-900 transition-colors flex items-center gap-2 group">
                <span className="w-8 h-8 rounded-full bg-white shadow-sm flex items-center justify-center border border-gray-200 group-hover:bg-gray-50 transition-colors">
                    <ArrowLeft className="w-4 h-4" />
                </span>
                <span className="text-sm font-medium tracking-wide">Back to Home</span>
            </Link>

            <div className="w-full max-w-[1100px] mx-auto z-10 flex flex-col lg:flex-row shadow-[0_8px_30px_rgb(0,0,0,0.04)] rounded-3xl overflow-hidden border border-gray-200 bg-white m-6">

                {/* Visual Left Panel */}
                <div className="hidden lg:flex lg:w-5/12 relative flex-col justify-between p-12 overflow-hidden border-r border-gray-100 bg-gradient-to-br from-emerald-50/50 to-teal-50/50">
                    <div className="relative z-20">
                        <motion.div
                            initial={{ opacity: 0, y: -20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6 }}
                            className="flex items-center gap-3 mb-16"
                        >
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/20 border border-emerald-500/20">
                                <Leaf className="w-5 h-5 text-white" />
                            </div>
                            <span className="text-xl font-bold tracking-tight text-gray-900">CarbonSense AI</span>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.6, delay: 0.1 }}
                        >
                            <h2 className="text-4xl font-bold text-gray-900 leading-[1.15] mb-6 tracking-tight">
                                Code <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-500 to-teal-500">Smarter.</span><br />
                                Save the Planet.
                            </h2>
                            <p className="text-gray-500 text-lg leading-relaxed max-w-sm mb-12">
                                Join the community of forward-thinking developers building the future of sustainable AI optimization.
                            </p>
                        </motion.div>
                    </div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.2 }}
                        className="relative z-20"
                    >
                        <div className="grid grid-cols-2 gap-4">
                            <div className="p-5 rounded-2xl bg-white border border-gray-100 shadow-sm">
                                <div className="text-3xl font-bold text-gray-900 tracking-tight mb-1 text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-teal-600">45%</div>
                                <div className="text-sm text-gray-500 font-medium">Carbon Reduction</div>
                            </div>
                            <div className="p-5 rounded-2xl bg-white border border-gray-100 shadow-sm">
                                <div className="text-3xl font-bold text-gray-900 tracking-tight mb-1 text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-teal-600">10k+</div>
                                <div className="text-sm text-gray-500 font-medium">Queries Optimized</div>
                            </div>
                        </div>
                    </motion.div>
                </div>

                {/* Form Right Panel */}
                <div className="w-full lg:w-7/12 flex items-center justify-center p-8 sm:p-16 relative bg-white">
                    <div className="w-full max-w-sm relative z-20">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5 }}
                        >
                            <h3 className="text-3xl font-bold text-gray-900 tracking-tight mb-2">
                                {isLogin ? 'Welcome back' : 'Create account'}
                            </h3>
                            <p className="text-gray-500 font-medium mb-8 text-sm">
                                {isLogin ? 'Enter your credentials to access your dashboard.' : 'Start computing sustainably today.'}
                            </p>

                            <div className="flex bg-gray-50 p-1 rounded-xl border border-gray-200 mb-8 relative">
                                <div
                                    className="absolute left-1 top-1 bottom-1 w-[calc(50%-4px)] bg-white rounded-lg shadow-sm transition-transform duration-300 ease-out border border-gray-200/50"
                                    style={{ transform: `translateX(${isLogin ? '0' : '100%'})` }}
                                />
                                <button
                                    onClick={() => {
                                        setIsLogin(true);
                                        setError('');
                                    }}
                                    className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-colors duration-200 relative z-10 ${isLogin ? 'text-gray-900' : 'text-gray-500 hover:text-gray-700'}`}
                                >
                                    Login
                                </button>
                                <button
                                    onClick={() => {
                                        setIsLogin(false);
                                        setError('');
                                    }}
                                    className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-colors duration-200 relative z-10 ${!isLogin ? 'text-gray-900' : 'text-gray-500 hover:text-gray-700'}`}
                                >
                                    Sign Up
                                </button>
                            </div>

                            <AnimatePresence mode="wait">
                                {error && (
                                    <motion.div
                                        initial={{ opacity: 0, height: 0, marginBottom: 0 }}
                                        animate={{ opacity: 1, height: 'auto', marginBottom: 24 }}
                                        exit={{ opacity: 0, height: 0, marginBottom: 0 }}
                                        className="bg-red-50 border border-red-100 rounded-xl p-4 flex gap-3 text-red-700 text-sm font-medium items-start"
                                    >
                                        <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                                        <p>{error}</p>
                                    </motion.div>
                                )}
                                {success && (
                                    <motion.div
                                        initial={{ opacity: 0, height: 0, marginBottom: 0 }}
                                        animate={{ opacity: 1, height: 'auto', marginBottom: 24 }}
                                        exit={{ opacity: 0, height: 0, marginBottom: 0 }}
                                        className="bg-emerald-50 border border-emerald-100 rounded-xl p-4 flex gap-3 text-emerald-700 text-sm font-medium items-start"
                                    >
                                        <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
                                        <p>{success}</p>
                                    </motion.div>
                                )}
                            </AnimatePresence>

                            <form onSubmit={handleSubmit} className="space-y-4">
                                <AnimatePresence mode="popLayout">
                                    {!isLogin && (
                                        <motion.div
                                            initial={{ opacity: 0, height: 0, filter: 'blur(4px)' }}
                                            animate={{ opacity: 1, height: 'auto', filter: 'blur(0px)' }}
                                            exit={{ opacity: 0, height: 0, filter: 'blur(4px)' }}
                                            transition={{ duration: 0.3, ease: 'easeInOut' }}
                                            className="space-y-1.5 overflow-hidden"
                                        >
                                            <label className="block text-sm font-medium text-gray-700 mb-1.5 ml-1">Full Name</label>
                                            <div className="relative group/input">
                                                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                                                    <User className="h-5 w-5 text-gray-400 group-focus-within/input:text-emerald-500 transition-colors" />
                                                </div>
                                                <input
                                                    type="text"
                                                    required={!isLogin}
                                                    value={formData.fullName}
                                                    onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                                                    className="block w-full pl-10 pr-4 py-3 bg-white border border-gray-300 rounded-xl focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500 text-gray-900 placeholder:text-gray-400 transition-all font-medium text-sm outline-none"
                                                    placeholder="John Doe"
                                                />
                                            </div>
                                        </motion.div>
                                    )}
                                </AnimatePresence>

                                <div className="space-y-1.5 relative z-10">
                                    <label className="block text-sm font-medium text-gray-700 mb-1.5 ml-1">Email Address</label>
                                    <div className="relative group/input">
                                        <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                                            <Mail className="h-5 w-5 text-gray-400 group-focus-within/input:text-emerald-500 transition-colors" />
                                        </div>
                                        <input
                                            type="email"
                                            required
                                            value={formData.email}
                                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                            className="block w-full pl-10 pr-4 py-3 bg-white border border-gray-300 rounded-xl focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500 text-gray-900 placeholder:text-gray-400 transition-all font-medium text-sm outline-none"
                                            placeholder="you@example.com"
                                        />
                                    </div>
                                </div>

                                <div className="space-y-1.5 relative z-10">
                                    <div className="flex items-center justify-between mb-1.5 ml-1">
                                        <label className="block text-sm font-medium text-gray-700">Password</label>
                                        {isLogin && (
                                            <a href="#" className="text-xs font-semibold text-emerald-600 hover:text-emerald-500 transition-colors mr-1">
                                                Forgot password?
                                            </a>
                                        )}
                                    </div>
                                    <div className="relative group/input">
                                        <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                                            <Lock className="h-5 w-5 text-gray-400 group-focus-within/input:text-emerald-500 transition-colors" />
                                        </div>
                                        <input
                                            type="password"
                                            required
                                            value={formData.password}
                                            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                            className="block w-full pl-10 pr-4 py-3 bg-white border border-gray-300 rounded-xl focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500 text-gray-900 placeholder:text-gray-400 transition-all font-medium text-sm tracking-widest outline-none"
                                            placeholder="••••••••"
                                        />
                                    </div>
                                </div>

                                <button
                                    type="submit"
                                    disabled={isLoading}
                                    className="w-full flex justify-center items-center py-3 px-4 mt-6 border border-transparent rounded-xl shadow-sm text-sm font-bold text-white bg-gray-900 hover:bg-emerald-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-all disabled:opacity-70 disabled:cursor-not-allowed group/btn hover:shadow-md"
                                >
                                    {isLoading ? (
                                        <RefreshCw className="w-5 h-5 text-white animate-spin mr-2" />
                                    ) : null}
                                    {isLogin ? 'Sign in to Console' : 'Create Account'}
                                </button>
                            </form>

                            <div className="mt-8 mb-6 relative">
                                <div className="absolute inset-0 flex items-center">
                                    <div className="w-full border-t border-gray-200"></div>
                                </div>
                                <div className="relative flex justify-center text-xs">
                                    <span className="px-3 bg-white text-gray-500 font-medium">Or continue with</span>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-3">
                                <button className="flex justify-center items-center px-4 py-2.5 border border-gray-200 shadow-sm text-sm font-semibold rounded-xl text-gray-600 bg-white hover:bg-gray-50 transition-colors gap-2">
                                    <Chrome className="h-4 w-4 text-gray-500" />
                                    Google
                                </button>
                                <button className="flex justify-center items-center px-4 py-2.5 border border-gray-200 shadow-sm text-sm font-semibold rounded-xl text-gray-600 bg-white hover:bg-gray-50 transition-colors gap-2">
                                    <Github className="h-4 w-4 text-gray-500" />
                                    GitHub
                                </button>
                            </div>

                            <p className="mt-8 text-center text-xs text-gray-500">
                                By signing up, you agree to our <a href="#" className="underline hover:text-gray-700">Terms of Service</a> and <a href="#" className="underline hover:text-gray-700">Privacy Policy</a>.
                            </p>
                        </motion.div>
                    </div>
                </div>
            </div>
        </div>
    );
}

