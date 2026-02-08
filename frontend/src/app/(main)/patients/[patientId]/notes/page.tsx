'use client';

import React from 'react';
import DetailPanel from '@/components/layout/DetailPanel';
import { usePatientNotes } from '@/lib/hooks/useNotes';
import { format } from 'date-fns';
import { FileText, AlertCircle } from 'lucide-react';

export default function ChartHistoryPage({ params }: { params: Promise<{ patientId: string }> }) {
    const { patientId } = React.use(params);
    const { notes, isLoading } = usePatientNotes(patientId);

    // Sort notes by creation date (most recent first)
    const sortedNotes = notes?.slice().sort((a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    ) || [];

    return (
        <DetailPanel title="Chart History">
            {isLoading ? (
                <div className="space-y-4">
                    {[1, 2, 3].map(i => (
                        <div key={i} className="bg-white rounded-xl p-4 animate-pulse border border-slate-200">
                            <div className="h-5 bg-slate-100 rounded w-1/3 mb-3"></div>
                            <div className="h-4 bg-slate-100 rounded w-full mb-2"></div>
                            <div className="h-4 bg-slate-100 rounded w-2/3"></div>
                        </div>
                    ))}
                </div>
            ) : sortedNotes.length === 0 ? (
                <div className="text-center py-12 text-slate-500">
                    <FileText className="w-12 h-12 mx-auto mb-4 opacity-30" />
                    <p className="font-medium">No chart entries yet</p>
                    <p className="text-sm mt-1">Charts will appear here after you create notes.</p>
                </div>
            ) : (
                <div className="space-y-4">
                    {sortedNotes.map((note) => (
                        <div
                            key={note.id}
                            className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm hover:shadow-md transition-shadow"
                        >
                            <div className="flex items-start justify-between mb-3">
                                <div className="flex items-center gap-3">
                                    <div className="bg-teal-50 p-2 rounded-lg">
                                        <FileText className="w-4 h-4 text-teal-600" />
                                    </div>
                                    <div>
                                        <span className="inline-block px-2 py-0.5 text-xs font-semibold rounded-full bg-slate-100 text-slate-600">
                                            {note.note_type?.replace('_', ' ') || 'Note'}
                                        </span>
                                        {note.tooth_number && (
                                            <span className="ml-2 text-xs text-slate-400">
                                                Tooth/Area: {note.tooth_number}
                                            </span>
                                        )}
                                    </div>
                                </div>
                                <time className="text-sm text-slate-400">
                                    {format(new Date(note.created_at), 'MMM d, yyyy • h:mm a')}
                                </time>
                            </div>
                            <p className="text-slate-700 leading-relaxed">
                                {note.content}
                            </p>
                        </div>
                    ))}
                </div>
            )}
        </DetailPanel>
    );
}
