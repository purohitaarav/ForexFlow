'use client';

import React, { useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import MarketChart from '@/components/MarketChart';
import RecommendationPanel from '@/components/RecommendationPanel';
import { getTradeRecommendation, getLiveQuote, type TradeResponse } from '@/services/api';
import { RefreshCw, TrendingUp, ArrowUp, ArrowDown } from 'lucide-react';

function LiveQuotePanel({ pair }: { pair: string }) {
    const [quote, setQuote] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchQuote = async () => {
        setLoading(true);
        try {
            const result = await getLiveQuote(pair);
            if (result.success) {
                setQuote(result.data);
                setError(null);
            }
        } catch (err) {
            console.error(err);
            setError('Failed to fetch quote');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchQuote();
        const interval = setInterval(fetchQuote, 10000); // Refresh every 10s
        return () => clearInterval(interval);
    }, [pair]);

    if (!quote) return null;

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 border border-gray-200 dark:border-gray-700 mb-6">
            <div className="flex items-center justify-between">
                <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                        {pair} Live Quote
                        {loading && <RefreshCw className="w-3 h-3 animate-spin text-gray-400" />}
                    </h3>
                    <p className="text-xs text-gray-500">
                        {new Date(quote.timestamp).toLocaleTimeString()}
                    </p>
                </div>
                <div className="flex items-center gap-6">
                    <div className="text-center">
                        <p className="text-xs text-gray-500 uppercase">Bid</p>
                        <p className="text-xl font-mono font-bold text-red-600 dark:text-red-400">
                            {quote.bid.toFixed(5)}
                        </p>
                    </div>
                    <div className="text-center">
                        <p className="text-xs text-gray-500 uppercase">Ask</p>
                        <p className="text-xl font-mono font-bold text-green-600 dark:text-green-400">
                            {quote.ask.toFixed(5)}
                        </p>
                    </div>
                    <div className="text-center">
                        <p className="text-xs text-gray-500 uppercase">Spread</p>
                        <p className="text-sm font-mono font-medium text-gray-700 dark:text-gray-300">
                            {(quote.spread * 10000).toFixed(1)} pips
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

const FOREX_PAIRS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'USDCHF'];
const TRADER_PROFILES = ['conservative', 'balanced', 'aggressive'];

export default function TradingPage() {
    const [selectedPair, setSelectedPair] = useState('EURUSD');
    const [selectedProfile, setSelectedProfile] = useState('balanced');
    const [capital, setCapital] = useState(10000);
    const [recommendation, setRecommendation] = useState<TradeResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Fetch recommendation
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
        <DashboardLayout>
            <div className="space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                            Live Trading
                        </h1>
                        <p className="mt-2 text-gray-600 dark:text-gray-400">
                            Get AI-powered trade recommendations using MCP tools
                        </p>
                    </div>
                    <div className="flex items-center gap-2 px-4 py-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        <span className="text-sm font-medium text-green-700 dark:text-green-400">
                            Market Open
                        </span>
                    </div>
                </div>

                {/* Controls */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
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

                {/* Live Quote Panel */}
                <LiveQuotePanel pair={selectedPair} />

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

                {/* Trading Info */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-primary-500" />
                        How It Works
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                            <h4 className="font-semibold text-primary-500 mb-2">1. TrendSense</h4>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                Analyzes market data using probabilistic reasoning to forecast trends with uncertainty quantification
                            </p>
                        </div>
                        <div className="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                            <h4 className="font-semibold text-primary-500 mb-2">2. RiskGuard</h4>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                Validates risk parameters using constraint satisfaction to ensure safe trading limits
                            </p>
                        </div>
                        <div className="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                            <h4 className="font-semibold text-primary-500 mb-2">3. OptiTrade</h4>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                Finds optimal trade strategy using beam search to maximize expected returns
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
