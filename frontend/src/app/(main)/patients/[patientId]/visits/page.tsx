'use client';

import React from 'react';
import DetailPanel from '@/components/layout/DetailPanel';
import { usePatientVisits } from '@/lib/hooks/useVisits';
import { format } from 'date-fns';
import { FileText, Calendar } from 'lucide-react';

export default function VisitHistoryPage({ params }: { params: Promise<{ patientId: string }> }) {
    const { patientId } = React.use(params);
    const { visits, isLoading } = usePatientVisits(patientId);

    return (
        <DetailPanel title="Visit History">
            {isLoading ? (
                <div className="flex justify-center p-8">
                    <div className="w-6 h-6 border-2 border-slate-200 border-t-blue-600 rounded-full animate-spin" />
                </div>
            ) : (
                <div className="space-y-4">
                    {visits?.length === 0 ? (
                        <p className="text-slate-500 text-center py-8">No visits found.</p>
                    ) : (
                        visits?.map(visit => (
                            <div key={visit.id} className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                                <div className="flex justify-between items-start mb-2">
                                    <div className="flex items-center gap-2">
                                        <Calendar className="w-4 h-4 text-slate-400" />
                                        <span className="font-medium text-slate-900">
                                            {format(new Date(visit.visit_date), 'MMM d, yyyy - h:mm a')}
                                        </span>
                                    </div>
                                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${visit.status === 'COMPLETED' ? 'bg-green-100 text-green-700' :
                                        visit.status === 'SCHEDULED' ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-700'
                                        }`}>
                                        {visit.status}
                                    </span>
                                </div>
                                {visit.reason && <p className="text-sm text-slate-600 mb-2">{visit.reason}</p>}
                                <div className="flex items-center gap-1 text-xs text-blue-600 font-medium cursor-pointer hover:underline">
                                    <FileText className="w-3 h-3" />
                                    View Full Notes
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}
        </DetailPanel>
    );
}
