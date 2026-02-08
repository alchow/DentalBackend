'use client';

import React, { InputHTMLAttributes, forwardRef, useId } from 'react';
import styles from './Input.module.css';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
    leftIcon?: React.ReactNode;
    rightIcon?: React.ReactNode;
    containerClassName?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
    (
        {
            label,
            error,
            leftIcon,
            rightIcon,
            className,
            containerClassName,
            id,
            ...props
        },
        ref
    ) => {
        const generatedId = useId();
        const inputId = id || generatedId;

        const inputClassNames = [
            styles.input,
            error && styles.errorInput,
            leftIcon && styles.hasLeftIcon,
            rightIcon && styles.hasRightIcon,
            className,
        ]
            .filter(Boolean)
            .join(' ');

        return (
            <div className={`${styles.container} ${containerClassName || ''}`}>
                {label && (
                    <label htmlFor={inputId} className={styles.label}>
                        {label}
                    </label>
                )}

                <div className={styles.inputWrapper}>
                    {leftIcon && <span className={styles.leftIcon}>{leftIcon}</span>}

                    <input
                        id={inputId}
                        ref={ref}
                        className={inputClassNames}
                        aria-invalid={!!error}
                        aria-describedby={error ? `${inputId}-error` : undefined}
                        {...props}
                    />

                    {rightIcon && <span className={styles.rightIcon}>{rightIcon}</span>}
                </div>

                {error && (
                    <p id={`${inputId}-error`} className={styles.errorMessage}>
                        {error}
                    </p>
                )}
            </div>
        );
    }
);

Input.displayName = 'Input';

export default Input;
