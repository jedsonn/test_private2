import { create } from 'zustand';
import { produce } from 'immer';

export type CellCoordinate = { row: number; col: number };
export type CellSelection = {
  anchor: CellCoordinate;
  focus: CellCoordinate;
};

export type CellData = {
  value: string;
  formula?: string;
};

export interface WorkbookState {
  rows: number;
  columns: number;
  data: Record<string, CellData>;
  selection: CellSelection;
  setSelection: (selection: CellSelection) => void;
  updateCell: (coord: CellCoordinate, updater: (cell: CellData) => CellData) => void;
}

const defaultSelection: CellSelection = {
  anchor: { row: 0, col: 0 },
  focus: { row: 0, col: 0 }
};

const getKey = ({ row, col }: CellCoordinate) => `${row}:${col}`;

export const useWorkbookStore = create<WorkbookState>((set) => ({
  rows: 60,
  columns: 26,
  data: {},
  selection: defaultSelection,
  setSelection: (selection) => set({ selection }),
  updateCell: (coord, updater) =>
    set((state) =>
      produce(state, (draft) => {
        const key = getKey(coord);
        const current = draft.data[key] ?? { value: '' };
        draft.data[key] = updater(current);
      }),
    ),
}));
