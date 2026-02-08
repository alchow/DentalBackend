'use client';

import React from 'react';
import { NoteType } from '@/types/api';
import styles from './NoteTypeSelector.module.css';

interface NoteTypeSelectorProps {
    selectedType: string;
    onSelect: (type: NoteType) => void;
    disabled?: boolean;
}

const noteTypes: { id: NoteType; label: string; colorClass: string }[] = [
    { id: 'CHIEF_COMPLAINT', label: 'Chief Complaint', colorClass: 'complaint' },
    { id: 'FINDING', label: 'Finding', colorClass: 'finding' },
    { id: 'TREATMENT', label: 'Treatment', colorClass: 'treatment' },
    { id: 'PATIENT_CONCERN', label: 'Patient Concern', colorClass: 'concern' },
    { id: 'FOLLOW_UP', label: 'Follow Up', colorClass: 'followup' },
    { id: 'PHONE_CALL', label: 'Phone Call', colorClass: 'phone' },
    { id: 'LAB_COMMUNICATION', label: 'Lab', colorClass: 'lab' },
];

export default function NoteTypeSelector({ selectedType, onSelect, disabled }: NoteTypeSelectorProps) {
    return (
        <div className={styles.container}>
            {noteTypes.map((type) => (
                <button
                    key={type.id}
                    type="button"
                    disabled={disabled}
                    onClick={() => onSelect(type.id)}
                    className={`
            ${styles.chip} 
            ${styles[type.colorClass]} 
            ${selectedType === type.id ? styles.selected : ''}
          `}
                >
                    {type.label}
                </button>
            ))}
        </div>
    );
}
