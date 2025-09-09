import React from 'react';

interface StatsCardProps {
  title: string;
  count: number;
  description: string;
  color: 'yellow' | 'blue' | 'purple' | 'green';
  icon?: React.ReactNode;
}

const StatsCard: React.FC<StatsCardProps> = ({ title, count, description, color, icon }) => {
  const colorClasses = {
    yellow: {
      bg: 'bg-yellow-100',
      text: 'text-yellow-600',
      border: 'border-yellow-200'
    },
    blue: {
      bg: 'bg-blue-100',
      text: 'text-blue-600',
      border: 'border-blue-200'
    },
    purple: {
      bg: 'bg-purple-100',
      text: 'text-purple-600',
      border: 'border-purple-200'
    },
    green: {
      bg: 'bg-fresh-100 dark:bg-fresh-900',
      text: 'text-fresh-600 dark:text-fresh-400',
      border: 'border-green-200'
    }
  };

  const classes = colorClasses[color];

  return (
    <div className={`bg-white dark:bg-plum-900 overflow-hidden shadow rounded-lg border ${classes.border} hover:shadow-md transition-shadow`}>
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className={`w-8 h-8 ${classes.bg} rounded-full flex items-center justify-center`}>
              {icon ? (
                <div className={`${classes.text}`}>{icon}</div>
              ) : (
                <span className={`${classes.text} font-semibold`}>{count}</span>
              )}
            </div>
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-plum-600 dark:text-plum-400 truncate">
                {title}
              </dt>
              <dd className="flex items-baseline">
                <div className="text-2xl font-semibold text-plum-900 dark:text-plum-100">
                  {count}
                </div>
                <div className="ml-2 text-sm text-plum-700 dark:text-plum-300">
                  {description}
                </div>
              </dd>
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatsCard;
