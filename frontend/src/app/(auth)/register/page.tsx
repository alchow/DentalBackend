'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/contexts/AuthContext';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Lock, Mail, User, Building } from 'lucide-react';

export default function RegisterPage() {
    const router = useRouter();
    const { register, error: authError } = useAuth();

    const [formData, setFormData] = useState({
        fullName: '',
        email: '',
        password: '',
        confirmPassword: '',
        practiceName: '',
        address: '',
    });

    const [formErrors, setFormErrors] = useState({
        fullName: '',
        email: '',
        password: '',
        confirmPassword: '',
        practiceName: '',
    });

    const [isSubmitting, setIsSubmitting] = useState(false);

    const validateForm = () => {
        let isValid = true;
        const errors = {
            fullName: '',
            email: '',
            password: '',
            confirmPassword: '',
            practiceName: '',
        };

        if (!formData.fullName) {
            errors.fullName = 'Full name is required';
            isValid = false;
        }

        if (!formData.email) {
            errors.email = 'Email is required';
            isValid = false;
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            errors.email = 'Invalid email address';
            isValid = false;
        }

        if (!formData.password) {
            errors.password = 'Password is required';
            isValid = false;
        } else if (formData.password.length < 8) {
            errors.password = 'Password must be at least 8 characters';
            isValid = false;
        }

        if (formData.password !== formData.confirmPassword) {
            errors.confirmPassword = 'Passwords do not match';
            isValid = false;
        }

        if (!formData.practiceName) {
            errors.practiceName = 'Practice name is required';
            isValid = false;
        }

        setFormErrors(errors);
        return isValid;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!validateForm()) return;

        setIsSubmitting(true);

        try {
            await register({
                user: {
                    email: formData.email,
                    password: formData.password,
                    full_name: formData.fullName,
                },
                office: {
                    name: formData.practiceName,
                    address: formData.address,
                },
            });
            router.push('/schedule');
        } catch (error) {
            console.error('Registration failed:', error);
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        if (formErrors[name as keyof typeof formErrors]) {
            setFormErrors(prev => ({ ...prev, [name]: '' }));
        }
    };

    return (
        <div className="w-full max-w-md mx-auto p-6 bg-white rounded-xl shadow-lg border border-slate-200">
            <div className="text-center mb-8">
                <h1 className="text-2xl font-bold text-slate-900">Create your account</h1>
                <p className="mt-2 text-sm text-slate-600">
                    Already have an account?{' '}
                    <Link href="/login" className="font-medium text-blue-600 hover:text-blue-500">
                        Sign in
                    </Link>
                </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                {authError && (
                    <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
                        {authError}
                    </div>
                )}

                <div className="space-y-4">
                    <Input
                        id="fullName"
                        name="fullName"
                        type="text"
                        label="Full Name"
                        placeholder="Dr. Jane Smith"
                        autoComplete="name"
                        required
                        value={formData.fullName}
                        onChange={handleChange}
                        error={formErrors.fullName}
                        leftIcon={<User className="w-5 h-5" />}
                    />

                    <Input
                        id="practiceName"
                        name="practiceName"
                        type="text"
                        label="Practice Name"
                        placeholder="Smith Dental Care"
                        required
                        value={formData.practiceName}
                        onChange={handleChange}
                        error={formErrors.practiceName}
                        leftIcon={<Building className="w-5 h-5" />}
                    />

                    <Input
                        id="email"
                        name="email"
                        type="email"
                        label="Email address"
                        placeholder="dentist@example.com"
                        autoComplete="email"
                        required
                        value={formData.email}
                        onChange={handleChange}
                        error={formErrors.email}
                        leftIcon={<Mail className="w-5 h-5" />}
                    />

                    <Input
                        id="password"
                        name="password"
                        type="password"
                        label="Password"
                        autoComplete="new-password"
                        required
                        value={formData.password}
                        onChange={handleChange}
                        error={formErrors.password}
                        leftIcon={<Lock className="w-5 h-5" />}
                    />

                    <Input
                        id="confirmPassword"
                        name="confirmPassword"
                        type="password"
                        label="Confirm Password"
                        autoComplete="new-password"
                        required
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        error={formErrors.confirmPassword}
                        leftIcon={<Lock className="w-5 h-5" />}
                    />
                </div>

                <Button
                    type="submit"
                    variant="primary"
                    size="lg"
                    className="w-full"
                    isLoading={isSubmitting}
                >
                    Create Account
                </Button>
            </form>
        </div>
    );
}
