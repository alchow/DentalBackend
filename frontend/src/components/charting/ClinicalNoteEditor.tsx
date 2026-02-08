'use client';

import React from 'react';
import styles from './ClinicalNoteEditor.module.css';

interface ClinicalNoteEditorProps {
    value: string;
    onChange: (value: string) => void;
}

export default function ClinicalNoteEditor({ value, onChange }: ClinicalNoteEditorProps) {
    return (
        <div className={styles.container}>
            <textarea
                className={styles.textarea}
                placeholder="Enter clinical notes..."
                value={value}
                onChange={(e) => onChange(e.target.value)}
            />
        </div>
    );
}
