import { Link, Outlet, useLocation } from 'react-router-dom';
import { useMemo } from 'react';
import { cn } from '../../utils/cn';

const routes = [
  { to: '/', label: 'Home' },
  { to: '/dashboard', label: 'Dashboard' }
];

export const AppShell = () => {
  const location = useLocation();
  const activePath = useMemo(() => location.pathname, [location.pathname]);

  return (
    <div className="flex min-h-screen flex-col bg-slate-100 text-slate-900">
      <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4 shadow-sm">
        <div className="flex items-center gap-4">
          <span className="text-xl font-semibold text-excel-green">Excel Expert Training</span>
          <nav className="flex gap-2 text-sm font-medium">
            {routes.map((route) => (
              <Link
                key={route.to}
                className={cn(
                  'rounded px-3 py-2 transition-colors hover:bg-excel-green/10',
                  activePath === route.to && 'bg-excel-green/10 text-excel-green'
                )}
                to={route.to}
              >
                {route.label}
              </Link>
            ))}
          </nav>
        </div>
        <div className="text-xs uppercase tracking-wide text-slate-500">Prototype</div>
      </header>
      <main className="flex flex-1 overflow-hidden">
        <Outlet />
      </main>
    </div>
  );
};
