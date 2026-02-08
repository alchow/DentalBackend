'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { usePatient } from '@/lib/hooks/usePatients';
import DetailPanel from '@/components/layout/DetailPanel';
import Button from '@/components/ui/Button';
import { formatDobWithAge } from '@/lib/utils/dates';
import { ArrowLeft, Edit, PlusCircle } from 'lucide-react';

// New Components
import ItemsToAddressCard from '@/components/patients/ItemsToAddressCard';
import LastVisitCard from '@/components/patients/LastVisitCard';
import PatientInfoCard from '@/components/patients/PatientInfoCard';

export default function PatientDetailPage({ params }: { params: Promise<{ patientId: string }> }) {
    const router = useRouter();
    const { patientId } = React.use(params);
    const { patient, isLoading, error } = usePatient(patientId);

    // Loading State
    if (isLoading) {
        return (
            <DetailPanel title="Loading...">
                <div className="flex flex-col gap-6 animate-pulse">
                    <div className="h-48 bg-slate-100 rounded-xl"></div>
                    <div className="h-64 bg-slate-100 rounded-xl"></div>
                    <div className="h-64 bg-slate-100 rounded-xl"></div>
                </div>
            </DetailPanel>
        );
    }

    // Error State
    if (error || !patient) {
        return (
            <DetailPanel title="Error">
                <div className="p-8 text-center text-red-500 bg-red-50 rounded-xl border border-red-100">
                    <p className="font-semibold">Patient not found or access denied.</p>
                    <p className="text-sm mt-2 text-red-400">Please check the patient ID or try searching again.</p>
                    <div className="mt-6">
                        <Button onClick={() => router.back()} variant="secondary">Go Back</Button>
                    </div>
                </div>
            </DetailPanel>
        );
    }

    // Action Buttons
    const actions = (
        <div className="flex gap-2">
            <Button variant="ghost" size="sm" onClick={() => router.back()} className="lg:hidden">
                <ArrowLeft className="w-4 h-4" />
            </Button>
            <Button variant="secondary" size="sm" leftIcon={<Edit className="w-4 h-4" />}>
                Edit Profile
            </Button>
            <Button
                variant="primary"
                size="sm"
                leftIcon={<PlusCircle className="w-4 h-4" />}
                onClick={() => router.push(`/patients/${patientId}/notes/new`)}
            >
                Add Note
            </Button>
        </div>
    );

    return (
        <DetailPanel
            title={`${patient.first_name} ${patient.last_name}`}
            subtitle={formatDobWithAge(patient.dob)}
            actions={actions}
        >
            <div className="space-y-6 max-w-3xl mx-auto lg:mx-0 lg:max-w-none">
                {/* 1. Items to Address (Top) */}
                <ItemsToAddressCard patientId={patient.id} />

                {/* 2. Last Visit Summary (Middle) */}
                <LastVisitCard patientId={patient.id} />

                {/* 3. Patient Info (Bottom) */}
                <PatientInfoCard patient={patient} />
            </div>
        </DetailPanel>
    );
}
