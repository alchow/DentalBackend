'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/contexts/AuthContext';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Lock, Mail } from 'lucide-react';

export default function LoginPage() {
    const router = useRouter();
    const { login, error: authError } = useAuth();

    const [formData, setFormData] = useState({
        email: '',
        password: '',
    });

    const [formErrors, setFormErrors] = useState({
        email: '',
        password: '',
    });

    const [isSubmitting, setIsSubmitting] = useState(false);

    const validateForm = () => {
        let isValid = true;
        const errors = { email: '', password: '' };

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
        }

        setFormErrors(errors);
        return isValid;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!validateForm()) return;

        setIsSubmitting(true);

        try {
            await login(formData);
            router.push('/schedule');
        } catch (error) {
            // Auth context handles setting the error state
            console.error('Login failed:', error);
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        // Clear error when user types
        if (formErrors[name as keyof typeof formErrors]) {
            setFormErrors(prev => ({ ...prev, [name]: '' }));
        }
    };

    return (
        <div className="w-full max-w-md mx-auto p-6 bg-white rounded-xl shadow-lg border border-slate-200">
            <div className="text-center mb-8">
                <h1 className="text-2xl font-bold text-slate-900">Sign in to your account</h1>
                <p className="mt-2 text-sm text-slate-600">
                    Or{' '}
                    <Link href="/register" className="font-medium text-blue-600 hover:text-blue-500">
                        create a new account
                    </Link>
                </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                {authError && (
                    <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
                        {authError}
                    </div>
                )}

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
                    autoComplete="current-password"
                    required
                    value={formData.password}
                    onChange={handleChange}
                    error={formErrors.password}
                    leftIcon={<Lock className="w-5 h-5" />}
                />

                <div className="flex items-center justify-between">
                    <div className="flex items-center">
                        <input
                            id="remember-me"
                            name="remember-me"
                            type="checkbox"
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label htmlFor="remember-me" className="ml-2 block text-sm text-slate-900">
                            Remember me
                        </label>
                    </div>

                    <div className="text-sm">
                        <a href="#" className="font-medium text-blue-600 hover:text-blue-500">
                            Forgot your password?
                        </a>
                    </div>
                </div>

                <Button
                    type="submit"
                    variant="primary"
                    size="lg"
                    className="w-full"
                    isLoading={isSubmitting}
                >
                    Sign in
                </Button>
            </form>
        </div>
    );
}
