'use client';

import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface MarketChartProps {
    pair: string;
    data?: any[];
}

export default function MarketChart({ pair, data }: MarketChartProps) {
    // TODO: Replace with real historical data
    // Generate mock data for demonstration
    const mockData = React.useMemo(() => {
        const points = 50;
        const basePrice = 1.1000;
        const chartData = [];

        let price = basePrice;
        for (let i = 0; i < points; i++) {
            const change = (Math.random() - 0.5) * 0.002;
            price = price * (1 + change);
            chartData.push({
                time: i,
                price: price,
                sma20: price * (1 + (Math.random() - 0.5) * 0.001),
                sma50: price * (1 + (Math.random() - 0.5) * 0.002)
            });
        }

        return chartData;
    }, [pair]);

    const chartData = data || mockData;

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <div className="mb-4">
                <h2 className="text-2xl font-bold">{pair}</h2>
                <p className="text-gray-500">Market Chart</p>
            </div>

            <ResponsiveContainer width="100%" height={400}>
                <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                    <XAxis
                        dataKey="time"
                        stroke="#9CA3AF"
                        tick={{ fill: '#9CA3AF' }}
                    />
                    <YAxis
                        stroke="#9CA3AF"
                        tick={{ fill: '#9CA3AF' }}
                        domain={['auto', 'auto']}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#1F2937',
                            border: 'none',
                            borderRadius: '8px',
                            color: '#F3F4F6'
                        }}
                    />
                    <Line
                        type="monotone"
                        dataKey="price"
                        stroke="#0ea5e9"
                        strokeWidth={2}
                        dot={false}
                        name="Price"
                    />
                    <Line
                        type="monotone"
                        dataKey="sma20"
                        stroke="#10b981"
                        strokeWidth={1.5}
                        strokeDasharray="5 5"
                        dot={false}
                        name="SMA 20"
                    />
                    <Line
                        type="monotone"
                        dataKey="sma50"
                        stroke="#f59e0b"
                        strokeWidth={1.5}
                        strokeDasharray="5 5"
                        dot={false}
                        name="SMA 50"
                    />
                </LineChart>
            </ResponsiveContainer>

            <div className="mt-4 flex gap-4 text-sm">
                <div className="flex items-center gap-2">
                    <div className="w-4 h-0.5 bg-primary-500"></div>
                    <span className="text-gray-600 dark:text-gray-400">Price</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-4 h-0.5 bg-success" style={{ borderTop: '2px dashed' }}></div>
                    <span className="text-gray-600 dark:text-gray-400">SMA 20</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-4 h-0.5 bg-warning" style={{ borderTop: '2px dashed' }}></div>
                    <span className="text-gray-600 dark:text-gray-400">SMA 50</span>
                </div>
            </div>
        </div>
    );
}
