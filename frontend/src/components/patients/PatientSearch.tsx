'use client';

import React, { useState, useEffect } from 'react';
import { Search, Plus } from 'lucide-react';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import { useDebounce } from '@/lib/hooks/useDebounce'; // We need to create this
import styles from './PatientSearch.module.css';

interface PatientSearchProps {
    onSearch: (query: string) => void;
    onAddPatient?: () => void;
    placeholder?: string;
}

export default function PatientSearch({
    onSearch,
    onAddPatient,
    placeholder = "Search by last name..."
}: PatientSearchProps) {
    const [searchTerm, setSearchTerm] = useState('');

    // Debounce search input to avoid API hammer
    const debouncedSearchTerm = useDebounce(searchTerm, 500);

    useEffect(() => {
        onSearch(debouncedSearchTerm);
    }, [debouncedSearchTerm, onSearch]);

    return (
        <div className={styles.container}>
            <Input
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder={placeholder}
                leftIcon={<Search className="w-4 h-4" />}
                className="w-full"
                containerClassName="flex-1"
            />
            {onAddPatient && (
                <Button
                    variant="primary"
                    onClick={onAddPatient}
                    className={styles.addButton}
                    aria-label="Add new patient"
                >
                    <Plus className="w-5 h-5" />
                </Button>
            )}
        </div>
    );
}
