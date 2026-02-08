'use client';

import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import { X, Maximize2, Minimize2 } from 'lucide-react';
import Button from '@/components/ui/Button';
import styles from './Modal.module.css';

interface ModalProps {
    isOpen: boolean;
    onClose: () => void;
    title: string;
    children: React.ReactNode;
    footer?: React.ReactNode;
    size?: 'default' | 'full';
}

export default function Modal({
    isOpen,
    onClose,
    title,
    children,
    footer,
    size = 'default'
}: ModalProps) {
    // Close on Escape key
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
        };

        if (isOpen) {
            window.addEventListener('keydown', handleKeyDown);
            document.body.style.overflow = 'hidden'; // Prevent background scrolling
        }

        return () => {
            window.removeEventListener('keydown', handleKeyDown);
            document.body.style.overflow = '';
        };
    }, [isOpen, onClose]);

    if (!isOpen) return null;

    const modalClass = `${styles.modal} ${size === 'full' ? styles.full : ''}`;

    const content = (
        <div className={styles.backdrop} onClick={onClose}>
            <div
                className={modalClass}
                onClick={(e) => e.stopPropagation()} // Prevent closing when clicking inside
                role="dialog"
                aria-modal="true"
                aria-labelledby="modal-title"
            >
                <header className={styles.header}>
                    <h2 id="modal-title" className={styles.title}>{title}</h2>
                    <div className="flex gap-2">
                        {/* Would toggle full screen here if state was lifted */}
                        <button onClick={onClose} className={styles.closeButton} aria-label="Close modal">
                            <X className="w-6 h-6" />
                        </button>
                    </div>
                </header>

                <div className={styles.content}>
                    {children}
                </div>

                {footer && (
                    <footer className={styles.footer}>
                        {footer}
                    </footer>
                )}
            </div>
        </div>
    );

    // Use portal if document is available (client-side)
    if (typeof document === 'undefined') return null;

    // Render to body
    return createPortal(content, document.body);
}
