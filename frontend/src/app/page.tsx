'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import MarketChart from '@/components/MarketChart';
import RecommendationPanel from '@/components/RecommendationPanel';
import { getTradeRecommendation, type TradeResponse } from '@/services/api';
import { RefreshCw, ArrowRight } from 'lucide-react';

const FOREX_PAIRS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'USDCHF'];
const TRADER_PROFILES = ['conservative', 'balanced', 'aggressive'];

export default function Home() {
    const [selectedPair, setSelectedPair] = useState('EURUSD');
    const [selectedProfile, setSelectedProfile] = useState('balanced');
    const [capital, setCapital] = useState(10000);
    const [recommendation, setRecommendation] = useState<TradeResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Fetch recommendation when parameters change
    const fetchRecommendation = async () => {
        setLoading(true);
        setError(null);

        try {
            const result = await getTradeRecommendation(selectedPair, selectedProfile, capital);
            setRecommendation(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch recommendation');
            setRecommendation(null);
        } finally {
            setLoading(false);
        }
    };

    // Auto-fetch on mount
    useEffect(() => {
        fetchRecommendation();
    }, []);

    return (
        <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
            {/* Header */}
            <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                                ForexFlow
                            </h1>
                            <p className="text-gray-500 dark:text-gray-400 mt-1">
                                AI-Powered Forex Trading Simulator
                            </p>
                        </div>
                        <div className="flex items-center gap-4">
                            <Link
                                href="/dashboard"
                                className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white font-medium rounded-lg transition-colors flex items-center gap-2"
                            >
                                Go to Dashboard
                                <ArrowRight className="w-4 h-4" />
                            </Link>
                            <div className="flex items-center gap-2 text-sm text-gray-500">
                                <div className="w-2 h-2 bg-success rounded-full animate-pulse"></div>
                                <span>MCP Tools Active</span>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* Controls */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        {/* Forex Pair Selector */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Forex Pair
                            </label>
                            <select
                                value={selectedPair}
                                onChange={(e) => setSelectedPair(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                            >
                                {FOREX_PAIRS.map(pair => (
                                    <option key={pair} value={pair}>{pair}</option>
                                ))}
                            </select>
                        </div>

                        {/* Trader Profile Selector */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Trader Profile
                            </label>
                            <select
                                value={selectedProfile}
                                onChange={(e) => setSelectedProfile(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                            >
                                {TRADER_PROFILES.map(profile => (
                                    <option key={profile} value={profile}>
                                        {profile.charAt(0).toUpperCase() + profile.slice(1)}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* Capital Input */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Capital ($)
                            </label>
                            <input
                                type="number"
                                value={capital}
                                onChange={(e) => setCapital(Number(e.target.value))}
                                min="1000"
                                step="1000"
                                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                            />
                        </div>

                        {/* Get Recommendation Button */}
                        <div className="flex items-end">
                            <button
                                onClick={fetchRecommendation}
                                disabled={loading}
                                className="w-full px-4 py-2 bg-primary-500 hover:bg-primary-600 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
                            >
                                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                                {loading ? 'Analyzing...' : 'Get Recommendation'}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Market Chart */}
                    <MarketChart pair={selectedPair} />

                    {/* AI Recommendation Panel */}
                    <RecommendationPanel
                        recommendation={recommendation}
                        loading={loading}
                        error={error}
                    />
                </div>

                {/* Footer Info */}
                <div className="mt-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                    <h3 className="text-lg font-semibold mb-3">About ForexFlow</h3>
                    <p className="text-gray-600 dark:text-gray-400 mb-4">
                        ForexFlow demonstrates how Model Context Protocol (MCP) can coordinate multiple classical AI methods:
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                            <h4 className="font-semibold text-primary-500 mb-2">TrendSense</h4>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                Probabilistic reasoning for trend forecasting with uncertainty quantification
                            </p>
                        </div>
                        <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                            <h4 className="font-semibold text-primary-500 mb-2">RiskGuard</h4>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                Constraint satisfaction problem (CSP) for risk management and validation
                            </p>
                        </div>
                        <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                            <h4 className="font-semibold text-primary-500 mb-2">OptiTrade</h4>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                Search-based optimization using beam search for optimal trade strategies
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}
