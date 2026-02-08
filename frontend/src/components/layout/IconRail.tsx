'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Calendar, CheckSquare, Bell, Settings, Users, LogOut } from 'lucide-react';
import { useAuth } from '@/lib/contexts/AuthContext';
import styles from './IconRail.module.css';

export default function IconRail() {
    const pathname = usePathname();
    const { logout } = useAuth();

    const isActive = (path: string) => {
        return pathname.startsWith(path);
    };

    const navItems = [
        {
            label: 'Schedule',
            path: '/schedule',
            icon: <Calendar className={styles.icon} />,
        },
        {
            label: 'Patients',
            path: '/patients',
            icon: <Users className={styles.icon} />,
        },
        {
            label: 'Tasks',
            path: '/tasks',
            icon: <CheckSquare className={styles.icon} />,
        },
        // Notifications disabled for MVP per user request
        // {
        //   label: 'Notifications',
        //   path: '/notifications',
        //   icon: <Bell className={styles.icon} />,
        // },
        {
            label: 'Settings',
            path: '/settings',
            icon: <Settings className={styles.icon} />,
        },
    ];

    return (
        <nav className={styles.rail}>
            <div className={styles.topSection}>
                {navItems.map((item) => (
                    <Link
                        key={item.path}
                        href={item.path}
                        className={`${styles.navItem} ${isActive(item.path) ? styles.active : ''}`}
                        title={item.label}
                    >
                        {item.icon}
                        <span className="sr-only">{item.label}</span>
                    </Link>
                ))}
            </div>

            <div className={styles.bottomSection}>
                <button
                    onClick={logout}
                    className={styles.navItem}
                    title="Sign out"
                >
                    <LogOut className={styles.icon} />
                    <span className="sr-only">Sign out</span>
                </button>
            </div>
        </nav>
    );
}
