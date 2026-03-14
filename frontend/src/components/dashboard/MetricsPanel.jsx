import React from 'react';
import {
    LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';
import { Leaf, Zap, Activity, Server, Timer, Trees, Database } from 'lucide-react';
import { Card } from '../ui/Card';

const GaugeChart = ({ value, max = 500 }) => {
    const data = [
        { name: 'Value', value: value },
        { name: 'Remaining', value: max - value }
    ];

    return (
        <div className="relative h-32 w-full flex items-end justify-center pb-6">
            <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                    <Pie
                        dataKey="value"
                        startAngle={180}
                        endAngle={0}
                        data={data}
                        cx="50%"
                        cy="70%"
                        innerRadius="60%"
                        outerRadius="80%"
                        fill="#f3f4f6"
                        stroke="none"
                    >
                        <Cell fill="#16a34a" /> {/* emerald-600 */}
                        <Cell fill="#e5e7eb" /> {/* gray-200 */}
                    </Pie>
                </PieChart>
            </ResponsiveContainer>
            <div className="absolute bottom-2 text-center z-10">
                <div className="text-xl font-bold text-gray-900 leading-none">{value}</div>
                <div className="text-[9px] uppercase text-gray-400 mt-1 font-semibold">gCO2/kWh</div>
            </div>
        </div>
    );
};

export const MetricsPanel = ({ metrics }) => {
    if (!metrics) return (
        <div className="h-full flex items-center justify-center text-gray-400 animate-pulse bg-gray-50/30">
            <div className="text-center">
                <Activity className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="font-medium text-sm">Connecting to Live Metrics...</p>
            </div>
        </div>
    );

    return (
        <div className="h-full overflow-y-auto p-8 space-y-6 bg-gray-50/50">
            <div className="flex items-center justify-between mb-2">
                <h2 className="text-xs font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                    <Activity className="w-4 h-4 text-emerald-600" />
                    Live Dashboard
                </h2>
                <div className="flex items-center gap-2 px-2.5 py-1 bg-white border border-emerald-200 rounded-full text-[10px] text-emerald-700 shadow-sm">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    <span className="font-semibold">SYSTEM OPTIMAL</span>
                </div>
            </div>

            {/* Top Row: Grid Intensity & Token Efficiency */}
            <div className="grid grid-cols-2 gap-5">
                <Card className="bg-white border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex items-center gap-2 mb-2">
                        <Zap className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                        <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Grid Intensity</span>
                    </div>
                    <GaugeChart value={metrics.carbon_intensity || 150} />
                </Card>

                <Card className="bg-white border-gray-200 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between">
                    <div>
                        <div className="flex items-center gap-2 mb-4">
                            <Database className="w-4 h-4 text-teal-500" />
                            <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Token Efficiency</span>
                        </div>
                        <div className="space-y-3">
                            <div className="flex justify-between items-end">
                                <span className="text-3xl font-bold text-gray-900 tracking-tight">
                                    {metrics.tokens_saved_percent || 0}%
                                </span>
                                <span className="text-xs font-medium text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-100">
                                    Savings
                                </span>
                            </div>
                            <div className="h-2.5 w-full bg-gray-100 rounded-full overflow-hidden border border-gray-100">
                                <div
                                    className="h-full bg-teal-500 rounded-full shadow-[0_0_10px_rgba(59,130,246,0.3)] transition-all duration-500"
                                    style={{ width: `${metrics.tokens_saved_percent || 0}%` }}
                                >
                                    <div className="h-full w-full bg-white/20 animate-pulse" />
                                </div>
                            </div>
                            <div className="text-[10px] text-gray-400 font-medium">
                                {metrics.tokens_saved?.toLocaleString()} tokens saved via optimization
                            </div>
                        </div>
                    </div>
                </Card>
            </div>

            {/* Carbon & Energy Impact */}
            <div className="p-6 rounded-2xl bg-white border border-gray-200 shadow-sm relative overflow-hidden group hover:shadow-md transition-all">
                <div className="absolute right-0 top-0 p-4 opacity-[0.03] group-hover:opacity-[0.05] transition-opacity">
                    <Trees className="w-32 h-32 text-emerald-900" />
                </div>
                <div className="relative z-10">
                    <div className="flex items-center gap-2 mb-6">
                        <div className="p-1.5 bg-emerald-50 rounded-lg">
                            <Leaf className="w-5 h-5 text-emerald-600" />
                        </div>
                        <span className="text-sm font-bold text-gray-800 tracking-tight">Environmental Impact</span>
                    </div>

                    <div className="grid grid-cols-2 gap-8 mb-6">
                        <div>
                            <div className="text-4xl font-bold text-gray-900 tracking-tight">{metrics.carbon_saved_today}g</div>
                            <div className="text-xs text-gray-500 mt-1 font-medium">CO2 Saved Today</div>
                        </div>
                        <div className="border-l border-gray-100 pl-8">
                            <div className="text-4xl font-bold text-gray-900 tracking-tight">
                                {metrics.energy_saved_kwh || 0}
                            </div>
                            <div className="text-xs text-gray-500 mt-1 font-medium">kWh Energy Saved</div>
                        </div>
                    </div>

                    {/* Energy Comparison Bar */}
                    <div className="space-y-3 pt-4 border-t border-gray-100">
                        <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Energy Consumption Comparison</div>

                        {/* Our Model */}
                        <div className="space-y-1">
                            <div className="flex justify-between text-xs">
                                <span className="font-medium text-gray-700">Our Adaptive Model</span>
                                <span className="font-mono text-emerald-600">{metrics.energy_used_kwh || 0} kWh</span>
                            </div>
                            <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-emerald-500 rounded-full"
                                    style={{ width: `${Math.min(100, (metrics.energy_used_kwh / (metrics.energy_baseline_kwh || 1)) * 100)}%` }}
                                />
                            </div>
                        </div>

                        {/* Standard Model */}
                        <div className="space-y-1">
                            <div className="flex justify-between text-xs">
                                <span className="font-medium text-gray-500">Standard Model (Baseline)</span>
                                <span className="font-mono text-gray-400">{metrics.energy_baseline_kwh || 0.001} kWh</span>
                            </div>
                            <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
                                <div className="h-full bg-gray-400 rounded-full w-full" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Response Time Chart */}
            <Card className="bg-white border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-2">
                        <Timer className="w-4 h-4 text-violet-500" />
                        <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Latency Trend</span>
                    </div>
                    <span className="text-xs font-mono font-medium text-gray-400 bg-gray-50 px-2 py-1 rounded border border-gray-100">
                        {metrics.response_times?.length > 0
                            ? `avg: ${Math.round(metrics.response_times.reduce((a, b) => a + b.latency, 0) / metrics.response_times.length)}ms`
                            : 'avg: --'}
                    </span>
                </div>
                <div className="h-40 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={metrics.response_times || []}>
                            <defs>
                                <linearGradient id="colorLatency" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.2} />
                                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <Area type="monotone" dataKey="latency" stroke="#8b5cf6" strokeWidth={2} fillOpacity={1} fill="url(#colorLatency)" />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e5e7eb', fontSize: '12px', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                itemStyle={{ color: '#6d28d9', fontWeight: 600 }}
                                cursor={{ stroke: '#e5e7eb' }}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </Card>

            {/* Active Models */}
            <Card className="bg-white border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center gap-2 mb-5">
                    <Server className="w-4 h-4 text-orange-500" />
                    <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Model Distribution</span>
                </div>
                <div className="space-y-4">
                    {metrics.active_model_dist && metrics.active_model_dist.length > 0 ? (
                        metrics.active_model_dist.map((model, i) => (
                            <div key={i} className="flex items-center justify-between text-xs group">
                                <span className="text-gray-600 font-medium group-hover:text-gray-900 transition-colors">{model.name}</span>
                                <div className="flex items-center gap-3 w-1/2 justify-end">
                                    <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden border border-gray-100">
                                        <div
                                            className={`h-full ${i === 0 ? 'bg-teal-500' : i === 1 ? 'bg-purple-500' : 'bg-orange-500'} rounded-full opacity-80 group-hover:opacity-100 transition-opacity`}
                                            style={{ width: `${model.value}%` }}
                                        />
                                    </div>
                                    <span className="w-8 text-right text-gray-500 font-mono">{model.value}%</span>
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="text-center text-xs text-gray-400 py-4">No data yet</div>
                    )}
                </div>
            </Card>
        </div>
    );
};
