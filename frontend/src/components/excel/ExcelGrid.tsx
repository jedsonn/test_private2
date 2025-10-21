import { useMemo, type CSSProperties } from 'react';
import { AgGridReact } from 'ag-grid-react';
import type { ColDef, GridApi, GridOptions } from 'ag-grid-community';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
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

export const ExcelGrid = () => {
  const { rows, columns, data, setSelection, updateCell } = useWorkbookStore();

  const columnDefs = useMemo<ColDef[]>(() => {
    return new Array(columns).fill(null).map((_, index) => ({
      headerName: columnLetter(index),
      field: `col_${index}`,
      editable: true,
      width: 100,
      headerClass: 'excel-header-cell',
      cellClass: 'excel-cell'
    }));
  }, [columns]);

  const rowData = useMemo(() => {
    return new Array(rows).fill(null).map((_, rowIndex) => {
      const row: Record<string, string> = {};
      for (let colIndex = 0; colIndex < columns; colIndex += 1) {
        const key = `${rowIndex}:${colIndex}`;
        row[`col_${colIndex}`] = data[key]?.value ?? '';
      }
      return row;
    });
  }, [columns, data, rows]);

  const gridOptions: GridOptions = useMemo(
    () => ({
      rowSelection: 'single',
      suppressRowVirtualisation: false,
      suppressColumnVirtualisation: false,
      enableRangeSelection: true,
      suppressMenuHide: true,
      enableCellTextSelection: true,
      headerHeight: 28,
      rowHeight: 24,
      animateRows: false,
      rowDragManaged: false,
      suppressMovableColumns: true
    }),
    [],
  );

  const excelThemeOverrides: CSSProperties = {
    // @ts-expect-error CSS variable definitions are valid inline styles for AG Grid
    '--ag-foreground-color': '#1f2937',
    '--ag-header-background-color': '#f1f5f9',
    '--ag-alpine-active-color': '#217346',
  };

  const handleSelectionChange = (api: GridApi) => {
    const focusedCell = api.getFocusedCell();
    if (!focusedCell) return;
    const columnIndex = Number(focusedCell.column.getColId().replace('col_', ''));
    setSelection({
      anchor: { row: focusedCell.rowIndex ?? 0, col: columnIndex },
      focus: { row: focusedCell.rowIndex ?? 0, col: columnIndex }
    });
  };

  return (
    <div className="ag-theme-alpine h-full w-full" style={excelThemeOverrides}>
      <AgGridReact
        columnDefs={columnDefs}
        rowData={rowData}
        gridOptions={gridOptions}
        onCellClicked={(event) => handleSelectionChange(event.api)}
        onCellFocused={(event) => handleSelectionChange(event.api)}
        onSelectionChanged={(event) => handleSelectionChange(event.api)}
        onCellValueChanged={(event) => {
          const columnIndex = Number(event.column.getColId().replace('col_', ''));
          const rowIndex = event.node.rowIndex ?? 0;
          updateCell({ row: rowIndex, col: columnIndex }, () => ({ value: String(event.value ?? ''), formula: undefined }));
        }}
      />
    </div>
  );
};
