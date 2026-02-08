'use client';

import React from 'react';
import { X, Check, AlertTriangle } from 'lucide-react';
import styles from './ClinicalNoteLayout.module.css';

interface ClinicalNoteLayoutProps {
    title: string;
    patientName: string;
    allergies?: string[];
    onClose: () => void;
    onSave: () => void;
    isSaving?: boolean;
    children: React.ReactNode;
}

export default function ClinicalNoteLayout({
    title,
    patientName,
    allergies = [],
    onClose,
    onSave,
    isSaving = false,
    children,
}: ClinicalNoteLayoutProps) {
    return (
        <div className={styles.fullScreenOverlay}>
            {/* Header */}
            <header className={styles.header}>
                <div className={styles.headerLeft}>
                    <button
                        onClick={onClose}
                        className={styles.closeButton}
                        aria-label="Close"
                    >
                        <X className="w-5 h-5" />
                    </button>
                    <div className={styles.titleGroup}>
                        <h1 className={styles.title}>{title}</h1>
                        <div className={styles.subtitle}>
                            for <strong>{patientName}</strong>
                            {allergies.length > 0 && (
                                <span className={styles.allergyBadge}>
                                    <AlertTriangle className="w-3 h-3" />
                                    {allergies.join(', ')}
                                </span>
                            )}
                        </div>
                    </div>
                </div>
                <button
                    onClick={onSave}
                    disabled={isSaving}
                    className={styles.headerSaveButton}
                >
                    <Check className="w-4 h-4" />
                    {isSaving ? 'Saving...' : 'Save Note'}
                </button>
            </header>

            {/* Content */}
            <div className={styles.content}>
                {children}
            </div>
        </div>
    );
}

export function NoteSection({ label, children }: { label: string; children: React.ReactNode }) {
    return (
        <section className={styles.section}>
            <label className={styles.label}>{label}</label>
            {children}
        </section>
    );
}

