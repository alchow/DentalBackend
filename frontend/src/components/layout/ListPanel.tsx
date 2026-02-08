'use client';

import React from 'react';
import styles from './ListPanel.module.css';

interface ListPanelProps {
    title: string;
    action?: React.ReactNode;
    children: React.ReactNode;
}

export default function ListPanel({ title, action, children }: ListPanelProps) {
    return (
        <div className={styles.panel}>
            <header className={styles.header}>
                <h2 className={styles.title}>{title}</h2>
                {action && <div>{action}</div>}
            </header>
            <div className={styles.content}>
                {children}
            </div>
        </div>
    );
}
