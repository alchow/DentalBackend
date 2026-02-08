'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { usePatient } from '@/lib/hooks/usePatients';
import ClinicalNoteLayout, { NoteSection } from '@/components/charting/ClinicalNoteLayout';
import ToothAreaSelector from '@/components/charting/ToothAreaSelector';
import NoteTypeSelector from '@/components/charting/NoteTypeSelector';
import QuickPhraseRail from '@/components/charting/QuickPhraseRail';
import ClinicalNoteEditor from '@/components/charting/ClinicalNoteEditor';
import { NoteType } from '@/types/api';
import { createNote } from '@/lib/api/notes';
import { Check } from 'lucide-react';
import styles from '@/components/charting/ClinicalNoteLayout.module.css';

export default function NewClinicalNotePage({ params }: { params: Promise<{ patientId: string }> }) {
    const router = useRouter();
    const { patientId } = React.use(params);
    const { patient, isLoading, error } = usePatient(patientId);

    const [toothArea, setToothArea] = useState('');
    const [noteType, setNoteType] = useState<NoteType>('CHIEF_COMPLAINT');
    const [noteContent, setNoteContent] = useState('');
    const [isSaving, setIsSaving] = useState(false);

    const handleQuickPhrase = (phrase: string) => {
        setNoteContent((prev) => prev ? `${prev} ${phrase}` : phrase);
    };

    const handleClose = () => {
        router.back();
    };

    const handleSave = async () => {
        if (!noteContent.trim()) {
            alert('Please enter a clinical note.');
            return;
        }

        setIsSaving(true);
        try {
            await createNote({
                patient_id: patientId,
                content: noteContent,
                note_type: noteType,
                tooth_number: toothArea,
                area_of_oral_cavity: toothArea,
                author_id: '00000000-0000-0000-0000-000000000000',
            });
            router.push(`/patients/${patientId}`);
        } catch (err) {
            console.error(err);
            alert('Failed to save note. Please try again.');
        } finally {
            setIsSaving(false);
        }
    };

    if (isLoading) {
        return (
            <div className="fixed inset-0 z-50 bg-white flex items-center justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-2 border-slate-300 border-t-teal-600" />
            </div>
        );
    }

    if (error || !patient) {
        return (
            <div className="fixed inset-0 z-50 bg-white flex items-center justify-center">
                <div className="text-center text-red-500">
                    <p className="font-semibold">Patient not found.</p>
                    <button onClick={handleClose} className="mt-4 text-blue-600 underline">Go Back</button>
                </div>
            </div>
        );
    }

    // Extract allergies from patient medical history
    const allergies = patient.medical_history?.allergies || [];

    return (
        <ClinicalNoteLayout
            title="New Clinical Note"
            patientName={`${patient.first_name} ${patient.last_name}`}
            allergies={allergies}
            onClose={handleClose}
            onSave={handleSave}
            isSaving={isSaving}
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

            {/* Footer */}
            <div className={styles.footer}>
                <button
                    onClick={handleClose}
                    disabled={isSaving}
                    className={styles.cancelButton}
                >
                    Cancel
                </button>
                <button
                    onClick={handleSave}
                    disabled={isSaving}
                    className={styles.saveButton}
                >
                    <Check className="w-5 h-5" />
                    Save Note
                </button>
            </div>
        </ClinicalNoteLayout>
    );
}

