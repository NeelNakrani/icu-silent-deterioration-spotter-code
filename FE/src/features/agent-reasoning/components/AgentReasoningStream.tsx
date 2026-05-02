// @ts-nocheck
// Agent Reasoning Stream Container - Main component orchestrating all agents

import { useState, useEffect } from 'react';
import { AgentPanel } from './AgentPanel';
import { CoordinatorPanel } from './CoordinatorPanel';
import { useAgentStream } from '../hooks/useAgentStream';
import type { AgentConfig } from '../types/agent-stream.types';

interface AgentReasoningStreamProps {
  patientId: string;
  className?: string;
}

// Agent configurations
const AGENT_CONFIGS: AgentConfig[] = [
  {
    id: 'trend',
    name: 'Trend Agent',
    accentColor: '#3b82f6', // Blue
    icon: '📈'
  },
  {
    id: 'lab-conflict',
    name: 'Lab-Conflict Agent',
    accentColor: '#eab308', // Yellow
    icon: '⚠️'
  },
  {
    id: 'timebomb',
    name: 'Time Bomb Agent',
    accentColor: '#ef4444', // Red
    icon: '⏰'
  }
];

export function AgentReasoningStream({ patientId, className = '' }: AgentReasoningStreamProps) {
  const [agentsEnabled, setAgentsEnabled] = useState(true);
  const [completedAgents, setCompletedAgents] = useState<Set<string>>(new Set());
  const [coordinatorEnabled, setCoordinatorEnabled] = useState(false);

  // Initialize agent streams
  const trendStream = useAgentStream({
    patientId,
    agentId: 'trend',
    enabled: agentsEnabled,
    onComplete: () => handleAgentComplete('trend')
  });

  const conflictStream = useAgentStream({
    patientId,
    agentId: 'lab-conflict',
    enabled: agentsEnabled,
    onComplete: () => handleAgentComplete('lab-conflict')
  });

  const timebombStream = useAgentStream({
    patientId,
    agentId: 'timebomb',
    enabled: agentsEnabled,
    onComplete: () => handleAgentComplete('timebomb')
  });

  const coordinatorStream = useAgentStream({
    patientId,
    agentId: 'coordinator',
    enabled: coordinatorEnabled,
    onComplete: () => {}
  });

  // Handle agent completion
  const handleAgentComplete = (agentId: string) => {
    setCompletedAgents(prev => new Set([...prev, agentId]));
  };

  // Enable coordinator when all agents complete
  useEffect(() => {
    if (completedAgents.size === 3 && !coordinatorEnabled) {
      // Small delay before starting coordinator for dramatic effect
      setTimeout(() => {
        setCoordinatorEnabled(true);
      }, 500);
    }
  }, [completedAgents.size, coordinatorEnabled]);

  const allAgentsComplete = completedAgents.size === 3;

  return (
    <div className={`space-y-4 md:space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg md:text-xl font-bold text-text-primary">
            Agent Reasoning Stream
          </h2>
          <p className="text-xs md:text-sm text-text-secondary mt-1">
            Live multi-agent analysis for Patient {patientId}
          </p>
        </div>
        <div className="flex items-center gap-2 self-start sm:self-auto">
          <div className="text-xs text-text-muted">
            {completedAgents.size}/3 agents complete
          </div>
          {allAgentsComplete && (
            <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          )}
        </div>
      </div>

      {/* Agent Panels Grid - Responsive Layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 md:gap-6">
        <AgentPanel
          config={AGENT_CONFIGS[0]}
          streamState={trendStream}
          className="animate-in fade-in slide-in-from-left duration-500"
        />
        <AgentPanel
          config={AGENT_CONFIGS[1]}
          streamState={conflictStream}
          className="animate-in fade-in slide-in-from-left duration-500 [animation-delay:100ms]"
        />
        <AgentPanel
          config={AGENT_CONFIGS[2]}
          streamState={timebombStream}
          className="animate-in fade-in slide-in-from-left duration-500 md:col-span-2 xl:col-span-1 [animation-delay:200ms]"
        />
      </div>

      {/* Coordinator Panel - Appears after all agents complete */}
      {coordinatorEnabled && (
        <CoordinatorPanel streamState={coordinatorStream} />
      )}

      {/* Demo Info */}
      <div className="bg-bg-elevated border border-border-subtle rounded-lg p-3 md:p-4">
        <div className="flex items-start gap-2 md:gap-3">
          <svg className="w-5 h-5 text-highlight shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div className="flex-1">
            <p className="text-xs md:text-sm text-text-secondary leading-relaxed">
              <strong className="text-text-primary">Demo Mode:</strong> This component showcases parallel multi-agent execution with simulated streaming. 
              Each agent analyzes different aspects of patient data simultaneously, then the Coordinator synthesizes their findings.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// Made with Bob
