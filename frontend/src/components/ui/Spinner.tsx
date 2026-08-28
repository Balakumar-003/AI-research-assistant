import React from 'react';
import './Spinner.css';

interface SpinnerProps {
  size?: 'small' | 'medium' | 'large';
  color?: string;
}

export const Spinner: React.FC<SpinnerProps> = ({ size = 'medium', color = 'var(--primary)' }) => {
  const sizeMap = {
    small: '1rem',
    medium: '2rem',
    large: '3rem',
  };

  return (
    <div 
      className="spinner animate-spin"
      style={{
        width: sizeMap[size],
        height: sizeMap[size],
        border: `3px solid ${color}40`,
        borderTopColor: color,
        borderRadius: '50%'
      }}
    />
  );
};
