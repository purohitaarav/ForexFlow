'use client';

import React from 'react';
import { TrendingUp, TrendingDown, Minus, AlertCircle, CheckCircle } from 'lucide-react';
import type { TradeResponse } from '@/services/api';

interface RecommendationPanelProps {
    recommendation: TradeResponse | null;
    loading: boolean;
    error: string | null;
}

export default function RecommendationPanel({
    recommendation,
    loading,
    error
}: RecommendationPanelProps) {
    if (loading) {
        return (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                <h2 className="text-2xl font-bold mb-4">AI Recommendation</h2>
                <div className="flex items-center justify-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                <h2 className="text-2xl font-bold mb-4">AI Recommendation</h2>
                <div className="flex items-center gap-2 text-danger p-4 bg-red-50 dark:bg-red-900/20 rounded">
                    <AlertCircle className="w-5 h-5" />
                    <span>{error}</span>
                </div>
            </div>
        );
    }

    if (!recommendation) {
        return (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                <h2 className="text-2xl font-bold mb-4">AI Recommendation</h2>
                <p className="text-gray-500">Select a forex pair to get AI-powered recommendations</p>
            </div>
        );
    }

    const { strategy, trend, risk_analysis, explanation, market_data } = recommendation;

    // Determine action color and icon
    const getActionStyle = (action: string) => {
        switch (action.toLowerCase()) {
            case 'buy':
                return {
                    color: 'text-success',
                    bgColor: 'bg-green-50 dark:bg-green-900/20',
                    icon: <TrendingUp className="w-6 h-6" />
                };
            case 'sell':
                return {
                    color: 'text-danger',
                    bgColor: 'bg-red-50 dark:bg-red-900/20',
                    icon: <TrendingDown className="w-6 h-6" />
                };
            default:
                return {
                    color: 'text-gray-500',
                    bgColor: 'bg-gray-50 dark:bg-gray-900/20',
                    icon: <Minus className="w-6 h-6" />
                };
        }
    };

    const actionStyle = getActionStyle(strategy.action);

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 space-y-6">
            <h2 className="text-2xl font-bold">AI Recommendation</h2>

            {/* Main Action */}
            <div className={`${actionStyle.bgColor} rounded-lg p-6`}>
                <div className="flex items-center gap-3 mb-3">
                    <div className={actionStyle.color}>
                        {actionStyle.icon}
                    </div>
                    <h3 className={`text-3xl font-bold uppercase ${actionStyle.color}`}>
                        {strategy.action}
                    </h3>
                </div>
                <div className="flex items-center gap-2 mb-2">
                    <span className="text-sm font-medium text-gray-600 dark:text-gray-300">
                        {market_data.pair} @ ${market_data.current_price.toFixed(5)}
                    </span>
                    <span className="text-xs text-gray-500">
                        Volatility: {(market_data.volatility * 100).toFixed(2)}%
                    </span>
                </div>
                <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${risk_analysis.is_valid
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                            : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                        }`}>
                        {risk_analysis.is_valid ? '✓ Risk Validated' : '✗ Risk Violated'}
                    </span>
                    <span className="px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                        Confidence: {(strategy.confidence_score * 100).toFixed(1)}%
                    </span>
                </div>
            </div>

            {/* Trend Probabilities */}
            <div className="border-t pt-4">
                <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <span>Trend Forecast</span>
                    <span className="text-xs text-gray-500">(TrendSense)</span>
                </h4>
                <div className="space-y-3">
                    <div className="flex justify-between items-center">
                        <span className="text-gray-600">Direction</span>
                        <span className={`font-bold capitalize ${trend.direction === 'bullish' ? 'text-success' :
                                trend.direction === 'bearish' ? 'text-danger' :
                                    'text-gray-500'
                            }`}>
                            {trend.direction}
                        </span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-600">Confidence</span>
                        <span className="font-bold">{(trend.confidence * 100).toFixed(1)}%</span>
                    </div>

                    {/* Probability Bars */}
                    <div className="space-y-2">
                        <div className="space-y-1">
                            <div className="flex justify-between text-sm">
                                <span className="text-success">↑ Bullish</span>
                                <span className="font-medium">{(trend.probability_up * 100).toFixed(1)}%</span>
                            </div>
                            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                <div
                                    className="bg-success h-2 rounded-full transition-all"
                                    style={{ width: `${trend.probability_up * 100}%` }}
                                />
                            </div>
                        </div>
                        <div className="space-y-1">
                            <div className="flex justify-between text-sm">
                                <span className="text-danger">↓ Bearish</span>
                                <span className="font-medium">{(trend.probability_down * 100).toFixed(1)}%</span>
                            </div>
                            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                <div
                                    className="bg-danger h-2 rounded-full transition-all"
                                    style={{ width: `${trend.probability_down * 100}%` }}
                                />
                            </div>
                        </div>
                        <div className="space-y-1">
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-500">→ Neutral</span>
                                <span className="font-medium">{(trend.probability_neutral * 100).toFixed(1)}%</span>
                            </div>
                            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                <div
                                    className="bg-gray-500 h-2 rounded-full transition-all"
                                    style={{ width: `${trend.probability_neutral * 100}%` }}
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Trade Parameters */}
            {strategy.action !== 'hold' && (
                <div className="border-t pt-4">
                    <h4 className="font-semibold mb-3 flex items-center gap-2">
                        <span>Trade Parameters</span>
                        <span className="text-xs text-gray-500">(OptiTrade)</span>
                    </h4>
                    <div className="grid grid-cols-2 gap-3">
                        <div className="bg-gray-50 dark:bg-gray-900/50 rounded p-3">
                            <p className="text-xs text-gray-500 mb-1">Entry Price</p>
                            <p className="text-lg font-bold">{strategy.entry_price.toFixed(5)}</p>
                        </div>
                        <div className="bg-gray-50 dark:bg-gray-900/50 rounded p-3">
                            <p className="text-xs text-gray-500 mb-1">Position Size</p>
                            <p className="text-lg font-bold">{strategy.position_size.toFixed(0)} units</p>
                        </div>
                        <div className="bg-gray-50 dark:bg-gray-900/50 rounded p-3">
                            <p className="text-xs text-gray-500 mb-1">Stop Loss</p>
                            <p className="text-lg font-bold text-danger">{strategy.stop_loss.toFixed(5)}</p>
                        </div>
                        <div className="bg-gray-50 dark:bg-gray-900/50 rounded p-3">
                            <p className="text-xs text-gray-500 mb-1">Take Profit</p>
                            <p className="text-lg font-bold text-success">{strategy.take_profit.toFixed(5)}</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Risk Analysis */}
            <div className="border-t pt-4">
                <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <span>Risk Analysis</span>
                    <span className="text-xs text-gray-500">(RiskGuard CSP)</span>
                </h4>
                <div className="space-y-2">
                    <div className="flex justify-between">
                        <span className="text-gray-600">Status</span>
                        <span className={`font-bold flex items-center gap-1 ${risk_analysis.is_valid ? 'text-success' : 'text-danger'
                            }`}>
                            {risk_analysis.is_valid ? (
                                <><CheckCircle className="w-4 h-4" /> Valid</>
                            ) : (
                                <><AlertCircle className="w-4 h-4" /> Violated</>
                            )}
                        </span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-600">Max Position</span>
                        <span className="font-bold">{risk_analysis.max_position_size.toFixed(0)} units</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-600">Risk Amount</span>
                        <span className="font-bold">${risk_analysis.risk_amount.toFixed(2)}</span>
                    </div>
                    {strategy.action !== 'hold' && (
                        <>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Risk/Reward</span>
                                <span className="font-bold">{strategy.risk_reward_ratio.toFixed(2)}:1</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Leverage</span>
                                <span className="font-bold">{strategy.leverage.toFixed(1)}x</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Expected Profit</span>
                                <span className={`font-bold ${strategy.expected_profit >= 0 ? 'text-success' : 'text-danger'}`}>
                                    ${strategy.expected_profit.toFixed(2)}
                                </span>
                            </div>
                        </>
                    )}
                    {risk_analysis.constraint_violations.length > 0 && (
                        <div className="mt-2 p-2 bg-red-50 dark:bg-red-900/20 rounded">
                            <p className="text-xs font-medium text-danger mb-1">Violations:</p>
                            {risk_analysis.constraint_violations.map((violation, i) => (
                                <p key={i} className="text-xs text-danger">• {violation}</p>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Explanation */}
            <div className="border-t pt-4">
                <h4 className="font-semibold mb-2">Detailed Explanation</h4>
                <div className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-line max-h-64 overflow-y-auto">
                    {explanation}
                </div>
            </div>

            {/* MCP Tools Footer */}
            <div className="border-t pt-4">
                <p className="text-xs text-gray-500">
                    Powered by MCP: <span className="font-semibold">TrendSense</span> (Probabilistic) •
                    <span className="font-semibold"> OptiTrade</span> (Beam Search) •
                    <span className="font-semibold"> RiskGuard</span> (CSP)
                </p>
            </div>
        </div>
    );
}
