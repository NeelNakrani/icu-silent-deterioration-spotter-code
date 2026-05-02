// Custom hook for managing agent streaming state

import { useState, useEffect, useCallback } from 'react';
import type { AgentId, AgentStatus, AgentStreamState } from '../types/agent-stream.types';
import { getMockReasoningChunks, getMockResult, delay, STREAM_DELAY_MS } from '../utils/mockAgentData';

interface UseAgentStreamOptions {
  patientId: string;
  agentId: AgentId;
  enabled: boolean;
  onComplete?: () => void;
}

export function useAgentStream({
  patientId,
  agentId,
  enabled,
  onComplete
}: UseAgentStreamOptions): AgentStreamState {
  const [status, setStatus] = useState<AgentStatus>('idle');
  const [reasoning, setReasoning] = useState<string[]>([]);
  const [result, setResult] = useState<unknown>(null);
  const [error, setError] = useState<Error | null>(null);
  const [startTime, setStartTime] = useState<number | null>(null);
  const [endTime, setEndTime] = useState<number | null>(null);

  const startStreaming = useCallback(async () => {
    if (!enabled || status !== 'idle') return;

    // Use a delay to avoid synchronous state update in useEffect
    await new Promise(resolve => setTimeout(resolve, 0));

    try {
      setStatus('running');
      setStartTime(Date.now());
      setReasoning([]);
      setError(null);

      // Get mock reasoning chunks
      const chunks = getMockReasoningChunks(agentId);

      // Stream chunks with delay
      for (const chunk of chunks) {
        await delay(STREAM_DELAY_MS);
        setReasoning(prev => [...prev, chunk]);
      }

      // Get final result
      const finalResult = getMockResult(agentId, patientId);
      setResult(finalResult);
      setStatus('complete');
      setEndTime(Date.now());

      // Notify completion
      if (onComplete) {
        onComplete();
      }
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Stream failed'));
      setStatus('error');
      setEndTime(Date.now());
    }
  }, [enabled, status, agentId, patientId, onComplete]);

  useEffect(() => {
    if (enabled && status === 'idle') {
      startStreaming();
    }
  }, [enabled, status, startStreaming]);

  // Reset when disabled
  useEffect(() => {
    if (!enabled) {
      // Use setTimeout to avoid synchronous state update in effect
      const timer = setTimeout(() => {
        setStatus('idle');
        setReasoning([]);
        setResult(null);
        setError(null);
        setStartTime(null);
        setEndTime(null);
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [enabled]);

  return {
    status,
    reasoning,
    result,
    error,
    startTime,
    endTime
  };
}

// Made with Bob
