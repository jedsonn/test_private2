import { useMemo } from 'react';
import { ExcelWorkspace } from '../excel/ExcelWorkspace';
import { ExercisePanel } from '../exercises/ExercisePanel';

const sampleExercise = {
  title: 'VLOOKUP Fundamentals',
  description: 'Build a lookup solution that retrieves employee records based on an ID reference. This exercise demonstrates how the workspace will deliver certification-aligned objectives.',
  estimatedTime: 15,
  tasks: [
    { id: 'task-1', instruction: 'Enter employee IDs and departments in the data table (A2:D11).' },
    { id: 'task-2', instruction: 'Use VLOOKUP in cell G2 to return the employee name for the ID in G1.' },
    { id: 'task-3', instruction: 'Configure G4 with a currency number format for salary presentation.' }
  ]
};

export const ExerciseWorkspacePage = () => {
  const exercise = useMemo(() => sampleExercise, []);

  return (
    <section className="flex h-full w-full">
      <div className="flex-1">
        <ExcelWorkspace />
      </div>
      <ExercisePanel {...exercise} />
    </section>
  );
};
