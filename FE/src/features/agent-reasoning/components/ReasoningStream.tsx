// Reasoning Stream Component - Displays streaming text with auto-scroll

import { useEffect, useRef } from 'react';
import type { AgentStatus } from '../types/agent-stream.types';

interface ReasoningStreamProps {
  chunks: string[];
  status: AgentStatus;
  maxHeight?: string;
  className?: string;
}

export function ReasoningStream({
  chunks,
  status,
  maxHeight = '300px',
  className = ''
}: ReasoningStreamProps) {
  const streamRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom as new text arrives
  useEffect(() => {
    if (streamRef.current) {
      streamRef.current.scrollTop = streamRef.current.scrollHeight;
    }
  }, [chunks]);

  return (
    <div
      ref={streamRef}
      className={`overflow-y-auto space-y-2 ${className}`}
      style={{ maxHeight }}
      role="log"
      aria-live="polite"
      aria-atomic="false"
    >
      {chunks.length === 0 && status === 'idle' && (
        <div className="text-sm text-text-muted italic">
          Waiting to start...
        </div>
      )}
      
      {chunks.map((chunk, index) => (
        <div
          key={index}
          className="reasoning-chunk animate-in fade-in slide-in-from-left duration-300"
          style={{ animationDelay: `${index * 50}ms` }}
        >
          <div className="flex items-start gap-2">
            <span className="text-xs text-text-muted font-mono mt-0.5 flex-shrink-0">
              {new Date().toLocaleTimeString('en-US', { 
                hour12: false, 
                hour: '2-digit', 
                minute: '2-digit',
                second: '2-digit'
              })}
            </span>
            <span className="text-sm font-mono leading-relaxed text-text-primary flex-1">
              {chunk}
            </span>
          </div>
        </div>
      ))}
      
      {status === 'running' && chunks.length > 0 && (
        <div className="flex items-center gap-2 animate-pulse">
          <span className="text-xs text-text-muted font-mono">
            {new Date().toLocaleTimeString('en-US', { 
              hour12: false, 
              hour: '2-digit', 
              minute: '2-digit',
              second: '2-digit'
            })}
          </span>
          <span className="text-sm font-mono text-highlight">▊</span>
        </div>
      )}
      
      {status === 'error' && (
        <div className="text-sm text-critical font-medium">
          ✗ Stream error occurred
        </div>
      )}
    </div>
  );
}

// Made with Bob
