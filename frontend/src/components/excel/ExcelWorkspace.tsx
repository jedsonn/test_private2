import { Ribbon } from './Ribbon';
import { NameBox } from './NameBox';
import { FormulaBar } from './FormulaBar';
import { ExcelGrid } from './ExcelGrid';

export const ExcelWorkspace = () => {
  return (
    <div className="flex h-full w-full flex-col bg-slate-200">
      <Ribbon />
      <div className="flex items-center gap-3 border-b border-slate-200 bg-white px-4 py-2">
        <NameBox />
        <FormulaBar />
      </div>
      <div className="flex-1 overflow-hidden">
        <ExcelGrid />
      </div>
      <div className="flex items-center justify-between border-t border-slate-200 bg-white px-4 py-2 text-xs text-slate-500">
        <span>Status: Prototype grid ready</span>
        <span>Sheet1</span>
      </div>
    </div>
  );
};
