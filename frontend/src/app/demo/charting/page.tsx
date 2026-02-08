'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import ClinicalNoteLayout, { NoteSection } from '@/components/charting/ClinicalNoteLayout';
import ToothAreaSelector from '@/components/charting/ToothAreaSelector';
import NoteTypeSelector from '@/components/charting/NoteTypeSelector';
import QuickPhraseRail from '@/components/charting/QuickPhraseRail';
import ClinicalNoteEditor from '@/components/charting/ClinicalNoteEditor';
import { NoteType } from '@/types/api';

export default function ChartingDemoPage() {
    const router = useRouter();
    const [toothArea, setToothArea] = useState('');
    const [noteType, setNoteType] = useState<NoteType>('CHIEF_COMPLAINT');
    const [noteContent, setNoteContent] = useState('');

    const handleQuickPhrase = (phrase: string) => {
        setNoteContent((prev) => prev ? `${prev} ${phrase}` : phrase);
    };

    const handleClose = () => {
        router.back();
    };

    const handleSave = () => {
        alert('Demo: Note would be saved here.');
    };

    return (
        <ClinicalNoteLayout
            title="New Clinical Note"
            patientName="Sarah Mitchell"
            allergies={['Penicillin', 'Latex']}
            onClose={handleClose}
            onSave={handleSave}
            isSaving={false}
        >
            <NoteSection label="Tooth / Area (optional)">
                <ToothAreaSelector value={toothArea} onChange={setToothArea} />
            </NoteSection>

            <NoteSection label="Note Type">
                <NoteTypeSelector selectedType={noteType} onSelect={setNoteType} />
            </NoteSection>

            <NoteSection label="Clinical Note">
                <ClinicalNoteEditor value={noteContent} onChange={setNoteContent} />
            </NoteSection>

            <NoteSection label="Quick Phrases">
                <QuickPhraseRail onPhraseSelect={handleQuickPhrase} />
            </NoteSection>
        </ClinicalNoteLayout>
    );
}

