import React from 'react';

interface StatCardProps {
  label: string;
  value: string;
  icon: string;
  color?: 'blue' | 'green' | 'yellow' | 'red';
}

export const StatCard: React.FC<StatCardProps> = ({ label, value, icon, color = 'green' }) => {
  const colorClasses = {
    blue: 'bg-blue-50 dark:bg-blue-900/20',
    green: 'bg-green-50 dark:bg-green-900/20',
    yellow: 'bg-yellow-50 dark:bg-yellow-900/20',
    red: 'bg-red-50 dark:bg-red-900/20',
  };

  return (
    <div className={`p-4 rounded-lg ${colorClasses[color]} backdrop-blur-sm`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-2xl">{icon}</span>
      </div>
      <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">{value}</p>
      <p className="text-sm text-gray-600 dark:text-gray-400">{label}</p>
    </div>
  );
};