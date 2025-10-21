import { useWorkbookStore } from '../../state/workbookStore';

const columnLetter = (index: number) => {
  let dividend = index + 1;
  let columnName = '';
  while (dividend > 0) {
    const modulo = (dividend - 1) % 26;
    columnName = String.fromCharCode(65 + modulo) + columnName;
    dividend = Math.floor((dividend - modulo) / 26);
  }
  return columnName;
};

const formatAddress = (row: number, col: number) => `${columnLetter(col)}${row + 1}`;

export const NameBox = () => {
  const { selection } = useWorkbookStore();
  const address = formatAddress(selection.focus.row, selection.focus.col);

  return (
    <div className="min-w-[96px] rounded border border-slate-200 bg-white px-3 py-1 text-sm font-semibold text-slate-700">
      {address}
    </div>
  );
};
