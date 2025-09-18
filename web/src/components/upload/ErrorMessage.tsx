import React from 'react';

interface ErrorMessageProps {
  message: string;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ message }) => {
  return (
    <div className="p-3 bg-red-100/80 dark:bg-red-900/30 border border-red-300 dark:border-red-700 rounded-lg">
      <p className="text-red-700 dark:text-red-400 text-sm">{message}</p>
    </div>
  );
};