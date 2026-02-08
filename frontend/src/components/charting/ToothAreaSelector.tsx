'use client';

import React from 'react';
import styles from './ToothAreaSelector.module.css';

interface ToothAreaSelectorProps {
    value: string;
    onChange: (value: string) => void;
}

const QUICK_AREAS = [
    'Upper Right', 'Upper Left', 'Lower Right', 'Lower Left',
    'Full Mouth', 'Upper Anterior', 'Lower Anterior'
];

export default function ToothAreaSelector({ value, onChange }: ToothAreaSelectorProps) {

    const handleChipClick = (area: string) => {
        // Logic: If empty, set. If exists, append with comma.
        if (!value) {
            onChange(area);
        } else {
            // Avoid duplicates for cleanliness
            if (!value.includes(area)) {
                onChange(`${value}, ${area}`);
            }
        }
    };

    return (
        <div className={styles.container}>
            <input
                type="text"
                className={styles.input}
                placeholder='e.g., #14, "lower right quadrant", "full mouth"'
                value={value}
                onChange={(e) => onChange(e.target.value)}
            />
            <div className={styles.chipGrid}>
                {QUICK_AREAS.map((area) => (
                    <button
                        key={area}
                        type="button"
                        className={styles.chip}
                        onClick={() => handleChipClick(area)}
                    >
                        {area}
                    </button>
                ))}
            </div>
        </div>
    );
}
