import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area, CartesianGrid } from 'recharts';
import { Download, Calendar, ArrowUpRight, ArrowDownRight, Leaf, Zap, Clock, Coins, RefreshCw } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { carbonSenseAPI } from '../services/api';

const efficiencyData = [
    { time: '00:00', value: 85 },
    { time: '04:00', value: 88 },
    { time: '08:00', value: 72 },
    { time: '12:00', value: 65 },
    { time: '16:00', value: 78 },
    { time: '20:00', value: 82 },
    { time: '23:59', value: 86 },
];

const StatCard = ({ title, value, change, icon: Icon, trend = 'up' }) => (
    <Card className="hover:shadow-md transition-shadow">
        <div className="flex items-start justify-between mb-4">
            <div className="p-2 bg-emerald-50 rounded-lg">
                <Icon className="w-5 h-5 text-emerald-600" />
            </div>
            <div className={`flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-full ${trend === 'up' ? 'bg-emerald-100 text-emerald-700' : 'bg-red-50 text-red-600'
                }`}>
                {trend === 'up' ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                {change}
            </div>
        </div>
        <div className="text-2xl font-bold text-gray-900 mb-1">{value}</div>
        <div className="text-xs text-gray-500 font-medium uppercase tracking-wider">{title}</div>
    </Card>
);

export const Analytics = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [analyticsData, metricsData] = await Promise.all([
                    carbonSenseAPI.getAnalytics(),
                    carbonSenseAPI.getMetrics()
                ]);
                setData({ ...analyticsData, ...metricsData });
            } catch (error) {
                console.error("Failed to fetch analytics:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) {
        return (
            <div className="flex h-full items-center justify-center">
                <RefreshCw className="w-8 h-8 text-carbon-500 animate-spin opacity-50" />
            </div>
        );
    }

    // Fallback if data is missing or error
    const metrics = data; // Alias for code clarity since we merged
    const weeklyData = data?.weekly_data || [];
    const totalEmissions = data?.total_emissions || 0;
    const totalRequests = data?.total_requests || 0;

    return (
        <div className="h-full overflow-y-auto p-8 bg-gray-50 font-sans pb-20">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Analytics Overview</h1>
                    <p className="text-gray-500 text-sm mt-1">Track your carbon footprint and operational efficiency.</p>
                </div>
                <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2 bg-white px-3 py-2 rounded-lg border border-gray-200 text-gray-600 text-sm shadow-sm">
                        <Calendar className="w-4 h-4" />
                        <span>Last 7 Days</span>
                    </div>
                    <Button variant="outline" size="sm" className="bg-white border-gray-200 text-gray-700 hover:bg-gray-50 hover:text-gray-900 shadow-sm">
                        <Download className="w-4 h-4 mr-2" />
                        Export Report
                    </Button>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <StatCard
                    title="Total Emissions"
                    value={`${totalEmissions}g`}
                    change="Live"
                    icon={Leaf}
                    trend="up" // Tracking up as we use more
                />
                <StatCard
                    title="Avg. Intensity"
                    value="142 g/kWh"
                    change="5% Stable"
                    icon={Zap}
                />
                <StatCard
                    title="Requests Served"
                    value={totalRequests}
                    change="Growing"
                    icon={Clock}
                />
                <StatCard
                    title="Est. Savings"
                    value="$--"
                    change="Calculated daily"
                    icon={Coins}
                />
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <Card className="lg:col-span-2">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="font-bold text-gray-800">Emissions vs Requests</h3>
                        {/* ... legend ... */}
                    </div>
                    {/* ... chart ... */}
                    <div className="h-80 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={weeklyData} barGap={0}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                                <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: '#6b7280', fontSize: 12 }} dy={10} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#6b7280', fontSize: 12 }} />
                                <Tooltip
                                    cursor={{ fill: '#f9fafb' }}
                                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                />
                                <Bar dataKey="emissions" fill="#22c55e" radius={[4, 4, 0, 0]} barSize={20} />
                                <Bar dataKey="requests" fill="#e5e7eb" radius={[4, 4, 0, 0]} barSize={20} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </Card>

                <Card>
                    <div className="mb-6">
                        <h3 className="font-bold text-gray-800">Carbon Efficiency Score</h3>
                        <p className="text-xs text-gray-500 mt-1">Live Logic Performance</p>
                    </div>
                    {/* Simplified Guage/Score instead of dummy area chart for now */}
                    <div className="flex flex-col items-center justify-center h-48 mb-4">
                        <div className="relative w-32 h-32 flex items-center justify-center">
                            <div className="absolute inset-0 rounded-full border-8 border-gray-100"></div>
                            <div className="absolute inset-0 rounded-full border-8 border-emerald-500 border-t-transparent animate-spin" style={{ animationDuration: '3s' }}></div>
                            <div className="absolute inset-0 flex items-center justify-center flex-col">
                                <span className="text-3xl font-bold text-gray-900">{metrics?.efficiency_score || 0}</span>
                                <span className="text-xs text-gray-500">SCORE</span>
                            </div>
                        </div>
                    </div>

                    <div className="bg-emerald-50 rounded-lg p-4 border border-emerald-100">
                        <div className="flex justify-between items-center mb-2">
                            <span className="text-xs text-emerald-800 font-semibold">Current Score</span>
                            <span className="text-xl font-bold text-emerald-600">{metrics?.efficiency_score || 0}/100</span>
                        </div>
                        <div className="w-full bg-white rounded-full h-2">
                            <div className="bg-emerald-500 h-2 rounded-full" style={{ width: `${metrics?.efficiency_score || 0}%` }}></div>
                        </div>
                        <p className="text-[10px] text-emerald-700 mt-2">
                            Efficiency calculated based on energy saved vs baseline.
                        </p>
                    </div>
                </Card>
            </div>

            <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                    <h3 className="font-bold text-gray-800 mb-4">Top Carbon Saving Actions</h3>
                    <div className="space-y-4">
                        {(metrics?.top_actions || []).length > 0 ? (
                            metrics.top_actions.map((item, i) => (
                                <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-white border border-transparent hover:border-gray-200 transition-all cursor-default">
                                    <div className="flex items-center gap-3">
                                        <div className="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600 font-bold text-xs">{i + 1}</div>
                                        <div>
                                            <div className="text-sm font-semibold text-gray-900">{item.action}</div>
                                            <div className="text-xs text-gray-500">{item.impact} Impact</div>
                                        </div>
                                    </div>
                                    <div className="text-sm font-bold text-emerald-600">{item.savings}</div>
                                </div>
                            ))
                        ) : (
                            <div className="text-center py-8 text-gray-400 text-sm">No data yet. Run queries to see savings!</div>
                        )}
                    </div>
                </Card>
                <Card>
                    <h3 className="font-bold text-gray-800 mb-4">Regional & Provider Breakdown</h3>
                    <div className="space-y-4">
                        {(metrics?.regional_breakdown || []).length > 0 ? (
                            metrics.regional_breakdown.map((item, i) => (
                                <div key={i} className="flex flex-col gap-1">
                                    <div className="flex justify-between text-xs mb-1">
                                        <span className="font-medium text-gray-700">{item.region}</span>
                                        <span className={`font-semibold ${item.intensity === 'Low' ? 'text-emerald-500' : item.intensity === 'Med' ? 'text-yellow-500' : 'text-red-500'}`}>{item.intensity} Intensity</span>
                                    </div>
                                    <div className="w-full bg-gray-100 rounded-full h-2">
                                        <div className="bg-gray-800 h-2 rounded-full" style={{ width: `${item.load}%` }}></div>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="text-center py-8 text-gray-400 text-sm">No regional data available yet.</div>
                        )}
                        <div className="mt-4 pt-4 border-t border-gray-100">
                            <div className="text-xs text-gray-400 text-center">Live Data from Backend</div>
                        </div>
                    </div>
                </Card>
            </div>
        </div>
    );
};
