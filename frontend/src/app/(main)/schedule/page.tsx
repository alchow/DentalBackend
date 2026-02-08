'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Plus, ChevronLeft, ChevronRight, Calendar as CalendarIcon } from 'lucide-react';
import { addDays, subDays } from 'date-fns';

import ListPanel from '@/components/layout/ListPanel';
import DetailPanel from '@/components/layout/DetailPanel';
import ScheduleList from '@/components/visits/ScheduleList';
import Button from '@/components/ui/Button';

import { useSchedule } from '@/lib/hooks/useSchedule';
import { formatDateLong, getTodayString, toISODateString, parseDate, calculateAge } from '@/lib/utils/dates';
import { formatAllergies, hasAllergies } from '@/lib/utils/medicalHistory';
import type { ScheduleEntry } from '@/types/api';

export default function SchedulePage() {
    const router = useRouter();

    // State
    const [selectedDate, setSelectedDate] = useState<string>(getTodayString());
    const [selectedVisit, setSelectedVisit] = useState<ScheduleEntry | null>(null);

    // Data Fetching
    const { schedule, isLoading, error } = useSchedule(selectedDate);

    // Date Navigation Handlers
    const handlePrevDay = () => {
        const date = parseDate(selectedDate);
        setSelectedDate(toISODateString(subDays(date, 1)));
        setSelectedVisit(null);
    };

    const handleNextDay = () => {
        const date = parseDate(selectedDate);
        setSelectedDate(toISODateString(addDays(date, 1)));
        setSelectedVisit(null);
    };

    const handleToday = () => {
        setSelectedDate(getTodayString());
        setSelectedVisit(null);
    };

    // Selection Handler
    const handleSelectVisit = (visit: ScheduleEntry) => {
        setSelectedVisit(visit);
        // In a real app, we might update the URL here for deep linking
        // router.push(`/schedule?date=${selectedDate}&visitId=${visit.id}`, { scroll: false });
    };

    // Render Helpers
    const renderDetailPanel = () => {
        if (!selectedVisit) {
            return (
                <DetailPanel title="">
                    <div className="flex flex-col items-center justify-center h-full text-slate-400">
                        <CalendarIcon className="w-16 h-16 mb-4 opacity-20" />
                        <p className="text-lg font-medium">Select an appointment</p>
                        <p className="text-sm">View patient details and start charting</p>
                    </div>
                </DetailPanel>
            );
        }

        const { patient, status, reason } = selectedVisit;

        if (!patient) return null; // Should not happen given types

        const age = calculateAge(patient.dob);
        const patientSubtitle = `${age} years`;

        // Panel Actions
        const actions = (
            <div className="flex gap-2">
                <Button variant="secondary" size="sm">History</Button>
                <Button
                    variant="primary"
                    size="sm"
                    onClick={() => router.push(`/charting/${selectedVisit.id}`)}
                >
                    {status === 'IN_PROGRESS' ? 'Resume Charting' : 'Start Charting'}
                </Button>
            </div>
        );

        return (
            <DetailPanel
                title={`${patient.first_name} ${patient.last_name}`}
                subtitle={patientSubtitle}
                actions={actions}
            >
                <div className="space-y-6">
                    {/* Visit Context Card */}
                    <div className="p-4 bg-blue-50 border border-blue-100 rounded-lg">
                        <h3 className="text-sm font-semibold text-blue-900 uppercase tracking-wide mb-2">
                            Current Visit
                        </h3>
                        <p className="text-blue-800 font-medium">{reason || 'Routine Checkup'}</p>
                        <div className="mt-2 flex gap-2">
                            <span className="text-xs px-2 py-1 bg-white rounded border border-blue-200 text-blue-700">
                                {status.replace('_', ' ')}
                            </span>
                        </div>
                    </div>

                    {/* Medical Alerts */}
                    {hasAllergies(patient.medical_history) && (
                        <div className="p-4 bg-red-50 border border-red-100 rounded-lg">
                            <h3 className="text-sm font-semibold text-red-900 uppercase tracking-wide mb-2">
                                Medical Alerts
                            </h3>
                            <div className="flex flex-wrap gap-2">
                                {formatAllergies(patient.medical_history).split(', ').map(allergy => (
                                    <span key={allergy} className="px-2 py-1 bg-white border border-red-200 text-red-700 text-sm font-medium rounded-full">
                                        {allergy}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Contact Info */}
                    <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
                        <div className="px-4 py-3 bg-slate-50 border-bottom border-slate-200">
                            <h3 className="font-medium text-slate-700">Contact Information</h3>
                        </div>
                        <div className="p-4 space-y-3 text-sm">
                            <div className="grid grid-cols-3 gap-2">
                                <span className="text-slate-500">Phone</span>
                                <span className="col-span-2">{patient.contact_info?.phone || '--'}</span>
                            </div>
                            <div className="grid grid-cols-3 gap-2">
                                <span className="text-slate-500">Email</span>
                                <span className="col-span-2">{patient.contact_info?.email || '--'}</span>
                            </div>
                        </div>
                    </div>

                    {/* Notes Preview (Placeholder) */}
                    <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
                        <div className="px-4 py-3 bg-slate-50 border-bottom border-slate-200 flex justify-between items-center">
                            <h3 className="font-medium text-slate-700">Recent Notes</h3>
                            <Button variant="ghost" size="sm">View All</Button>
                        </div>
                        <div className="p-8 text-center text-slate-400 text-sm">
                            No previous notes found
                        </div>
                    </div>

                </div>
            </DetailPanel>
        );
    };

    return (
        <>
            <ListPanel
                title={formatDateLong(selectedDate)}
                action={
                    <div className="flex gap-1">
                        <Button variant="ghost" size="sm" onClick={handlePrevDay}><ChevronLeft className="w-4 h-4" /></Button>
                        <Button variant="ghost" size="sm" onClick={handleToday}>Today</Button>
                        <Button variant="ghost" size="sm" onClick={handleNextDay}><ChevronRight className="w-4 h-4" /></Button>
                    </div>
                }
            >
                <div className="p-2">
                    {error ? (
                        <div className="p-4 text-center text-red-500">
                            Failed to load schedule. Please try again.
                        </div>
                    ) : (
                        <ScheduleList
                            visits={schedule || []}
                            isLoading={isLoading}
                            selectedVisitId={selectedVisit?.id}
                            onSelectVisit={handleSelectVisit}
                        />
                    )}
                </div>

                {/* Floating Action Button for New Appointment (Future feature) */}
                {/* <div className="absolute bottom-4 right-4">
          <Button variant="primary" size="lg" className="rounded-full shadow-lg w-12 h-12 p-0">
            <Plus className="w-6 h-6" />
          </Button>
        </div> */}
            </ListPanel>

            {renderDetailPanel()}
        </>
    );
}
