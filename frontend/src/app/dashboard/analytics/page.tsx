'use client';

import React, { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { BarChart3 } from 'lucide-react';
import { getHistoricalState, getTrendAnalysis, MarketState, TrendAnalysisResponse } from '@/services/api';

export default function AnalyticsPage() {
    const [pair, setPair] = useState('EURUSD');
    const [date, setDate] = useState(() => {
        const today = new Date();
        return today.toISOString().split('T')[0]; // YYYY-MM-DD
    });
    const [windowSize, setWindowSize] = useState(60);
    const [marketState, setMarketState] = useState<MarketState | null>(null);
    const [trendResult, setTrendResult] = useState<TrendAnalysisResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            const state = await getHistoricalState(pair, date, windowSize);
            setMarketState(state);
            const trend = await getTrendAnalysis(pair, date, windowSize);
            setTrendResult(trend);
        } catch (e: any) {
            setError(e.message || 'Unexpected error');
            setMarketState(null);
            setTrendResult(null);
        } finally {
            setLoading(false);
        }
    };

    return (
        <DashboardLayout>
            <div className="space-y-6">
                {/* Header */}
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Analytics</h1>
                    <p className="mt-2 text-gray-600 dark:text-gray-400">
                        Performance metrics and trading analytics
                    </p>
                </div>

                {/* Controls */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Pair</label>
                        <input
                            type="text"
                            value={pair}
                            onChange={e => setPair(e.target.value.toUpperCase())}
                            className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Date</label>
                        <input
                            type="date"
                            value={date}
                            onChange={e => setDate(e.target.value)}
                            className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                        />
                    </div>
                    <div className="flex items-end">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Window Size</label>
                            <input
                                type="number"
                                min="1"
                                value={windowSize}
                                onChange={e => setWindowSize(parseInt(e.target.value) || 60)}
                                className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                            />
                        </div>
                        <button
                            onClick={fetchData}
                            disabled={loading}
                            className="inline-flex items-center justify-center rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50 ml-4"
                        >
                            {loading ? 'Loading…' : 'Fetch Data'}
                        </button>
                    </div>
                </div>

                {/* Error Message */}
                {error && (
                    <div className="rounded-md bg-red-100 p-4 text-red-800">
                        {error}
                    </div>
                )}

                {/* Market State Summary */}
                {marketState && (
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Market State</h2>
                        <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <dt className="text-sm font-medium text-gray-600 dark:text-gray-400">Pair</dt>
                                <dd className="mt-1 text-lg font-medium text-gray-900 dark:text-white">{marketState.pair}</dd>
                            </div>
                            <div>
                                <dt className="text-sm font-medium text-gray-600 dark:text-gray-400">Date</dt>
                                <dd className="mt-1 text-lg font-medium text-gray-900 dark:text-white">{marketState.as_of_date}</dd>
                            </div>
                            <div>
                                <dt className="text-sm font-medium text-gray-600 dark:text-gray-400">Volatility (20d)</dt>
                                <dd className="mt-1 text-lg font-medium text-gray-900 dark:text-white">
                                    {marketState.volatility_20d?.toFixed(4) ?? 'N/A'}
                                </dd>
                            </div>
                            <div>
                                <dt className="text-sm font-medium text-gray-600 dark:text-gray-400">SMA (5d)</dt>
                                <dd className="mt-1 text-lg font-medium text-gray-900 dark:text-white">
                                    {marketState.sma_short?.toFixed(4) ?? 'N/A'}
                                </dd>
                            </div>
                            <div>
                                <dt className="text-sm font-medium text-gray-600 dark:text-gray-400">SMA (20d)</dt>
                                <dd className="mt-1 text-lg font-medium text-gray-900 dark:text-white">
                                    {marketState.sma_long?.toFixed(4) ?? 'N/A'}
                                </dd>
                            </div>
                            <div>
                                <dt className="text-sm font-medium text-gray-600 dark:text-gray-400">Data Points</dt>
                                <dd className="mt-1 text-lg font-medium text-gray-900 dark:text-white">
                                    {marketState.data_points}
                                </dd>
                            </div>
                        </dl>
                    </div>
                )}

                {/* Trend Analysis Result */}
                {trendResult && (
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Trend Analysis</h2>
                        <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <dt className="text-sm font-medium text-gray-600 dark:text-gray-400">Up Probability</dt>
                                <dd className="mt-1 text-lg font-medium text-green-600 dark:text-green-400">
                                    {(trendResult.trend_up_prob * 100).toFixed(1)}%
                                </dd>
                            </div>
                            <div>
                                <dt className="text-sm font-medium text-gray-600 dark:text-gray-400">Down Probability</dt>
                                <dd className="mt-1 text-lg font-medium text-red-600 dark:text-red-400">
                                    {(trendResult.trend_down_prob * 100).toFixed(1)}%
                                </dd>
                            </div>
                            <div>
                                <dt className="text-sm font-medium text-gray-600 dark:text-gray-400">Volatility</dt>
                                <dd className="mt-1 text-lg font-medium text-gray-900 dark:text-white">
                                    {trendResult.volatility?.toFixed(4)}
                                </dd>
                            </div>
                            <div className="col-span-2">
                                <dt className="text-sm font-medium text-gray-600 dark:text-gray-400">Explanation</dt>
                                <dd className="mt-2 text-gray-800 dark:text-gray-200 whitespace-pre-line">
                                    {trendResult.explanation}
                                </dd>
                            </div>
                        </dl>
                    </div>
                )}

                {/* Placeholder for charts */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                    <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Equity Curve</h2>
                    <div className="h-64 flex items-center justify-center bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                        <div className="text-center">
                            <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                            <p className="text-gray-600 dark:text-gray-400">No trading data available yet</p>
                        </div>
                    </div>
                </div>

                {/* Trade History */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                    <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Trade History</h2>
                    <div className="text-center py-12">
                        <p className="text-gray-600 dark:text-gray-400">No trades executed yet. Start trading to see your history here.</p>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
