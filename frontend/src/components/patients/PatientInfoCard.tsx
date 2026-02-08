'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import type { PatientResponse } from '@/types/api';
import { calculateAge, formatDate } from '@/lib/utils/dates';
import { Mail, Calendar, Pill, AlertTriangle, FileText } from 'lucide-react';
import { format } from 'date-fns';

interface PatientInfoCardProps {
    patient: PatientResponse;
}

export default function PatientInfoCard({ patient }: PatientInfoCardProps) {
    const router = useRouter();
    const age = calculateAge(patient.dob);
    const dob = formatDate(patient.dob);

    // Safety check for medical history
    const allergies = patient.medical_history?.allergies || [];
    const medications = patient.medical_history?.medications || [];

    // Helper to format list
    const formatList = (items: string[]) => items.length > 0 ? items.join(', ') : 'None known';

    return (
        <div className="bg-gradient-to-br from-teal-500 to-teal-600 rounded-xl p-6 shadow-sm text-white">
            <div className="flex items-start justify-between mb-6">
                <div className="flex gap-4">
                    <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center text-xl font-bold backdrop-blur-sm">
                        {patient.first_name[0]}{patient.last_name[0]}
                    </div>
                    <div>
                        <h2 className="text-xl font-bold flex items-center gap-2">
                            {patient.first_name} {patient.last_name}
                            {/* Risk Badge - Skipped per MVP Decision */}
                        </h2>
                        <p className="text-teal-100 text-sm font-medium mt-0.5">
                            {age}yo • DOB {dob} • Delta Dental PPO
                        </p>
                    </div>
                </div>
            </div>

            <div className="space-y-3">
                {/* Allergies - Red Pill */}
                <div className="bg-red-500/20 border border-red-400/30 rounded-full px-4 py-2 flex items-center gap-3 backdrop-blur-sm">
                    <AlertTriangle className="w-4 h-4 text-red-200 shrink-0" />
                    <div className="flex gap-2 text-sm overflow-hidden">
                        <span className="font-bold text-red-100 uppercase tracking-wider text-xs pt-0.5">Allergies:</span>
                        <span className="text-white truncate font-medium">{formatList(allergies)}</span>
                    </div>
                </div>

                {/* Medications - Blue Pill */}
                <div className="bg-blue-500/20 border border-blue-400/30 rounded-full px-4 py-2 flex items-center gap-3 backdrop-blur-sm">
                    <Pill className="w-4 h-4 text-blue-200 shrink-0" />
                    <div className="flex gap-2 text-sm overflow-hidden">
                        <span className="font-bold text-blue-100 uppercase tracking-wider text-xs pt-0.5">Medications:</span>
                        <span className="text-white truncate font-medium">{formatList(medications)}</span>
                    </div>
                </div>
            </div>

            <div className="mt-6 pt-4 border-t border-white/10 flex justify-between items-center text-sm text-teal-100">
                <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    <span>Last visit: Dec 14, 2024</span>
                </div>
                <div className="flex items-center gap-2">
                    <Mail className="w-4 h-4" />
                    <span>Prefers: Sms</span>
                </div>
            </div>

            <div className="mt-4 text-center">
                <button
                    onClick={() => router.push(`/patients/${patient.id}/notes`)}
                    className="w-full bg-white/10 hover:bg-white/20 transition-colors py-2 rounded-lg font-medium text-sm flex items-center justify-center gap-2"
                >
                    <FileText className="w-4 h-4" />
                    See Chart History
                </button>
            </div>
        </div>
    );
}

