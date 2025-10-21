const ribbonTabs = [
  { name: 'Home', actions: ['Clipboard', 'Font', 'Alignment', 'Number', 'Styles', 'Cells', 'Editing'] },
  { name: 'Insert', actions: ['Tables', 'Illustrations', 'Charts', 'Sparklines'] },
  { name: 'Formulas', actions: ['Function Library', 'Defined Names', 'Formula Auditing'] },
  { name: 'Data', actions: ['Get & Transform', 'Sort & Filter', 'Data Tools'] },
  { name: 'Review', actions: ['Proofing', 'Accessibility', 'Protect'] }
];

export const Ribbon = () => {
  return (
    <div className="flex flex-col border-b border-slate-200 bg-gradient-to-b from-white to-slate-100">
      <div className="flex items-center gap-6 px-6 pt-3 text-sm font-medium text-slate-700">
        {ribbonTabs.map((tab) => (
          <button
            key={tab.name}
            type="button"
            className="rounded-t border-b-2 border-transparent px-2 pb-2 transition hover:border-excel-green hover:text-excel-green"
          >
            {tab.name}
          </button>
        ))}
      </div>
      <div className="flex gap-6 px-6 pb-3">
        {ribbonTabs[0].actions.map((action) => (
          <div key={action} className="rounded border border-slate-200 bg-white px-4 py-3 text-xs uppercase tracking-wide text-slate-500">
            {action}
          </div>
        ))}
      </div>
    </div>
  );
};
