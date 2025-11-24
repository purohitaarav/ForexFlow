'use client';

import React, { useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { Save, User, Bell, Shield, Palette } from 'lucide-react';

export default function SettingsPage() {
    const [settings, setSettings] = useState({
        defaultPair: 'EURUSD',
        defaultProfile: 'balanced',
        defaultCapital: 10000,
        notifications: true,
        darkMode: false,
        autoRefresh: true
    });

    const handleSave = () => {
        console.log('Saving settings:', settings);
        // TODO: Implement settings save
    };

    return (
        <DashboardLayout>
            <div className="space-y-6">
                {/* Header */}
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                        Settings
                    </h1>
                    <p className="mt-2 text-gray-600 dark:text-gray-400">
                        Manage your trading preferences and account settings
                    </p>
                </div>

                {/* Trading Defaults */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-3 mb-6">
                        <User className="w-5 h-5 text-primary-500" />
                        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                            Trading Defaults
                        </h2>
                    </div>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Default Forex Pair
                            </label>
                            <select
                                value={settings.defaultPair}
                                onChange={(e) => setSettings({ ...settings, defaultPair: e.target.value })}
                                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                            >
                                <option value="EURUSD">EURUSD</option>
                                <option value="GBPUSD">GBPUSD</option>
                                <option value="USDJPY">USDJPY</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Default Trader Profile
                            </label>
                            <select
                                value={settings.defaultProfile}
                                onChange={(e) => setSettings({ ...settings, defaultProfile: e.target.value })}
                                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                            >
                                <option value="conservative">Conservative</option>
                                <option value="balanced">Balanced</option>
                                <option value="aggressive">Aggressive</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Default Capital ($)
                            </label>
                            <input
                                type="number"
                                value={settings.defaultCapital}
                                onChange={(e) => setSettings({ ...settings, defaultCapital: Number(e.target.value) })}
                                min="1000"
                                step="1000"
                                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                            />
                        </div>
                    </div>
                </div>

                {/* Notifications */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-3 mb-6">
                        <Bell className="w-5 h-5 text-primary-500" />
                        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                            Notifications
                        </h2>
                    </div>

                    <div className="space-y-4">
                        <label className="flex items-center justify-between">
                            <span className="text-gray-700 dark:text-gray-300">
                                Enable notifications
                            </span>
                            <input
                                type="checkbox"
                                checked={settings.notifications}
                                onChange={(e) => setSettings({ ...settings, notifications: e.target.checked })}
                                className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                            />
                        </label>

                        <label className="flex items-center justify-between">
                            <span className="text-gray-700 dark:text-gray-300">
                                Auto-refresh recommendations
                            </span>
                            <input
                                type="checkbox"
                                checked={settings.autoRefresh}
                                onChange={(e) => setSettings({ ...settings, autoRefresh: e.target.checked })}
                                className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                            />
                        </label>
                    </div>
                </div>

                {/* Save Button */}
                <div className="flex justify-end">
                    <button
                        onClick={handleSave}
                        className="px-6 py-2 bg-primary-500 hover:bg-primary-600 text-white font-medium rounded-lg transition-colors flex items-center gap-2"
                    >
                        <Save className="w-4 h-4" />
                        Save Settings
                    </button>
                </div>
            </div>
        </DashboardLayout>
    );
}
