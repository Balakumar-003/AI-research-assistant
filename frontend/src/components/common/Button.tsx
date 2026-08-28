import React from 'react';
import './Button.css';
import { Spinner } from '../ui/Spinner';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'small' | 'medium' | 'large';
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({ 
  children, 
  variant = 'primary', 
  isLoading, 
  disabled, 
  className = '', 
  ...props 
}) => {
  return (
    <button 
      className={`btn btn-${variant} ${className}`} 
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? <Spinner size="small" color="currentColor" /> : null}
      <span style={{ opacity: isLoading ? 0.7 : 1 }}>{children}</span>
    </button>
  );
};
