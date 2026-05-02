/**
 * SBARBrief Component - The "Money View" Right Panel
 * 
 * A high-contrast medical dashboard that presents critical patient deterioration
 * insights in under 60 seconds. Designed for non-clinical judges with a "Police Report"
 * aesthetic—urgent, factual, and clear.
 */

import { useState } from 'react';
import type { SBARBriefProps, RiskLevel } from '../../types/sbar.types';

const riskConfig: Record<RiskLevel, { bg: string; text: string; glow: string; border: string }> = {
  RED: {
    bg: 'bg-critical',
    text: 'text-critical',
    glow: 'shadow-[0_0_20px_rgba(239,68,68,0.4)]',
    border: 'border-critical'
  },
  YELLOW: {
    bg: 'bg-warning',
    text: 'text-warning',
    glow: 'shadow-[0_0_20px_rgba(234,179,8,0.4)]',
    border: 'border-warning'
  },
  GREEN: {
    bg: 'bg-success',
    text: 'text-success',
    glow: 'shadow-[0_0_20px_rgba(34,197,94,0.4)]',
    border: 'border-success'
  }
};

export default function SBARBrief({ data }: SBARBriefProps) {
  const [isEvidenceExpanded, setIsEvidenceExpanded] = useState(false);
  const config = riskConfig[data.risk];

  return (
    <div className="h-full flex flex-col bg-bg-panel border border-border-subtle rounded-xl overflow-hidden shadow-lg">
      {/* 60-Second Header - Responsive padding */}
      <header className={`${config.bg} px-4 md:px-6 py-3 md:py-4 border-b-4 ${config.border}`}>
        {/* Risk Badge - Full Width Status Bar */}
        <div className="flex items-center justify-between mb-2 md:mb-3">
          <div className={`text-xl md:text-2xl font-black tracking-wider ${data.risk === 'RED' ? 'text-white' : data.risk === 'YELLOW' ? 'text-gray-900' : 'text-white'}`}>
            {data.risk} RISK
          </div>
          <div className={`px-3 md:px-4 py-1 rounded-full text-[10px] md:text-xs font-bold uppercase ${data.risk === 'RED' ? 'bg-white/20 text-white' : data.risk === 'YELLOW' ? 'bg-black/20 text-gray-900' : 'bg-white/20 text-white'}`}>
            ACTIVE ALERT
          </div>
        </div>

        {/* Vital Metadata - Responsive grid */}
        <div className="grid grid-cols-2 gap-3 md:gap-4 mt-3 md:mt-4">
          <div>
            <div className={`text-[10px] md:text-xs font-semibold uppercase tracking-wider mb-1 ${data.risk === 'RED' ? 'text-white/70' : data.risk === 'YELLOW' ? 'text-gray-900/70' : 'text-white/70'}`}>
              Patient ID
            </div>
            <div className={`text-lg md:text-xl font-mono font-bold ${data.risk === 'RED' ? 'text-white' : data.risk === 'YELLOW' ? 'text-gray-900' : 'text-white'}`}>
              {data.patientId}
            </div>
          </div>
          <div>
            <div className={`text-[10px] md:text-xs font-semibold uppercase tracking-wider mb-1 ${data.risk === 'RED' ? 'text-white/70' : data.risk === 'YELLOW' ? 'text-gray-900/70' : 'text-white/70'}`}>
              ICU Stay
            </div>
            <div className={`text-lg md:text-xl font-mono font-bold ${data.risk === 'RED' ? 'text-white' : data.risk === 'YELLOW' ? 'text-gray-900' : 'text-white'}`}>
              {data.stayCount}
            </div>
          </div>
        </div>

        {/* Data Freshness */}
        <div className="mt-3 md:mt-4 pt-2 md:pt-3 border-t border-white/20">
          <div className={`text-[10px] md:text-xs font-semibold uppercase tracking-wider mb-1 ${data.risk === 'RED' ? 'text-white/70' : data.risk === 'YELLOW' ? 'text-gray-900/70' : 'text-white/70'}`}>
            Data Window
          </div>
          <div className={`text-xs md:text-sm font-mono ${data.risk === 'RED' ? 'text-white' : data.risk === 'YELLOW' ? 'text-gray-900' : 'text-white'}`}>
            {data.window}
          </div>
        </div>
      </header>

      {/* The Inference Engine - 3 Critical Questions - Responsive padding */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4 md:space-y-6">
        {/* Trend Agent */}
        <section>
          <div className="flex items-center gap-2 mb-2 md:mb-3">
            <div className="w-1 h-5 md:h-6 bg-highlight rounded-full"></div>
            <h3 className="text-xs md:text-sm font-bold uppercase tracking-wider text-highlight">
              What's Changing?
            </h3>
          </div>
          <p className="text-sm md:text-base leading-relaxed text-text-primary font-medium">
            {data.trend}
          </p>
        </section>

        {/* Lab-Conflict Agent */}
        <section>
          <div className="flex items-center gap-2 mb-2 md:mb-3">
            <div className="w-1 h-5 md:h-6 bg-warning rounded-full"></div>
            <h3 className="text-xs md:text-sm font-bold uppercase tracking-wider text-warning">
              Concerning Combination
            </h3>
          </div>
          <p className="text-sm md:text-base leading-relaxed text-text-primary font-medium">
            {data.conflict}
          </p>
        </section>

        {/* Time Bomb Agent - High Priority Box - Responsive padding */}
        <section className={`border-3 md:border-4 ${config.border} ${config.glow} rounded-lg p-4 md:p-5 bg-bg-elevated`}>
          <div className="flex items-center gap-2 mb-2 md:mb-3">
            <svg className={`w-5 h-5 md:w-6 md:h-6 ${config.text}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <h3 className={`text-xs md:text-sm font-black uppercase tracking-wider ${config.text}`}>
              Next 2 Hours
            </h3>
          </div>
          <p className={`text-base md:text-lg leading-relaxed font-bold ${config.text}`}>
            {data.timeBomb}
          </p>
        </section>
      </div>

      {/* Evidence Tray - Collapsible Reasoning Chain - Responsive padding */}
      <div className="border-t border-border-subtle">
        <button
          onClick={() => setIsEvidenceExpanded(!isEvidenceExpanded)}
          className="w-full px-4 md:px-6 py-3 md:py-4 flex items-center justify-between hover:bg-bg-elevated transition-colors"
        >
          <div className="flex items-center gap-2 md:gap-3">
            <svg className="w-4 h-4 md:w-5 md:h-5 text-highlight" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span className="text-xs md:text-sm font-bold uppercase tracking-wider text-text-primary">
              Evidence Tray
            </span>
            <span className="text-[10px] md:text-xs text-text-muted">
              ({data.reasoning.length} data points)
            </span>
          </div>
          <svg
            className={`w-4 h-4 md:w-5 md:h-5 text-text-secondary transition-transform ${isEvidenceExpanded ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {/* Collapsible Content */}
        <div
          className={`overflow-hidden transition-all duration-300 ease-in-out ${
            isEvidenceExpanded ? 'max-h-96' : 'max-h-0'
          }`}
        >
          <div className="px-4 md:px-6 pb-4 md:pb-6 pt-2 bg-bg-main/50">
            <p className="text-[10px] md:text-xs text-text-muted mb-3 md:mb-4 italic">
              Raw data points cited by the AI inference engine. This proves the analysis is grounded in actual measurements, not hallucinations.
            </p>
            <ul className="space-y-2">
              {data.reasoning.map((item, index) => (
                <li key={index} className="flex items-start gap-2 md:gap-3">
                  <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-highlight flex-shrink-0"></div>
                  <span className="text-xs md:text-sm text-text-primary font-mono leading-relaxed">
                    {item}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

// Made with Bob
