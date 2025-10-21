# Architecture Overview

This document captures the initial technical decisions for the Excel Expert Training System prototype. The goal is to provide a
scalable baseline that can evolve into the full specification.

## Frontend

- **Framework:** React 18 with TypeScript, powered by Vite for fast iteration.
- **Styling:** Tailwind CSS with Excel-inspired theming, supplemented by AG Grid for performant virtualized spreadsheet rendering.
- **State:** Zustand manages workbook state while leaving room for HyperFormula integration and undo/redo history.
- **Structure:**
  - `components/excel` contains the spreadsheet chrome (ribbon, name box, formula bar, grid).
  - `components/exercises` houses exercise-centric panels and future validation widgets.
  - `components/pages` delivers route-level views for landing, dashboard, and workspace experiences.

## Backend

- **Runtime:** Node.js with Express, configured for security via Helmet and CORS. Socket.IO prepares the foundation for collaborative scenarios.
- **APIs:** Initial endpoints surface health diagnostics and roadmap metadata. These will expand to handle authentication, workbook persistence, exercise evaluation, and analytics.
- **Extensibility:** TypeScript compilation targets modern ECMAScript while keeping strict type checks enabled.

## Cross-Cutting Concerns

- **Testing:** Scripts are provided for linting and unit testing (`eslint`, `vitest`), establishing the expectations for future coverage.
- **Configuration:** Environment variables are managed through `dotenv`, and the repository structure aligns with Docker-based deployment strategies described in the product brief.

This baseline should be treated as the first checkpoint toward the comprehensive certification training system.
