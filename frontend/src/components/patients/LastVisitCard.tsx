'use client';

import React from 'react';
import { usePatientVisits } from '@/lib/hooks/useVisits';
import { FileText, Stethoscope, ClipboardList } from 'lucide-react';
import { format } from 'date-fns';

import { useRouter } from 'next/navigation';

interface LastVisitCardProps {
    patientId: string;
}

export default function LastVisitCard({ patientId }: LastVisitCardProps) {
    const router = useRouter();
    const { visits, isLoading } = usePatientVisits(patientId);

    // Get most recent COMPLETED visit
    const lastVisit = visits
        ?.filter(v => v.status === 'COMPLETED')
        .sort((a, b) => new Date(b.visit_date).getTime() - new Date(a.visit_date).getTime())[0];

    const visitDate = lastVisit ? new Date(lastVisit.visit_date) : null;

    // Placeholder logic per User Decision
    // If summary is missing, show placeholder content
    const summary = lastVisit?.summary as any || {};
    const chiefComplaint = summary.chief_complaint || lastVisit?.reason || "Sensitivity lower right (Placeholder)";
    const procedures = summary.procedures || "D2391 - Composite #30 MO (Placeholder)";
    const clinicalNotes = summary.clinical_notes || "Patient presented with cold sensitivity. Examined and noted decay. Proceeded with restoration. (AI Summary Generation Pending...)";

    if (isLoading) {
        return (
            <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100 animate-pulse h-64">
                <div className="flex justify-between mb-6">
                    <div className="h-6 bg-slate-100 rounded w-1/3"></div>
                    <div className="h-6 bg-slate-100 rounded w-1/4"></div>
                </div>
                <div className="space-y-4">
                    <div className="h-4 bg-slate-100 rounded w-full"></div>
                    <div className="h-4 bg-slate-100 rounded w-full"></div>
                    <div className="h-4 bg-slate-100 rounded w-3/4"></div>
                </div>
            </div>
        );
    }

    if (!lastVisit) {
        return (
            <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
                <div className="text-center text-slate-500 py-8">
                    <p>No previous visits found.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <header className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-slate-900">Last Visit Summary</h3>
                <span className="text-slate-500 font-medium">
                    {visitDate && format(visitDate, 'MMM d, yyyy')}
                </span>
            </header>

            <div className="space-y-6">
                {/* Chief Complaint */}
                <div className="flex gap-4">
                    <div className="bg-slate-50 p-2 rounded-lg h-fit">
                        <Stethoscope className="w-5 h-5 text-slate-400" />
                    </div>
                    <div>
                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">
                            Chief Complaint
                        </h4>
                        <p className="text-slate-900 font-medium">{chiefComplaint}</p>
                    </div>
                </div>

                {/* Procedures */}
                <div className="flex gap-4">
                    <div className="bg-slate-50 p-2 rounded-lg h-fit">
                        <ClipboardList className="w-5 h-5 text-slate-400" />
                    </div>
                    <div>
                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">
                            Procedures
                        </h4>
                        <p className="text-slate-900 font-medium">{procedures}</p>
                    </div>
                </div>

                {/* Clinical Notes */}
                <div className="flex gap-4">
                    <div className="bg-slate-50 p-2 rounded-lg h-fit">
                        <FileText className="w-5 h-5 text-slate-400" />
                    </div>
                    <div>
                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">
                            Clinical Notes
                        </h4>
                        <p className="text-slate-600 text-sm leading-relaxed line-clamp-3">
                            {clinicalNotes}
                        </p>
                    </div>
                </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-100 text-center">
                <button
                    onClick={() => router.push(`/patients/${patientId}/notes`)}
                    className="text-blue-600 font-semibold hover:text-blue-700 text-sm"
                >
                    See Chart History
                </button>
            </div>
        </div>
    );
}
