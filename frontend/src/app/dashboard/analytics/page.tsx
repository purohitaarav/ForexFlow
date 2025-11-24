'use client';

import React from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { BarChart3, TrendingUp, DollarSign, Target } from 'lucide-react';

export default function AnalyticsPage() {
    return (
        <DashboardLayout>
            <div className="space-y-6">
                {/* Header */}
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                        Analytics
                    </h1>
                    <p className="mt-2 text-gray-600 dark:text-gray-400">
                        Performance metrics and trading analytics
                    </p>
                </div>

                {/* Performance Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                                    Total Trades
                                </p>
                                <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                                    0
                                </p>
                            </div>
                            <div className="p-3 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
                                <BarChart3 className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                            </div>
                        </div>
                    </div>

                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                                    Win Rate
                                </p>
                                <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                                    N/A
                                </p>
                            </div>
                            <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                <Target className="w-6 h-6 text-green-600 dark:text-green-400" />
                            </div>
                        </div>
                    </div>

                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                                    Total P&L
                                </p>
                                <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                                    $0.00
                                </p>
                            </div>
                            <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                                <DollarSign className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                            </div>
                        </div>
                    </div>

                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                                    Sharpe Ratio
                                </p>
                                <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                                    N/A
                                </p>
                            </div>
                            <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                                <TrendingUp className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Placeholder for charts */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                    <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                        Equity Curve
                    </h2>
                    <div className="h-64 flex items-center justify-center bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                        <div className="text-center">
                            <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                            <p className="text-gray-600 dark:text-gray-400">
                                No trading data available yet
                            </p>
                        </div>
                    </div>
                </div>

                {/* Trade History */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                    <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                        Trade History
                    </h2>
                    <div className="text-center py-12">
                        <p className="text-gray-600 dark:text-gray-400">
                            No trades executed yet. Start trading to see your history here.
                        </p>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
