'use client';

import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Minus, AlertCircle } from 'lucide-react';
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

    const { recommendation: trade, trend_forecast, risk_constraints } = recommendation;

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

    const actionStyle = getActionStyle(trade.action);

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 space-y-6">
            <h2 className="text-2xl font-bold">AI Recommendation</h2>

            {/* Main Action */}
            <div className={`${actionStyle.bgColor} rounded-lg p-6`}>
                <div className="flex items-center gap-3 mb-2">
                    <div className={actionStyle.color}>
                        {actionStyle.icon}
                    </div>
                    <h3 className={`text-3xl font-bold uppercase ${actionStyle.color}`}>
                        {trade.action}
                    </h3>
                </div>
                <p className="text-gray-600 dark:text-gray-300">{trade.reasoning}</p>
            </div>

            {/* Trade Parameters */}
            <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 dark:bg-gray-900/50 rounded p-4">
                    <p className="text-sm text-gray-500 mb-1">Entry Price</p>
                    <p className="text-xl font-bold">{trade.entry_price.toFixed(5)}</p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-900/50 rounded p-4">
                    <p className="text-sm text-gray-500 mb-1">Position Size</p>
                    <p className="text-xl font-bold">${trade.position_size.toFixed(2)}</p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-900/50 rounded p-4">
                    <p className="text-sm text-gray-500 mb-1">Stop Loss</p>
                    <p className="text-xl font-bold text-danger">{trade.stop_loss.toFixed(5)}</p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-900/50 rounded p-4">
                    <p className="text-sm text-gray-500 mb-1">Take Profit</p>
                    <p className="text-xl font-bold text-success">{trade.take_profit.toFixed(5)}</p>
                </div>
            </div>

            {/* Risk Metrics */}
            <div className="border-t pt-4">
                <h4 className="font-semibold mb-3">Risk Analysis</h4>
                <div className="space-y-2">
                    <div className="flex justify-between">
                        <span className="text-gray-600">Risk/Reward Ratio</span>
                        <span className="font-bold">{trade.risk_reward_ratio.toFixed(2)}:1</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-600">Leverage</span>
                        <span className="font-bold">{trade.leverage.toFixed(1)}x</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-600">Expected Profit</span>
                        <span className={`font-bold ${trade.expected_profit >= 0 ? 'text-success' : 'text-danger'}`}>
                            ${trade.expected_profit.toFixed(2)}
                        </span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-600">Confidence Score</span>
                        <span className="font-bold">{(trade.confidence_score * 100).toFixed(1)}%</span>
                    </div>
                </div>
            </div>

            {/* Trend Forecast */}
            <div className="border-t pt-4">
                <h4 className="font-semibold mb-3">Trend Forecast (TrendSense)</h4>
                <div className="space-y-2">
                    <div className="flex justify-between items-center">
                        <span className="text-gray-600">Direction</span>
                        <span className={`font-bold capitalize ${trend_forecast.direction === 'bullish' ? 'text-success' :
                                trend_forecast.direction === 'bearish' ? 'text-danger' :
                                    'text-gray-500'
                            }`}>
                            {trend_forecast.direction}
                        </span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-600">Confidence</span>
                        <span className="font-bold">{(trend_forecast.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div className="space-y-1">
                        <div className="flex justify-between text-sm">
                            <span>Bullish</span>
                            <span>{(trend_forecast.probability_up * 100).toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                                className="bg-success h-2 rounded-full"
                                style={{ width: `${trend_forecast.probability_up * 100}%` }}
                            />
                        </div>
                    </div>
                    <div className="space-y-1">
                        <div className="flex justify-between text-sm">
                            <span>Bearish</span>
                            <span>{(trend_forecast.probability_down * 100).toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                                className="bg-danger h-2 rounded-full"
                                style={{ width: `${trend_forecast.probability_down * 100}%` }}
                            />
                        </div>
                    </div>
                </div>
            </div>

            {/* MCP Tools Info */}
            <div className="border-t pt-4">
                <p className="text-xs text-gray-500">
                    Powered by: <span className="font-semibold">TrendSense</span> (Probabilistic Reasoning) •
                    <span className="font-semibold"> RiskGuard</span> (CSP) •
                    <span className="font-semibold"> OptiTrade</span> (Search)
                </p>
            </div>
        </div>
    );
}
