import React, { useState } from 'react';
import { X } from 'lucide-react';
import Button from '@/components/ui/Button';
import { createPatient } from '@/lib/api/patients';

interface AddPatientModalProps {
    isOpen: boolean;
    onClose: () => void;
    onPatientCreated: () => void;
}

export default function AddPatientModal({ isOpen, onClose, onPatientCreated }: AddPatientModalProps) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Form State
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        dob: '',
        email: '',
        phone: '',
    });

    if (!isOpen) return null;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            // Basic validation
            if (!formData.first_name || !formData.last_name || !formData.dob) {
                setError("First Name, Last Name, and DOB are required.");
                setLoading(false);
                return;
            }

            const payload: any = {
                first_name: formData.first_name,
                last_name: formData.last_name,
                dob: formData.dob,
                contact_info: {}
            };

            if (formData.email) payload.contact_info.email = formData.email;
            if (formData.phone) payload.contact_info.phone = formData.phone;

            await createPatient(payload);

            onPatientCreated();
            onClose();
            // Reset form
            setFormData({ first_name: '', last_name: '', dob: '', email: '', phone: '' });

        } catch (err) {
            console.error(err);
            setError("Failed to create patient. Please check your inputs.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
            <div className="w-full max-w-md bg-white rounded-xl shadow-xl border border-slate-100 overflow-hidden">

                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-slate-100 bg-slate-50/50">
                    <h2 className="text-lg font-semibold text-slate-800">New Patient</h2>
                    <button onClick={onClose} className="p-1 hover:bg-slate-200 rounded-full transition-colors text-slate-500">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Body */}
                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    {error && (
                        <div className="p-3 text-sm text-red-600 bg-red-50 rounded-lg border border-red-100">
                            {error}
                        </div>
                    )}

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1">
                            <label className="text-xs font-medium text-slate-500 uppercase">First Name *</label>
                            <input
                                type="text"
                                required
                                className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all"
                                value={formData.first_name}
                                onChange={e => setFormData({ ...formData, first_name: e.target.value })}
                            />
                        </div>
                        <div className="space-y-1">
                            <label className="text-xs font-medium text-slate-500 uppercase">Last Name *</label>
                            <input
                                type="text"
                                required
                                className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all"
                                value={formData.last_name}
                                onChange={e => setFormData({ ...formData, last_name: e.target.value })}
                            />
                        </div>
                    </div>

                    <div className="space-y-1">
                        <label className="text-xs font-medium text-slate-500 uppercase">Date of Birth *</label>
                        <input
                            type="date"
                            required
                            className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all"
                            value={formData.dob}
                            onChange={e => setFormData({ ...formData, dob: e.target.value })}
                        />
                    </div>

                    <div className="space-y-1">
                        <label className="text-xs font-medium text-slate-500 uppercase">Email (Optional)</label>
                        <input
                            type="email"
                            className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all"
                            value={formData.email}
                            onChange={e => setFormData({ ...formData, email: e.target.value })}
                        />
                    </div>

                    <div className="space-y-1">
                        <label className="text-xs font-medium text-slate-500 uppercase">Phone (Optional)</label>
                        <input
                            type="tel"
                            className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all"
                            value={formData.phone}
                            onChange={e => setFormData({ ...formData, phone: e.target.value })}
                        />
                    </div>

                    <div className="pt-2 flex justify-end gap-2">
                        <Button variant="ghost" onClick={onClose} type="button">Cancel</Button>
                        <Button variant="primary" type="submit" disabled={loading}>
                            {loading ? 'Creating...' : 'Create Patient'}
                        </Button>
                    </div>
                </form>
            </div>
        </div>
    );
}
