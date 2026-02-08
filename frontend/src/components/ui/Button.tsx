'use client';

import React, { ButtonHTMLAttributes, forwardRef } from 'react';
import styles from './Button.module.css';

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
export type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: ButtonVariant;
    size?: ButtonSize;
    isLoading?: boolean;
    leftIcon?: React.ReactNode;
    rightIcon?: React.ReactNode;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
    (
        {
            variant = 'primary',
            size = 'md',
            isLoading = false,
            leftIcon,
            rightIcon,
            children,
            disabled,
            className,
            ...props
        },
        ref
    ) => {
        const classNames = [
            styles.button,
            styles[variant],
            styles[size],
            isLoading && styles.loading,
            className,
        ]
            .filter(Boolean)
            .join(' ');

        return (
            <button
                ref={ref}
                className={classNames}
                disabled={disabled || isLoading}
                {...props}
            >
                {isLoading && <span className={styles.spinner} />}
                {!isLoading && leftIcon && <span className={styles.icon}>{leftIcon}</span>}
                <span className={styles.label}>{children}</span>
                {!isLoading && rightIcon && <span className={styles.icon}>{rightIcon}</span>}
            </button>
        );
    }
);

Button.displayName = 'Button';

export default Button;
