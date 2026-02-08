'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { Save, Plus } from 'lucide-react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import NoteTypeSelector from '@/components/charting/NoteTypeSelector';
import Input from '@/components/ui/Input';
import { useVisit } from '@/lib/hooks/useVisits';
import { usePatient } from '@/lib/hooks/usePatients';
import type { NoteType } from '@/types/api';

// Temporary hook placement until file created
import useSWRMutation from 'swr/mutation';
import { createNote } from '@/lib/api/notes';

// Hook implementation
function useCreateNote() {
    return useSWRMutation('notes', (_, { arg }: { arg: any }) => createNote(arg));
}


export default function ChartingPage({ params }: { params: { visitId: string } }) {
    const router = useRouter();
    const { visit, isLoading: visitLoading } = useVisit(params.visitId); // This hook needs to be verified
    const { patient, isLoading: patientLoading } = usePatient(visit?.patient_id || null);
    const { trigger: saveNote, isMutating } = useCreateNote();

    const [noteType, setNoteType] = useState<NoteType>('FINDING');
    const [content, setContent] = useState('');
    const [tooth, setTooth] = useState('');
    const [surfaces, setSurfaces] = useState('');

    // Note: For MVP we use simple state processing. 
    // Real app would use React Hook Form for full validation.

    const handleClose = () => {
        if (content && !confirm('Discard unsaved changes?')) return;
        router.back();
    };

    const handleSave = async (saveAndNew: boolean = false) => {
        if (!content.trim()) return;

        try {
            await saveNote({
                patient_id: visit!.patient_id,
                visit_id: visit!.id,
                author_id: 'current-user-id', // TODO: Get from AuthContext
                note_type: noteType,
                content: content,
                tooth_number: tooth,
                surface_ids: surfaces,
            });

            if (saveAndNew) {
                setContent('');
                // Keep same visit/patient context
            } else {
                router.back();
            }
        } catch (error) {
            console.error('Failed to save note', error);
            alert('Failed to save note. Please try again.');
        }
    };

    const isLoading = visitLoading || patientLoading;

    if (isLoading) return null; // Modal will just not show yet

    return (
        <Modal
            isOpen={true}
            onClose={handleClose}
            title={`Charting for ${patient?.first_name} ${patient?.last_name}`}
            size="full"
            footer={
                <>
                    <span className="text-sm text-slate-500 mr-auto">
                        {visit?.visit_date ? new Date(visit.visit_date).toLocaleDateString() : ''}
                    </span>
                    <Button variant="ghost" onClick={handleClose}>Cancel</Button>
                    <Button variant="secondary" onClick={() => handleSave(true)} isLoading={isMutating}>
                        Save & New
                    </Button>
                    <Button variant="primary" onClick={() => handleSave(false)} isLoading={isMutating} leftIcon={<Save className="w-4 h-4" />}>
                        Save Note
                    </Button>
                </>
            }
        >
            <div className="max-w-4xl mx-auto space-y-6">
                {/* Note Type Selection */}
                <section>
                    <h3 className="text-sm font-medium text-slate-700 mb-2">Note Type</h3>
                    <NoteTypeSelector
                        selectedType={noteType}
                        onSelect={setNoteType}
                    />
                </section>

                {/* Tooth / Area Input */}
                <div className="grid grid-cols-2 gap-4">
                    <Input
                        label="Tooth #"
                        placeholder="e.g. 18"
                        value={tooth}
                        onChange={e => setTooth(e.target.value)}
                    />
                    <Input
                        label="Surfaces"
                        placeholder="e.g. MOD"
                        value={surfaces}
                        onChange={e => setSurfaces(e.target.value)}
                    />
                </div>

                {/* Main Note Input */}
                <section>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Clinical Note</label>
                    <textarea
                        className="w-full h-64 p-4 text-lg border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                        placeholder="Start typing or use quick phrases..."
                        value={content}
                        onChange={e => setContent(e.target.value)}
                        autoFocus
                    />
                </section>

                {/* Quick Phrases (Placeholder) */}
                <section>
                    <h3 className="text-sm font-medium text-slate-700 mb-2">Quick Phrases</h3>
                    <div className="flex flex-wrap gap-2">
                        <button className="px-3 py-1 bg-slate-100 border border-slate-200 rounded-md text-sm hover:bg-slate-200" onClick={() => setContent(c => c + "Patient presented with ")}>
                            + Patient presented
                        </button>
                        <button className="px-3 py-1 bg-slate-100 border border-slate-200 rounded-md text-sm hover:bg-slate-200" onClick={() => setContent(c => c + "No significant findings. ")}>
                            + No findings
                        </button>
                        <button className="px-3 py-1 bg-slate-100 border border-slate-200 rounded-md text-sm hover:bg-slate-200" onClick={() => setContent(c => c + "Discussed treatment plan. ")}>
                            + Discussed Plan
                        </button>
                    </div>
                </section>
            </div>
        </Modal>
    );
}
