// Agent Reasoning Stream Types

export type AgentId = 'trend' | 'lab-conflict' | 'timebomb' | 'coordinator';

export type AgentStatus = 'idle' | 'running' | 'complete' | 'error';

export interface StreamChunk {
  agent_id: AgentId;
  chunk_type: 'reasoning' | 'status' | 'result';
  content: string;
  timestamp: string;
  is_final: boolean;
}

export interface AgentConfig {
  id: AgentId;
  name: string;
  accentColor: string;
  icon: string;
}

export interface AgentStreamState {
  status: AgentStatus;
  reasoning: string[];
  result: unknown | null;
  error: Error | null;
  startTime: number | null;
  endTime: number | null;
}

// Made with Bob
