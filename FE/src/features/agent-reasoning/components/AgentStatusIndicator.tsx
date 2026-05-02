// Agent Status Indicator Component

import type { AgentStatus } from '../types/agent-stream.types';

interface AgentStatusIndicatorProps {
  status: AgentStatus;
  className?: string;
}

export function AgentStatusIndicator({ status, className = '' }: AgentStatusIndicatorProps) {
  const getStatusConfig = () => {
    switch (status) {
      case 'running':
        return {
          label: 'RUNNING',
          color: 'bg-blue-500',
          textColor: 'text-blue-500',
          animate: 'animate-pulse'
        };
      case 'complete':
        return {
          label: 'COMPLETE',
          color: 'bg-green-500',
          textColor: 'text-green-500',
          animate: ''
        };
      case 'error':
        return {
          label: 'ERROR',
          color: 'bg-red-500',
          textColor: 'text-red-500',
          animate: ''
        };
      case 'idle':
      default:
        return {
          label: 'IDLE',
          color: 'bg-gray-500',
          textColor: 'text-gray-500',
          animate: ''
        };
    }
  };

  const config = getStatusConfig();

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className={`w-2 h-2 rounded-full ${config.color} ${config.animate}`} />
      <span className={`text-xs font-bold uppercase tracking-wider ${config.textColor}`}>
        {config.label}
      </span>
      {status === 'complete' && (
        <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      )}
      {status === 'error' && (
        <svg className="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      )}
    </div>
  );
}

// Made with Bob
