import React from 'react';
import { Spinner } from '../ui/Spinner';

interface LoadingStateProps {
  message?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({ message = "Loading..." }) => {
  return (
    <div className="flex flex-col items-center justify-center h-full w-full p-8 gap-4 min-h-[50vh]">
      <Spinner size="large" />
      <p style={{ color: 'var(--text-muted)' }}>{message}</p>
    </div>
  );
};
