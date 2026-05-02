// Coordinator Panel Component - Appears after all agents complete

import { AgentStatusIndicator } from './AgentStatusIndicator';
import { ReasoningStream } from './ReasoningStream';
import type { AgentStreamState } from '../types/agent-stream.types';

interface CoordinatorPanelProps {
  streamState: AgentStreamState;
  className?: string;
}

export function CoordinatorPanel({ streamState, className = '' }: CoordinatorPanelProps) {
  const { status, reasoning, startTime, endTime } = streamState;

  // Calculate duration if available
  const duration = startTime && endTime ? ((endTime - startTime) / 1000).toFixed(1) : null;

  return (
    <div
      className={`bg-bg-panel border-l-4 border-purple-500 rounded-xl overflow-hidden shadow-lg animate-in fade-in slide-in-from-bottom duration-500 ${className}`}
    >
      {/* Header */}
      <div className="px-4 md:px-6 py-3 md:py-4 border-b border-border-subtle bg-gradient-to-r from-purple-900/20 to-bg-elevated">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2 md:gap-3">
            <div className="w-8 h-8 md:w-10 md:h-10 rounded-lg bg-purple-500/20 flex items-center justify-center text-lg md:text-xl text-purple-500">
              🎯
            </div>
            <h3 className="text-sm md:text-base font-bold uppercase tracking-wider text-purple-500">
              Coordinator Agent
            </h3>
          </div>
          <AgentStatusIndicator status={status} />
        </div>
        
        <p className="text-xs text-text-muted mt-1">
          Synthesizing findings from all agents...
        </p>
        
        {duration && status === 'complete' && (
          <div className="text-xs text-text-muted font-mono mt-1">
            Synthesis completed in {duration}s
          </div>
        )}
      </div>

      {/* Reasoning Stream */}
      <div className="p-4 md:p-6">
        <ReasoningStream
          chunks={reasoning}
          status={status}
          maxHeight="250px"
        />
      </div>

      {/* Final Output (if complete) */}
      {status === 'complete' && (
        <div className="px-4 md:px-6 pb-4 md:pb-6">
          <div className="border-t-2 border-purple-500/40 pt-3 md:pt-4">
            <div className="flex items-center gap-2 mb-3">
              <svg className="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-xs font-bold uppercase tracking-wider text-purple-500">
                Multi-Agent Analysis Complete
              </span>
            </div>
            <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-3 md:p-4">
              <p className="text-sm text-text-primary leading-relaxed">
                All specialized agents have completed their analysis. The system has identified multiple concerning patterns requiring clinical attention. Review the individual agent findings above for detailed insights.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Made with Bob
