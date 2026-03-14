
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { User, Mail, Shield, Calendar, Save, Trash2, AlertCircle } from 'lucide-react';
import { authService } from '../services/auth';

export function Profile() {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [updating, setUpdating] = useState(false);
    const [message, setMessage] = useState({ type: '', text: '' });
    const [formData, setFormData] = useState({
        full_name: '',
        password: ''
    });

    useEffect(() => {
        const fetchUser = async () => {
            const data = await authService.getCurrentUser();
            if (data) {
                setUser(data);
                setFormData({ full_name: data.full_name || '', password: '' });
            }
            setLoading(false);
        };
        fetchUser();
    }, []);

    const handleUpdate = async (e) => {
        e.preventDefault();
        setUpdating(true);
        setMessage({ type: '', text: '' });
        try {
            const updatedUser = await authService.updateProfile(
                formData.full_name,
                formData.password || undefined
            );
            setUser(updatedUser);
            setMessage({ type: 'success', text: 'Profile updated successfully!' });
        } catch (error) {
            setMessage({ type: 'error', text: error.message });
        } finally {
            setUpdating(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center p-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
            </div>
        );
    }

    if (!user) {
        return (
            <div className="max-w-2xl mx-auto p-8 text-center bg-white rounded-2xl shadow-sm border border-gray-100 mt-10">
                <AlertCircle className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-gray-900">Not Authenticated</h2>
                <p className="text-gray-500 mt-2">Please sign in to view your profile data.</p>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto p-6 space-y-8">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                {/* Header Section */}
                <div className="bg-gradient-to-r from-gray-900 to-emerald-900 p-8 text-white relative h-48 flex items-end">
                    <div className="absolute top-4 right-4 bg-white/10 backdrop-blur-md px-3 py-1 rounded-full text-xs border border-white/20">
                        Level: Environmental Pilot
                    </div>
                    <div className="flex items-center gap-6 relative z-10 translate-y-6">
                        <div className="w-24 h-24 rounded-2xl bg-white flex items-center justify-center text-gray-900 text-4xl font-bold shadow-xl border-4 border-white">
                            {user.full_name?.charAt(0) || user.email.charAt(0).toUpperCase()}
                        </div>
                        <div className="space-y-1">
                            <h1 className="text-3xl font-bold">{user.full_name || 'Anonymous User'}</h1>
                            <p className="text-gray-300 flex items-center gap-2">
                                <Mail className="w-4 h-4" /> {user.email}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Content Section */}
                <div className="p-8 pt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
                    {/* Left: Account Stats */}
                    <div className="space-y-4">
                        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Account Information</h3>
                        <div className="space-y-3">
                            <div className="flex items-center gap-3 text-gray-600">
                                <Shield className="w-5 h-5 text-emerald-500" />
                                <div>
                                    <p className="text-xs text-gray-400">Account Type</p>
                                    <p className="text-sm font-medium">{user.is_superuser ? 'Administrator' : 'Standard User'}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-3 text-gray-600">
                                <Calendar className="w-5 h-5 text-emerald-500" />
                                <div>
                                    <p className="text-xs text-gray-400">Joined On</p>
                                    <p className="text-sm font-medium">{new Date(user.created_at).toLocaleDateString()}</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Right: Profile Edit Form */}
                    <div className="md:col-span-2 space-y-6">
                        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Update Profile</h3>

                        {message.text && (
                            <div className={`p-4 rounded-xl text-sm ${message.type === 'success' ? 'bg-emerald-50 text-emerald-700 border border-emerald-100' : 'bg-red-50 text-red-700 border border-red-100'}`}>
                                {message.text}
                            </div>
                        )}

                        <form onSubmit={handleUpdate} className="space-y-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-700">Full Name</label>
                                <input
                                    type="text"
                                    value={formData.full_name}
                                    onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                                    className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-all"
                                    placeholder="Enter your full name"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-700">New Password (leave blank to keep current)</label>
                                <input
                                    type="password"
                                    value={formData.password}
                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                    className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-all"
                                    placeholder="••••••••"
                                />
                            </div>

                            <div className="pt-4 flex gap-4">
                                <button
                                    type="submit"
                                    disabled={updating}
                                    className="flex items-center gap-2 bg-gray-900 text-white px-6 py-2 rounded-xl font-medium hover:bg-black transition-all disabled:opacity-50"
                                >
                                    <Save className="w-4 h-4" />
                                    {updating ? 'Saving...' : 'Save Changes'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>

            {/* Danger Zone */}
            <div className="bg-red-50 border border-red-100 rounded-2xl p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="space-y-1">
                    <h3 className="text-lg font-semibold text-red-900">Danger Zone</h3>
                    <p className="text-sm text-red-700">Deleting your account is permanent and cannot be undone.</p>
                </div>
                <button
                    onClick={async () => {
                        if (window.confirm('Are you sure you want to delete your account?')) {
                            await authService.deleteAccount();
                            window.location.href = '/auth';
                        }
                    }}
                    className="bg-red-600 text-white px-6 py-2 rounded-xl font-medium hover:bg-red-700 transition-all flex items-center gap-2"
                >
                    <Trash2 className="w-4 h-4" />
                    Delete Account
                </button>
            </div>
        </div>
    );
}
