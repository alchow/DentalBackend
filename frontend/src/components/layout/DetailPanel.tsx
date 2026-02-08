'use client';

import React from 'react';
import styles from './DetailPanel.module.css';

interface DetailPanelProps {
    title: string;
    subtitle?: string; // e.g., "30 year old male"
    actions?: React.ReactNode;
    children: React.ReactNode;
}

export default function DetailPanel({
    title,
    subtitle,
    actions,
    children
}: DetailPanelProps) {
    return (
        <div className={styles.panel}>
            <header className={styles.header}>
                <div className={styles.titleGroup}>
                    <h2 className={styles.title}>{title}</h2>
                    {subtitle && <span className={styles.subtitle}>{subtitle}</span>}
                </div>

                {actions && (
                    <div className={styles.actions}>
                        {actions}
                    </div>
                )}
            </header>

            <div className={styles.content}>
                {children}
            </div>
        </div>
    );
}
