import { Link } from 'react-router-dom';

export const LandingPage = () => {
  return (
    <section className="flex w-full flex-1 items-center justify-center bg-gradient-to-br from-white via-slate-100 to-slate-200">
      <div className="max-w-4xl space-y-6 rounded-2xl border border-slate-200 bg-white p-12 shadow-lg">
        <h1 className="text-4xl font-bold text-excel-green">Excel Expert Certification Training</h1>
        <p className="text-lg text-slate-600">
          This prototype lays the foundation for a web-based Excel simulator that mirrors the Microsoft Excel interface while
          delivering certification-aligned training content. Explore the dashboard for roadmap milestones and access the
          exercise workspace preview to see the grid layout prototype.
        </p>
        <div className="flex gap-4">
          <Link
            to="/exercise/sample"
            className="rounded-lg bg-excel-green px-6 py-3 text-white shadow transition hover:bg-excel-dark"
          >
            Open Workspace Prototype
          </Link>
          <Link
            to="/dashboard"
            className="rounded-lg border border-excel-green px-6 py-3 text-excel-green transition hover:bg-excel-green/10"
          >
            View Roadmap Dashboard
          </Link>
        </div>
      </div>
    </section>
  );
};
