import { useState, useEffect } from 'react';
import { useWorkbookStore } from '../../state/workbookStore';

export const FormulaBar = () => {
  const { selection, data, updateCell } = useWorkbookStore();
  const [inputValue, setInputValue] = useState('');
  const key = `${selection.focus.row}:${selection.focus.col}`;

  useEffect(() => {
    const cell = data[key];
    setInputValue(cell?.formula ?? cell?.value ?? '');
  }, [data, key]);

  const handleCommit = () => {
    updateCell(selection.focus, () => ({ value: inputValue.startsWith('=') ? '' : inputValue, formula: inputValue.startsWith('=') ? inputValue : undefined }));
  };

  return (
    <div className="flex items-center gap-3 border-b border-slate-200 bg-white px-4 py-2">
      <span className="text-xs font-semibold uppercase text-slate-500">fx</span>
      <input
        className="flex-1 rounded border border-slate-200 px-3 py-1 text-sm focus:border-excel-green focus:outline-none focus:ring-1 focus:ring-excel-green"
        value={inputValue}
        onChange={(event) => setInputValue(event.target.value)}
        onBlur={handleCommit}
        onKeyDown={(event) => {
          if (event.key === 'Enter') {
            handleCommit();
          }
        }}
        placeholder="Enter value or formula"
      />
    </div>
  );
};
