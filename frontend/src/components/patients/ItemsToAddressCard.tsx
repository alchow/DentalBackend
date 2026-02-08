'use client';

import React from 'react';
import { usePatientTasks } from '@/lib/hooks/useTasks';
import { CheckCircle2, Circle, AlertCircle } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

import { useRouter } from 'next/navigation';

interface ItemsToAddressCardProps {
    patientId: string;
}

export default function ItemsToAddressCard({ patientId }: ItemsToAddressCardProps) {
    const router = useRouter();
    const { tasks, isLoading } = usePatientTasks(patientId);

    // Filter pending tasks
    const pendingTasks = tasks?.filter(t => t.status === 'PENDING') || [];
    const displayTasks = pendingTasks.slice(0, 3);
    const hasMore = pendingTasks.length > 3;

    if (isLoading) {
        return (
            <div className="bg-amber-50 rounded-xl p-6 shadow-sm border border-amber-100 animate-pulse h-48">
                <div className="h-6 bg-amber-200/50 rounded w-1/2 mb-4"></div>
                <div className="space-y-3">
                    <div className="h-4 bg-amber-200/30 rounded w-full"></div>
                    <div className="h-4 bg-amber-200/30 rounded w-3/4"></div>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-amber-50 rounded-xl p-6 shadow-sm border border-amber-100">
            <header className="flex items-center gap-2 mb-4">
                <AlertCircle className="w-5 h-5 text-amber-600" />
                <h3 className="text-lg font-semibold text-amber-900">Items to Address Today</h3>
            </header>

            <div className="space-y-3">
                {displayTasks.length === 0 ? (
                    <p className="text-amber-800/60 italic text-sm">No pending items.</p>
                ) : (
                    displayTasks.map(task => (
                        <div key={task.id} className="flex items-start gap-3">
                            <Circle className="w-5 h-5 text-amber-500 mt-0.5 shrink-0" />
                            <div>
                                <p className="text-amber-900 font-medium leading-tight">
                                    {task.description}
                                </p>
                                <p className="text-xs text-amber-700 mt-0.5">
                                    Added {formatDistanceToNow(new Date(task.created_at), { addSuffix: true })}
                                </p>
                            </div>
                        </div>
                    ))
                )}
            </div>

            <div className="mt-4 pt-3 border-t border-amber-200/50 flex justify-between items-center text-sm">
                <span className="text-amber-700 font-medium">
                    {pendingTasks.length > 0 ? `${pendingTasks.length} Pending` : 'All trapped up'}
                </span>
                <button
                    onClick={() => router.push(`/patients/${patientId}/tasks`)}
                    className="text-amber-800 font-semibold hover:underline"
                >
                    {hasMore ? `See All (${pendingTasks.length})` : 'See Previous Tasks'}
                </button>
            </div>
        </div>
    );
}
