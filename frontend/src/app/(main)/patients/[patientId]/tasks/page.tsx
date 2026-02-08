'use client';

import React from 'react';
import DetailPanel from '@/components/layout/DetailPanel';
import { usePatientTasks } from '@/lib/hooks/useTasks';
import { CheckCircle2, Circle } from 'lucide-react';

export default function PatientTasksPage({ params }: { params: Promise<{ patientId: string }> }) {
    const { patientId } = React.use(params);
    const { tasks, isLoading } = usePatientTasks(patientId);

    return (
        <DetailPanel title="Patient Tasks">
            {isLoading ? (
                <div className="flex justify-center p-8">
                    <div className="w-6 h-6 border-2 border-slate-200 border-t-blue-600 rounded-full animate-spin" />
                </div>
            ) : (
                <div className="space-y-3">
                    {tasks?.length === 0 ? (
                        <p className="text-slate-500 text-center py-8">No tasks found.</p>
                    ) : (
                        tasks?.map(task => (
                            <div key={task.id} className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm flex items-start gap-3">
                                {task.status === 'COMPLETED' ? (
                                    <CheckCircle2 className="w-5 h-5 text-green-500 mt-0.5" />
                                ) : (
                                    <Circle className="w-5 h-5 text-amber-500 mt-0.5" />
                                )}
                                <div>
                                    <p className={`font-medium ${task.status === 'COMPLETED' ? 'text-slate-500 line-through' : 'text-slate-900'}`}>
                                        {task.description}
                                    </p>
                                    <div className="flex gap-2 text-xs text-slate-500 mt-1">
                                        <span className={`uppercase font-bold ${task.priority === 'HIGH' ? 'text-red-600' : 'text-slate-400'
                                            }`}>{task.priority}</span>
                                        <span>•</span>
                                        <span>{task.status}</span>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}
        </DetailPanel>
    );
}
