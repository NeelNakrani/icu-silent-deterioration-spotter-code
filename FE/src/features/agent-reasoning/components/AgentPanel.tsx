// Agent Panel Component - Individual agent display with streaming reasoning

import { AgentStatusIndicator } from './AgentStatusIndicator';
import { ReasoningStream } from './ReasoningStream';
import type { AgentConfig, AgentStreamState } from '../types/agent-stream.types';

interface GenericAgentResult {
  summary?: string;
  overall_concern?: number;
  overall_severity?: number;
  overall_urgency?: number;
}

interface AgentPanelProps {
  config: AgentConfig;
  streamState: AgentStreamState;
  className?: string;
}

export function AgentPanel({ config, streamState, className = '' }: AgentPanelProps) {
  const { status, reasoning, startTime, endTime } = streamState;
  const result = streamState.result as GenericAgentResult | null;

  // Calculate duration if available
  const duration = startTime && endTime ? ((endTime - startTime) / 1000).toFixed(1) : null;

  return (
    <div
      className={`bg-bg-panel border-l-4 rounded-xl overflow-hidden shadow-lg transition-all duration-300 hover:shadow-xl ${className}`}
      style={{ borderColor: config.accentColor }}
    >
      {/* Header */}
      <div className="px-4 md:px-6 py-3 md:py-4 border-b border-border-subtle bg-bg-elevated">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between mb-2">
          <div className="flex items-center gap-2 md:gap-3">
            <div
              className="w-8 h-8 md:w-10 md:h-10 rounded-lg flex items-center justify-center text-lg md:text-xl"
              style={{ backgroundColor: `${config.accentColor}20`, color: config.accentColor }}
            >
              {config.icon}
            </div>
            <h3
              className="text-sm md:text-base font-bold uppercase tracking-wider break-words"
              style={{ color: config.accentColor }}
            >
              {config.name}
            </h3>
          </div>
          <AgentStatusIndicator status={status} />
        </div>
        
        {duration && status === 'complete' && (
          <div className="text-xs text-text-muted font-mono">
            Completed in {duration}s
          </div>
        )}
      </div>

      {/* Reasoning Stream */}
      <div className="p-4 md:p-6">
        <ReasoningStream
          chunks={reasoning}
          status={status}
          maxHeight="300px"
        />
      </div>

      {/* Result Summary (if complete) */}
      {status === 'complete' && result && (
        <div className="px-4 md:px-6 pb-4 md:pb-6">
          <div
            className="border-t-2 pt-3 md:pt-4"
            style={{ borderColor: `${config.accentColor}40` }}
          >
            <div className="text-xs font-bold uppercase tracking-wider text-text-secondary mb-2">
              Summary
            </div>
            <div className="text-sm text-text-primary font-medium">
              {result.summary || 'Analysis complete'}
            </div>
            {result.overall_concern !== undefined && (
              <div className="mt-2 flex items-center gap-2">
                <span className="text-xs text-text-muted">Concern Level:</span>
                <div className="flex gap-1">
                  {[0, 1, 2, 3].map((level) => (
                    <div
                      key={level}
                      className={`w-2 h-4 rounded-sm ${
                        level <= (result.overall_concern ?? -1)
                          ? 'opacity-100'
                          : 'opacity-20'
                      }`}
                      style={{
                        backgroundColor: config.accentColor
                      }}
                    />
                  ))}
                </div>
              </div>
            )}
            {result.overall_severity !== undefined && (
              <div className="mt-2 flex items-center gap-2">
                <span className="text-xs text-text-muted">Severity Level:</span>
                <div className="flex gap-1">
                  {[0, 1, 2, 3].map((level) => (
                    <div
                      key={level}
                      className={`w-2 h-4 rounded-sm ${
                        level <= (result.overall_severity ?? -1)
                          ? 'opacity-100'
                          : 'opacity-20'
                      }`}
                      style={{
                        backgroundColor: config.accentColor
                      }}
                    />
                  ))}
                </div>
              </div>
            )}
            {result.overall_urgency !== undefined && (
              <div className="mt-2 flex items-center gap-2">
                <span className="text-xs text-text-muted">Urgency Level:</span>
                <div className="flex gap-1">
                  {[0, 1, 2, 3].map((level) => (
                    <div
                      key={level}
                      className={`w-2 h-4 rounded-sm ${
                        level <= (result.overall_urgency ?? -1)
                          ? 'opacity-100'
                          : 'opacity-20'
                      }`}
                      style={{
                        backgroundColor: config.accentColor
                      }}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// Made with Bob
