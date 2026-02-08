'use client';

import React from 'react';
import { User } from 'lucide-react';
import { formatDobWithAge } from '@/lib/utils/dates';
import type { PatientResponse } from '@/types/api';
import styles from './PatientCard.module.css';

interface PatientCardProps {
    patient: PatientResponse;
    isSelected?: boolean;
    onClick?: () => void;
}

export default function PatientCard({ patient, isSelected, onClick }: PatientCardProps) {
    return (
        <div
            className={`${styles.card} ${isSelected ? styles.selected : ''}`}
            onClick={onClick}
        >
            <div className={styles.avatar}>
                <User className="w-5 h-5" />
            </div>

            <div className={styles.info}>
                <h3 className={styles.name}>
                    {patient.first_name} {patient.last_name}
                </h3>
                <p className={styles.meta}>
                    {formatDobWithAge(patient.dob)}
                </p>
                {patient.contact_info?.phone && (
                    <p className={styles.contact}>{patient.contact_info.phone}</p>
                )}
            </div>
        </div>
    );
}
