'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    LayoutDashboard,
    TrendingUp,
    Settings,
    Activity,
    Menu,
    X
} from 'lucide-react';

interface LayoutProps {
    children: React.ReactNode;
}

export default function DashboardLayout({ children }: LayoutProps) {
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const pathname = usePathname();

    const navigation = [
        { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
        { name: 'Live Trading', href: '/dashboard/trading', icon: TrendingUp },
        { name: 'Analytics', href: '/dashboard/analytics', icon: Activity },
        { name: 'Settings', href: '/dashboard/settings', icon: Settings },
    ];

    const isActive = (href: string) => pathname === href;

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
            {/* Sidebar */}
            <aside
                className={`fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transform transition-transform duration-300 ease-in-out ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'
                    }`}
            >
                <div className="flex flex-col h-full">
                    {/* Logo */}
                    <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200 dark:border-gray-700">
                        <Link href="/dashboard" className="flex items-center">
                            <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                                <TrendingUp className="w-5 h-5 text-white" />
                            </div>
                            <span className="ml-3 text-xl font-bold text-gray-900 dark:text-white">
                                ForexFlow
                            </span>
                        </Link>
                        <button
                            onClick={() => setSidebarOpen(false)}
                            className="lg:hidden text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                        >
                            <X className="w-6 h-6" />
                        </button>
                    </div>

                    {/* Navigation */}
                    <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
                        {navigation.map((item) => {
                            const Icon = item.icon;
                            const active = isActive(item.href);

                            return (
                                <Link
                                    key={item.name}
                                    href={item.href}
                                    className={`flex items-center px-4 py-3 rounded-lg transition-colors ${active
                                            ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400'
                                            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                                        }`}
                                >
                                    <Icon className="w-5 h-5" />
                                    <span className="ml-3 font-medium">{item.name}</span>
                                </Link>
                            );
                        })}
                    </nav>

                    {/* Footer */}
                    <div className="p-4 border-t border-gray-200 dark:border-gray-700">
                        <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                            <span>MCP Tools Active</span>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Mobile sidebar backdrop */}
            {sidebarOpen && (
                <div
                    className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
                    onClick={() => setSidebarOpen(false)}
                />
            )}

            {/* Main content */}
            <div className={`transition-all duration-300 ${sidebarOpen ? 'lg:pl-64' : ''}`}>
                {/* Top bar */}
                <header className="sticky top-0 z-30 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
                    <div className="flex items-center justify-between h-16 px-6">
                        <button
                            onClick={() => setSidebarOpen(!sidebarOpen)}
                            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                        >
                            <Menu className="w-6 h-6" />
                        </button>

                        <div className="flex items-center gap-4">
                            <div className="text-sm text-gray-600 dark:text-gray-400">
                                {new Date().toLocaleDateString('en-US', {
                                    weekday: 'long',
                                    year: 'numeric',
                                    month: 'long',
                                    day: 'numeric'
                                })}
                            </div>
                        </div>
                    </div>
                </header>

                {/* Page content */}
                <main className="p-6">
                    {children}
                </main>
            </div>
        </div>
    );
}
