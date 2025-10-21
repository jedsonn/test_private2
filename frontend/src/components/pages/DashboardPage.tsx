const roadmap = [
  {
    phase: 'Phase 1: Core Excel Engine',
    timeframe: 'Weeks 1-2',
    highlights: [
      'Excel-like grid with row/column headers and selection states',
      'Formula bar, name box, and HyperFormula integration prototype',
      'Foundational formatting controls and ribbon scaffolding'
    ]
  },
  {
    phase: 'Phase 2: Exercise System',
    timeframe: 'Weeks 3-4',
    highlights: [
      'Exercise data model and validation engine',
      'Real-time feedback and hint delivery loop',
      'Seed set of 20 certification-aligned exercises'
    ]
  },
  {
    phase: 'Phase 3: Student & Instructor Experience',
    timeframe: 'Weeks 5-6',
    highlights: [
      'Instructor dashboards with progress analytics',
      'Student mastery tracking and readiness scoring',
      'Exercise authoring toolkit'
    ]
  }
];

export const DashboardPage = () => {
  return (
    <section className="flex w-full flex-1 flex-col gap-6 overflow-y-auto bg-slate-50 p-10">
      <div>
        <h2 className="text-3xl font-semibold text-excel-green">Program Roadmap</h2>
        <p className="mt-2 max-w-3xl text-slate-600">
          Track high-level milestones that guide implementation. Each milestone aligns directly with Certiport&apos;s Excel Expert
          certification domains and ensures the simulator provides measurable learning outcomes for students and instructors.
        </p>
      </div>
      <div className="grid gap-6 lg:grid-cols-3">
        {roadmap.map((item) => (
          <article key={item.phase} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-xl font-semibold text-excel-green">{item.phase}</h3>
            <p className="mt-1 text-sm uppercase tracking-wide text-excel-blue">{item.timeframe}</p>
            <ul className="mt-4 space-y-2 text-sm text-slate-600">
              {item.highlights.map((highlight) => (
                <li key={highlight} className="flex items-start gap-2">
                  <span className="mt-1 h-2 w-2 rounded-full bg-excel-green" />
                  <span>{highlight}</span>
                </li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </section>
  );
};
