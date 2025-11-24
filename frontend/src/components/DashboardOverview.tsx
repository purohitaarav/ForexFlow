'use client';

import React from 'react';
import { TrendingUp, TrendingDown, DollarSign, Activity } from 'lucide-react';

interface StatCardProps {
    title: string;
    value: string;
    change: string;
    changeType: 'positive' | 'negative' | 'neutral';
    icon: React.ReactNode;
}

function StatCard({ title, value, change, changeType, icon }: StatCardProps) {
    const changeColor = {
        positive: 'text-green-600 dark:text-green-400',
        negative: 'text-red-600 dark:text-red-400',
        neutral: 'text-gray-600 dark:text-gray-400'
    }[changeType];

    const ChangeIcon = changeType === 'positive' ? TrendingUp : TrendingDown;

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
                <div className="flex-1">
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                        {title}
                    </p>
                    <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                        {value}
                    </p>
                    <div className={`mt-2 flex items-center gap-1 text-sm ${changeColor}`}>
                        {changeType !== 'neutral' && <ChangeIcon className="w-4 h-4" />}
                        <span>{change}</span>
                    </div>
                </div>
                <div className="p-3 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
                    {icon}
                </div>
            </div>
        </div>
    );
}

interface QuickActionProps {
    title: string;
    description: string;
    icon: React.ReactNode;
    onClick: () => void;
}

function QuickAction({ title, description, icon, onClick }: QuickActionProps) {
    return (
        <button
            onClick={onClick}
            className="flex items-start gap-4 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-primary-500 dark:hover:border-primary-500 transition-colors text-left w-full"
        >
            <div className="p-2 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
                {icon}
            </div>
            <div className="flex-1">
                <h3 className="font-semibold text-gray-900 dark:text-white">
                    {title}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {description}
                </p>
            </div>
        </button>
    );
}

export default function DashboardOverview() {
    const stats = [
        {
            title: 'Total Portfolio Value',
            value: '$10,000',
            change: '+0.00%',
            changeType: 'neutral' as const,
            icon: <DollarSign className="w-6 h-6 text-primary-600 dark:text-primary-400" />
        },
        {
            title: 'Active Positions',
            value: '0',
            change: 'No open trades',
            changeType: 'neutral' as const,
            icon: <Activity className="w-6 h-6 text-primary-600 dark:text-primary-400" />
        },
        {
            title: 'Today\'s P&L',
            value: '$0.00',
            change: '+0.00%',
            changeType: 'neutral' as const,
            icon: <TrendingUp className="w-6 h-6 text-primary-600 dark:text-primary-400" />
        },
        {
            title: 'Win Rate',
            value: 'N/A',
            change: 'No trades yet',
            changeType: 'neutral' as const,
            icon: <Activity className="w-6 h-6 text-primary-600 dark:text-primary-400" />
        }
    ];

    const quickActions = [
        {
            title: 'Get AI Recommendation',
            description: 'Analyze market and get trade suggestions from MCP tools',
            icon: <TrendingUp className="w-5 h-5 text-primary-600 dark:text-primary-400" />
        },
        {
            title: 'View Market Analysis',
            description: 'See detailed technical analysis and indicators',
            icon: <Activity className="w-5 h-5 text-primary-600 dark:text-primary-400" />
        },
        {
            title: 'Backtest Strategy',
            description: 'Test your trading strategy on historical data',
            icon: <TrendingDown className="w-5 h-5 text-primary-600 dark:text-primary-400" />
        }
    ];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                    Dashboard
                </h1>
                <p className="mt-2 text-gray-600 dark:text-gray-400">
                    Welcome to ForexFlow - AI-Powered Forex Trading Simulator
                </p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {stats.map((stat, index) => (
                    <StatCard key={index} {...stat} />
                ))}
            </div>

            {/* Quick Actions */}
            <div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                    Quick Actions
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {quickActions.map((action, index) => (
                        <QuickAction
                            key={index}
                            {...action}
                            onClick={() => console.log(`Action: ${action.title}`)}
                        />
                    ))}
                </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                    Recent Activity
                </h2>
                <div className="text-center py-12">
                    <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600 dark:text-gray-400">
                        No recent activity. Start trading to see your history here.
                    </p>
                </div>
            </div>

            {/* MCP Tools Status */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                    MCP Tools Status
                </h2>
                <div className="space-y-3">
                    {['TrendSense', 'RiskGuard', 'OptiTrade'].map((tool) => (
                        <div key={tool} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                            <div className="flex items-center gap-3">
                                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                <span className="font-medium text-gray-900 dark:text-white">
                                    {tool}
                                </span>
                            </div>
                            <span className="text-sm text-green-600 dark:text-green-400">
                                Active
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
