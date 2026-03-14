import React from 'react';
import { cn } from '../../lib/utils';

export const Badge = ({ className, variant = 'default', children, ...props }) => {
    const variants = {
        default: 'bg-gray-800 text-gray-300',
        success: 'bg-emerald-900/30 text-emerald-400 border border-emerald-800/50',
        warning: 'bg-yellow-900/30 text-yellow-500 border border-yellow-800/50',
        info: 'bg-teal-900/30 text-teal-400 border border-teal-800/50',
        error: 'bg-red-900/30 text-red-500 border border-red-800/50',
    };

    return (
        <div
            className={cn(
                "inline-flex items-center rounded-full border border-transparent px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
                variants[variant],
                className
            )}
            {...props}
        >
            {children}
        </div>
    );
};
