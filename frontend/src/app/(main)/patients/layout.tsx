'use client';

import React, { useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import ListPanel from '@/components/layout/ListPanel';
import PatientSearch from '@/components/patients/PatientSearch';
import PatientCard from '@/components/patients/PatientCard';
import AddPatientModal from '@/components/patients/AddPatientModal';
import { usePatients } from '@/lib/hooks/usePatients';
import { searchPatients } from '@/lib/api/patients';
import type { PatientResponse } from '@/types/api';

export default function PatientsLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const router = useRouter();
    const params = useParams();
    const selectedPatientId = params?.patientId as string | undefined;

    // State
    const [searchResults, setSearchResults] = useState<PatientResponse[] | null>(null);
    const [isSearching, setIsSearching] = useState(false);
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);

    // Data - Default list (recent/all)
    const { patients: allPatients, isLoading, mutate } = usePatients({ limit: 50 });

    // Handlers
    const handleSearch = async (query: string) => {
        if (!query) {
            setSearchResults(null);
            return;
        }

        setIsSearching(true);
        try {
            const results = await searchPatients(query);
            setSearchResults(results);
        } catch (error) {
            console.error('Search failed', error);
            setSearchResults([]);
        } finally {
            setIsSearching(false);
        }
    };

    const handleSelectPatient = (patient: PatientResponse) => {
        router.push(`/patients/${patient.id}`);
    };

    const handleCreatePatient = () => {
        setIsAddModalOpen(true);
    };

    const handlePatientCreated = () => {
        mutate();
        // Close modal handled by prop/state
        setIsAddModalOpen(false);
    };

    // Determine list to show
    const displayList = searchResults || allPatients || [];

    return (
        <>
            <ListPanel
                title="Patients"
                action={null}
            >
                <PatientSearch
                    onSearch={handleSearch}
                    onAddPatient={handleCreatePatient}
                />

                {isLoading && !searchResults ? (
                    <div className="flex justify-center p-8">
                        <div className="w-6 h-6 border-2 border-slate-200 border-t-blue-600 rounded-full animate-spin" />
                    </div>
                ) : (
                    <div className="flex flex-col">
                        {displayList.length === 0 ? (
                            <div className="p-8 text-center text-slate-500">
                                {searchResults !== null
                                    ? "No patients found matching your search."
                                    : "No patients yet."}
                            </div>
                        ) : (
                            displayList.map(patient => (
                                <PatientCard
                                    key={patient.id}
                                    patient={patient}
                                    isSelected={selectedPatientId === patient.id}
                                    onClick={() => handleSelectPatient(patient)}
                                />
                            ))
                        )}
                    </div>
                )}
            </ListPanel>

            {/* This renders the page.tsx (Empty State) or [patientId]/page.tsx (Detail) */}
            {children}

            <AddPatientModal
                isOpen={isAddModalOpen}
                onClose={() => setIsAddModalOpen(false)}
                onPatientCreated={handlePatientCreated}
            />
        </>
    );
}
