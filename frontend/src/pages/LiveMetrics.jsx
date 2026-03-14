import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Zap, Database, TrendingDown, Activity, Leaf, Gauge,
    RefreshCw, Cpu, Globe, BarChart2, Wifi, Clock
} from 'lucide-react';
import { carbonSenseAPI } from '../services/api';

// ─────────────────────────────────────────────
// Individual live metric card
// ─────────────────────────────────────────────
const MetricCard = ({ icon: Icon, label, value, sub, color, index, trend }) => {
    const palettes = {
        emerald: {
            card: 'bg-gradient-to-br from-emerald-950/80 to-emerald-900/40',
            border: 'border-emerald-700/30',
            icon: 'bg-emerald-800/60 text-emerald-300',
            val: 'text-emerald-300',
            pulse: 'bg-emerald-400',
            glow: 'shadow-emerald-900/40'
        },
        amber: {
            card: 'bg-gradient-to-br from-amber-950/80 to-amber-900/40',
            border: 'border-amber-700/30',
            icon: 'bg-amber-800/60 text-amber-300',
            val: 'text-amber-300',
            pulse: 'bg-amber-400',
            glow: 'shadow-amber-900/40'
        },
        rose: {
            card: 'bg-gradient-to-br from-rose-950/80 to-rose-900/40',
            border: 'border-rose-700/30',
            icon: 'bg-rose-800/60 text-rose-300',
            val: 'text-rose-300',
            pulse: 'bg-rose-400',
            glow: 'shadow-rose-900/40'
        },
        sky: {
            card: 'bg-gradient-to-br from-sky-950/80 to-sky-900/40',
            border: 'border-sky-700/30',
            icon: 'bg-sky-800/60 text-sky-300',
            val: 'text-sky-300',
            pulse: 'bg-sky-400',
            glow: 'shadow-sky-900/40'
        },
        violet: {
            card: 'bg-gradient-to-br from-violet-950/80 to-violet-900/40',
            border: 'border-violet-700/30',
            icon: 'bg-violet-800/60 text-violet-300',
            val: 'text-violet-300',
            pulse: 'bg-violet-400',
            glow: 'shadow-violet-900/40'
        },
        teal: {
            card: 'bg-gradient-to-br from-teal-950/80 to-teal-900/40',
            border: 'border-teal-700/30',
            icon: 'bg-teal-800/60 text-teal-300',
            val: 'text-teal-300',
            pulse: 'bg-teal-400',
            glow: 'shadow-teal-900/40'
        },
        cyan: {
            card: 'bg-gradient-to-br from-cyan-950/80 to-cyan-900/40',
            border: 'border-cyan-700/30',
            icon: 'bg-cyan-800/60 text-cyan-300',
            val: 'text-cyan-300',
            pulse: 'bg-cyan-400',
            glow: 'shadow-cyan-900/40'
        },
        indigo: {
            card: 'bg-gradient-to-br from-indigo-950/80 to-indigo-900/40',
            border: 'border-indigo-700/30',
            icon: 'bg-indigo-800/60 text-indigo-300',
            val: 'text-indigo-300',
            pulse: 'bg-indigo-400',
            glow: 'shadow-indigo-900/40'
        },
    };

    const p = palettes[color] || palettes.emerald;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.06, duration: 0.4 }}
            className={`${p.card} ${p.border} border rounded-2xl p-5 shadow-lg ${p.glow} relative overflow-hidden group hover:scale-[1.02] transition-transform duration-200`}
        >
            {/* Background glow blob */}
            <div className="absolute -right-6 -bottom-6 w-24 h-24 rounded-full opacity-10 blur-2xl bg-white" />

            {/* Header row */}
            <div className="flex items-start justify-between mb-4">
                <div className={`p-2.5 rounded-xl ${p.icon}`}>
                    <Icon className="w-5 h-5" />
                </div>
                <div className="flex items-center gap-1.5">
                    <div className={`w-2 h-2 rounded-full ${p.pulse} animate-pulse`} />
                    <span className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Live</span>
                </div>
            </div>

            {/* Value */}
            <div className={`text-3xl font-bold ${p.val} mb-1 leading-none`}>{value}</div>

            {/* Label */}
            <div className="text-xs text-gray-400 font-semibold uppercase tracking-wider mb-1">{label}</div>

            {/* Sub text */}
            {sub && <div className="text-[11px] text-gray-600">{sub}</div>}

            {/* Trend indicator */}
            {trend !== undefined && (
                <div className={`absolute top-4 right-12 text-xs font-bold ${trend >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {trend >= 0 ? '↑' : '↓'} {Math.abs(trend).toFixed(1)}%
                </div>
            )}
        </motion.div>
    );
};

// ─────────────────────────────────────────────
// Skeleton loader card
// ─────────────────────────────────────────────
const SkeletonCard = ({ index }) => (
    <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: index * 0.05 }}
        className="bg-white/5 border border-white/5 rounded-2xl p-5 animate-pulse"
    >
        <div className="flex justify-between mb-4">
            <div className="w-10 h-10 rounded-xl bg-white/10" />
            <div className="w-12 h-4 rounded-full bg-white/10" />
        </div>
        <div className="w-24 h-8 rounded-lg bg-white/10 mb-2" />
        <div className="w-32 h-3 rounded bg-white/5 mb-1" />
        <div className="w-20 h-3 rounded bg-white/5" />
    </motion.div>
);

// ─────────────────────────────────────────────
// Main LiveMetrics page
// ─────────────────────────────────────────────
const LiveMetrics = () => {
    const [metrics, setMetrics] = useState(null);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [lastUpdated, setLastUpdated] = useState(null);
    const [countdown, setCountdown] = useState(5);
    const intervalRef = useRef(null);
    const countRef = useRef(null);

    const fetchMetrics = async () => {
        setIsRefreshing(true);
        try {
            const data = await carbonSenseAPI.getMetrics();
            setMetrics(data);
            setLastUpdated(new Date());
            setCountdown(5);
        } catch (e) {
            console.error('LiveMetrics fetch error:', e);
        } finally {
            setIsRefreshing(false);
        }
    };

    useEffect(() => {
        fetchMetrics();
        intervalRef.current = setInterval(fetchMetrics, 5000);

        // countdown ticker
        countRef.current = setInterval(() => {
            setCountdown(prev => (prev <= 1 ? 5 : prev - 1));
        }, 1000);

        return () => {
            clearInterval(intervalRef.current);
            clearInterval(countRef.current);
        };
    }, []);

    // Compute derived values
    const intensity = metrics?.carbon_intensity ?? 0;
    const intensityColor = intensity < 150 ? 'emerald' : intensity < 300 ? 'amber' : 'rose';
    const intensityLabel = intensity < 150 ? 'LOW — Clean energy grid' : intensity < 300 ? 'MODERATE — Mixed sources' : 'HIGH — Heavy carbon load';

    const hitRate = metrics?.cache_hit_rate ?? 0;
    const hitRatePct = (hitRate * 100).toFixed(1);

    const tokensSaved = metrics?.tokens_saved ?? 0;
    const tokensPct = (metrics?.tokens_saved_percent ?? 0).toFixed(1);

    const energySaved = metrics?.energy_saved_kwh ?? 0;
    const energyUsed = metrics?.energy_used_kwh ?? 0;
    const energyBaseline = metrics?.energy_baseline_kwh ?? 0;

    const co2Saved = metrics?.carbon_saved_today ?? 0;
    const effScore = metrics?.efficiency_score ?? 0;
    const effColor = effScore >= 70 ? 'emerald' : effScore >= 40 ? 'amber' : 'rose';

    const metricCards = metrics ? [
        {
            icon: Zap,
            label: 'Carbon Intensity',
            value: `${intensity.toFixed(0)} gCO₂`,
            sub: `${intensityLabel}`,
            color: intensityColor,
        },
        {
            icon: Database,
            label: 'Cache Hit Rate',
            value: `${hitRatePct}%`,
            sub: `Avoiding redundant AI calls`,
            color: 'sky',
        },
        {
            icon: TrendingDown,
            label: 'Tokens Saved',
            value: tokensSaved.toLocaleString(),
            sub: `${tokensPct}% reduction via optimizer`,
            color: 'violet',
        },
        {
            icon: Activity,
            label: 'Energy Saved',
            value: `${energySaved.toFixed(3)} kWh`,
            sub: `Used: ${energyUsed.toFixed(3)} kWh  |  Baseline: ${energyBaseline.toFixed(3)} kWh`,
            color: 'teal',
        },
        {
            icon: Leaf,
            label: 'CO₂ Saved Today',
            value: `${co2Saved.toFixed(2)}g`,
            sub: `vs. unoptimized baseline model`,
            color: 'emerald',
        },
        {
            icon: Gauge,
            label: 'Efficiency Score',
            value: `${effScore.toFixed(0)}/100`,
            sub: effScore >= 70 ? 'Excellent — system is highly optimised' : effScore >= 40 ? 'Moderate — room for improvement' : 'Low — check system configuration',
            color: effColor,
        },
        {
            icon: Cpu,
            label: 'Optimized Tokens',
            value: (metrics?.optimized_tokens ?? 0).toLocaleString(),
            sub: `From ${(metrics?.original_tokens ?? 0).toLocaleString()} original tokens`,
            color: 'indigo',
        },
        {
            icon: Globe,
            label: 'Active Region',
            value: 'Auto-selected',
            sub: `Carbon-aware routing active`,
            color: 'cyan',
        },
    ] : [];

    return (
        <div className="min-h-full bg-[#080B10] text-white px-6 py-8">
            {/* Page Header */}
            <div className="max-w-7xl mx-auto">
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <div className="flex items-center gap-3 mb-1">
                            <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse shadow-lg shadow-emerald-400/50" />
                            <span className="text-emerald-400 text-xs font-bold uppercase tracking-widest">Real-time Feed</span>
                        </div>
                        <h1 className="text-3xl font-bold text-white">Live Metrics</h1>
                        <p className="text-gray-500 text-sm mt-1">All data pulled live from the CarbonSense backend every 5 seconds</p>
                    </div>

                    <div className="flex items-center gap-4">
                        {/* Countdown */}
                        <div className="flex items-center gap-2 text-gray-500 text-sm">
                            <Clock className="w-4 h-4" />
                            <span>Refresh in <span className="text-emerald-400 font-bold">{countdown}s</span></span>
                        </div>

                        {/* Last updated */}
                        {lastUpdated && (
                            <div className="text-xs text-gray-600">
                                Last updated: <span className="text-gray-400">{lastUpdated.toLocaleTimeString()}</span>
                            </div>
                        )}

                        {/* Manual refresh */}
                        <button
                            onClick={fetchMetrics}
                            disabled={isRefreshing}
                            className="flex items-center gap-2 px-4 py-2 bg-emerald-900/40 border border-emerald-700/40 rounded-xl text-emerald-300 text-xs font-bold hover:bg-emerald-800/40 transition-colors disabled:opacity-50"
                        >
                            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
                            Refresh
                        </button>
                    </div>
                </div>

                {/* Status bar */}
                <div className="flex items-center gap-3 mb-8 p-4 bg-white/3 border border-white/5 rounded-2xl">
                    <Wifi className="w-4 h-4 text-emerald-400" />
                    <span className="text-sm text-gray-400">Backend connection: </span>
                    <span className={`text-sm font-semibold ${metrics ? 'text-emerald-400' : 'text-amber-400'}`}>
                        {metrics ? '● Connected — Live data streaming' : '○ Connecting...'}
                    </span>
                    <div className="ml-auto text-xs text-gray-600">
                        Endpoint: <code className="text-gray-500">/api/v1/query/stats</code>
                    </div>
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    <AnimatePresence>
                        {metrics
                            ? metricCards.map((card, i) => (
                                <MetricCard key={card.label} {...card} index={i} />
                            ))
                            : [...Array(8)].map((_, i) => <SkeletonCard key={i} index={i} />)
                        }
                    </AnimatePresence>
                </div>

                {/* Footer note */}
                <p className="text-center text-xs text-gray-700 mt-10">
                    Data sourced from <code>/api/v1/query/stats</code> · Auto-refreshes every 5 seconds · Values may show 0 if backend is offline
                </p>
            </div>
        </div>
    );
};

export default LiveMetrics;
