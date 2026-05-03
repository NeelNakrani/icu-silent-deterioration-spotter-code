/**
 * SBARBrief Component - The "Money View" Right Panel
 *
 * A high-contrast medical dashboard that presents critical patient deterioration
 * insights in under 60 seconds. Designed for non-clinical judges with a "Police Report"
 * aesthetic—urgent, factual, and clear.
 */

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import type { SBARBriefProps, RiskLevel } from '../../types/sbar.types';

const riskTone: Record<RiskLevel, { badge: string; accent: string }> = {
  RED: {
    badge: "bg-critical/15 text-critical",
    accent: "border-critical/50",
  },
  YELLOW: {
    badge: "bg-warning/15 text-warning",
    accent: "border-warning/40",
  },
  GREEN: {
    badge: "bg-success/15 text-success",
    accent: "border-success/40",
  },
};

export default function SBARBrief({ data, onGenerateAIInsight, isGeneratingAI = false }: SBARBriefProps) {
  const tone = riskTone[data.risk];
  const isCritical = data.risk === 'RED';

  return (
    <Card className="bg-bg-panel border border-border-subtle/80 shadow-medical">
      <CardHeader className={`border-b ${tone.accent}`}>
        <div className="flex flex-col items-start gap-3 sm:flex-row sm:justify-between">
          <div>
            <CardTitle className="text-lg text-text-primary">Alert brief</CardTitle>
            <CardDescription className="text-text-secondary">
              {data.window} - latest 6 hour window
            </CardDescription>
          </div>
          <Badge className={tone.badge}>{data.risk} risk</Badge>
        </div>
        <div className="mt-4 grid grid-cols-1 gap-4 text-xs sm:grid-cols-2">
          <div>
            <div className="text-text-muted uppercase tracking-[0.2em]">Patient ID</div>
            <div className="mt-1 text-sm font-semibold text-text-primary font-mono">
              {data.patientId}
            </div>
          </div>
          <div>
            <div className="text-text-muted uppercase tracking-[0.2em]">ICU stay</div>
            <div className="mt-1 text-sm font-semibold text-text-primary font-mono">
              {data.stayCount}
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <Tabs defaultValue="overview">
          <TabsList variant="line" className="w-full justify-start gap-3 overflow-x-auto">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="trends">Trends</TabsTrigger>
            <TabsTrigger value="evidence">Evidence</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="mt-4 space-y-4">
            <section>
              <div className="flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-highlight">
                <span className="h-1.5 w-1.5 rounded-full bg-highlight"></span>
                What's changing
              </div>
              <p className="mt-2 text-sm text-text-primary leading-relaxed">
                {data.trend}
              </p>
            </section>
            <section>
              <div className="flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-warning">
                <span className="h-1.5 w-1.5 rounded-full bg-warning"></span>
                Concerning combination
              </div>
              <p className="mt-2 text-sm text-text-primary leading-relaxed">
                {data.conflict}
              </p>
            </section>
            <section className={`rounded-lg border ${tone.accent} bg-bg-elevated/50 p-4`}>
              <div className="flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-text-secondary">
                <span className="h-1.5 w-1.5 rounded-full bg-text-secondary"></span>
                Next 2 hours
              </div>
              <p className="mt-2 text-sm font-semibold text-text-primary leading-relaxed">
                {data.timeBomb}
              </p>
            </section>
            
            {/* AI Insight Section - Only for Critical Patients */}
            {isCritical && (
              <section className="mt-6 rounded-lg border border-critical/30 bg-critical/5 p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-critical">
                    <span className="h-1.5 w-1.5 rounded-full bg-critical"></span>
                    AI Clinical Insight
                  </div>
                  {onGenerateAIInsight && !data.aiInsight && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={onGenerateAIInsight}
                      disabled={isGeneratingAI}
                      className="text-xs"
                    >
                      {isGeneratingAI ? (
                        <>
                          <Spinner className="mr-2 h-3 w-3" />
                          Generating...
                        </>
                      ) : (
                        'Generate AI Insight'
                      )}
                    </Button>
                  )}
                </div>
                {data.aiInsight ? (
                  <Alert className="border-critical/20 bg-bg-elevated/50">
                    <AlertDescription className="text-sm text-text-primary leading-relaxed">
                      <span className="font-semibold text-critical">IBM watsonx.ai:</span> {data.aiInsight}
                    </AlertDescription>
                  </Alert>
                ) : isGeneratingAI ? (
                  <div className="flex items-center justify-center py-4">
                    <Spinner className="h-5 w-5 text-critical" />
                    <span className="ml-2 text-sm text-text-muted">Analyzing patient data...</span>
                  </div>
                ) : (
                  <p className="text-sm text-text-muted italic">
                    Click "Generate AI Insight" to get IBM watsonx.ai analysis for this critical patient.
                  </p>
                )}
              </section>
            )}
          </TabsContent>

          <TabsContent value="trends" className="mt-4 space-y-3">
            <div className="rounded-lg border border-dashed border-border-subtle/70 bg-bg-elevated/30 p-4 text-sm text-text-muted">
              Trends summary placeholder - connect to vitals chart.
            </div>
            <div className="grid gap-3 text-sm text-text-secondary">
              <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                <span>Respiratory rate</span>
                <span className="text-text-primary font-semibold">18 to 28</span>
              </div>
              <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                <span>Lactate</span>
                <span className="text-text-primary font-semibold">3.9 to 4.5</span>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="evidence" className="mt-4">
            <Accordion type="single" collapsible defaultValue="evidence">
              <AccordionItem value="evidence">
                <AccordionTrigger className="text-sm font-semibold">
                  Evidence tray ({data.reasoning.length} data points)
                </AccordionTrigger>
                <AccordionContent>
                  <ul className="space-y-2 text-xs text-text-secondary">
                    {data.reasoning.map((item, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <span className="mt-1 h-1.5 w-1.5 rounded-full bg-highlight"></span>
                        <span className="text-text-primary font-mono leading-relaxed">
                          {item}
                        </span>
                      </li>
                    ))}
                  </ul>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </TabsContent>
        </Tabs>
      </CardContent>

      <CardFooter className="border-t border-border-subtle/70 pt-4 flex flex-col items-stretch gap-2 sm:flex-row sm:items-center sm:justify-between">
        <Button variant="outline" size="sm">
          Open evidence
        </Button>
        <Button size="sm">Notify team</Button>
      </CardFooter>
    </Card>
  );
}

// Made with Bob
