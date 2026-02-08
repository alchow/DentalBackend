'use client';

import React from 'react';
import styles from './QuickPhraseRail.module.css';

interface QuickPhraseRailProps {
    onPhraseSelect: (phrase: string) => void;
}

const PHRASES = [
    'No issues noted',
    'Patient tolerated well',
    'Will monitor',
    'Needs follow-up',
    'Discussed with patient',
    'Patient declined',
    'Recommended',
    'Sensitivity to cold',
    'Sensitivity to heat',
    'Bleeding on probing',
    'Good home care'
];

export default function QuickPhraseRail({ onPhraseSelect }: QuickPhraseRailProps) {
    return (
        <div className={styles.container}>
            {PHRASES.map((phrase) => (
                <button
                    key={phrase}
                    type="button"
                    className={styles.chip}
                    onClick={() => onPhraseSelect(phrase)}
                >
                    <span className={styles.icon}>+</span>
                    {phrase}
                </button>
            ))}
        </div>
    );
}
