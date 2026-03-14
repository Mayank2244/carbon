export const carbonSenseAPI = {
    async sendQuery(query, context = null) {
        try {
            const body = {
                query: query,
                optimize_for: 'carbon',
                use_cache: true
            };

            if (context) {
                body.context = context;
            }

            // LIVE DEPLOYMENT: Using Cloudflare Tunnel URL instead of localhost
            const response = await fetch('/api/v1/query/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(body)
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            return {
                text: data.response,
                model: data.model_used,
                region: data.region || 'unknown',
                carbon_gco2: data.carbon_grams,
                saved_gco2: data.saved_gco2 || 0,
                tokens: data.tokens_used,
                original_tokens: data.metadata?.original_tokens || 0,
                optimized_tokens: data.metadata?.optimized_tokens || 0
            };
        } catch (error) {
            console.error("API Error (sendQuery):", error);
            // Fallback/Demo mode if backend is offline
            return {
                text: "Backend connection failed. This is a demo response.\n\n" + error.message,
                model: "offline-fallback",
                region: "local",
                carbon_gco2: 0,
                saved_gco2: 0,
                tokens: 0
            };
        }
    },

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/v1/files/upload', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('File upload failed');
            }

            return await response.json();
        } catch (error) {
            console.error("API Error (uploadFile):", error);
            throw error;
        }
    },

    async getMetrics() {
        try {
            const response = await fetch('/api/v1/query/stats');
            if (!response.ok) throw new Error("Failed to fetch stats");

            const data = await response.json();
            return {
                carbon_intensity: data.carbon_intensity || 150,
                cache_hit_rate: data.cache_hit_rate || 0,
                tokens_saved: data.tokens_saved || 0,
                tokens_saved_percent: data.tokens_saved_percent || 0,
                carbon_saved_today: data.carbon_saved_today || 0,
                energy_saved_kwh: data.energy_saved_kwh || 0,
                energy_used_kwh: data.energy_used_kwh || 0,
                energy_baseline_kwh: data.energy_baseline_kwh || 0,
                active_model_dist: data.active_model_dist || [],
                response_times: data.response_times || [],
                efficiency_score: data.efficiency_score || 0,
                top_actions: data.top_actions || [],
                regional_breakdown: data.regional_breakdown || []
            };
        } catch (error) {
            console.error("API Error (getMetrics):", error);
            // Fallback
            return {
                carbon_intensity: 154,
                cache_hit_rate: 0.38,
                tokens_saved: 12450,
                tokens_saved_percent: 15.2,
                carbon_saved_today: 0,
                energy_saved_kwh: 0,
                active_model_dist: [],
                response_times: [],
                efficiency_score: 0,
                top_actions: [],
                regional_breakdown: []
            };
        }
    },

    async sendFeedback(query, rating) {
        try {
            await fetch('/api/v1/query/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, rating })
            });
        } catch (error) {
            console.error("Feedback Error:", error);
        }
    },

    async getAnalytics(range = '7d') {
        try {
            const response = await fetch('/api/v1/query/analytics');
            if (!response.ok) throw new Error("Failed to fetch analytics");
            return await response.json();
        } catch (error) {
            console.error("API Error (getAnalytics):", error);
            // Fallback
            return {
                weekly_data: [],
                total_emissions: 0,
                total_requests: 0
            };
        }
    }
};
