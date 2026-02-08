'use client';

import React from 'react';
import { formatTime } from '@/lib/utils/dates';
import type { ScheduleEntry } from '@/types/api';
import styles from './ScheduleList.module.css';

interface ScheduleListProps {
    visits: ScheduleEntry[];
    selectedVisitId?: string | null;
    onSelectVisit: (visit: ScheduleEntry) => void;
    isLoading?: boolean;
}

export default function ScheduleList({
    visits,
    selectedVisitId,
    onSelectVisit,
    isLoading
}: ScheduleListProps) {

    if (isLoading) {
        return (
            <div className="flex justify-center p-8">
                <div className="w-6 h-6 border-2 border-slate-200 border-t-blue-600 rounded-full animate-spin" />
            </div>
        );
    }

    if (visits.length === 0) {
        return (
            <div className="p-6 text-center text-slate-500">
                <p>No appointments scheduled for this day.</p>
            </div>
        );
    }

    return (
        <ul className={styles.list}>
            {visits.map((visit) => {
                const isSelected = selectedVisitId === visit.id;
                const patientName = visit.patient
                    ? `${visit.patient.first_name} ${visit.patient.last_name}`
                    : 'Unknown Patient';

                return (
                    <li
                        key={visit.id}
                        className={`${styles.item} ${isSelected ? styles.selected : ''}`}
                        onClick={() => onSelectVisit(visit)}
                    >
                        <div className={styles.timeColumn}>
                            <span className={styles.time}>{formatTime(visit.visit_date)}</span>
                            <span className={`${styles.status} ${styles[visit.status.toLowerCase()]}`} />
                        </div>

                        <div className={styles.infoColumn}>
                            <h3 className={styles.patientName}>{patientName}</h3>
                            <p className={styles.reason}>{visit.reason || 'No reason specified'}</p>
                        </div>
                    </li>
                );
            })}
        </ul>
    );
}
