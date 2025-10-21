type Task = {
  id: string;
  instruction: string;
  completed?: boolean;
};

interface ExercisePanelProps {
  title: string;
  description: string;
  estimatedTime: number;
  tasks: Task[];
}

export const ExercisePanel = ({ title, description, estimatedTime, tasks }: ExercisePanelProps) => {
  return (
    <aside className="flex h-full w-full max-w-md flex-col border-l border-slate-200 bg-white">
      <div className="border-b border-slate-200 p-6">
        <h3 className="text-xl font-semibold text-excel-green">{title}</h3>
        <p className="mt-2 text-sm text-slate-600">{description}</p>
        <p className="mt-4 text-xs uppercase tracking-wide text-slate-500">Estimated time: {estimatedTime} minutes</p>
      </div>
      <div className="flex-1 overflow-y-auto p-6">
        <h4 className="text-sm font-semibold text-slate-700">Tasks</h4>
        <ul className="mt-3 space-y-3">
          {tasks.map((task) => (
            <li key={task.id} className="rounded border border-slate-200 bg-slate-50 p-3 text-sm text-slate-600">
              <div className="flex items-start gap-2">
                <span className="mt-1 h-2 w-2 rounded-full bg-excel-green" />
                <span>{task.instruction}</span>
              </div>
            </li>
          ))}
        </ul>
      </div>
      <div className="border-t border-slate-200 p-6">
        <button type="button" className="w-full rounded bg-excel-green px-4 py-2 text-sm font-semibold text-white hover:bg-excel-dark">
          Check My Work (coming soon)
        </button>
      </div>
    </aside>
  );
};
