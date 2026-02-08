'use client';

import React from 'react';
import { UserPlus } from 'lucide-react';
import DetailPanel from '@/components/layout/DetailPanel';

export default function PatientsPage() {
    return (
        <DetailPanel title="Patient Details">
            <div className="flex flex-col items-center justify-center h-full text-slate-400">
                <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mb-4">
                    <UserPlus className="w-8 h-8 text-slate-300" />
                </div>
                <p className="text-lg font-medium">Select a patient</p>
                <p className="text-sm">View medical history, notes, and treatment plan</p>
            </div>
        </DetailPanel>
    );
}
