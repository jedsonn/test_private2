# Excel Expert Training System Prototype

This repository establishes the initial project structure for a full-stack Excel Expert certification training platform. The implementation focuses on scaffolding a production-ready architecture that can grow into the fully featured system described in the product specification.

## Project Highlights

- **Frontend (React + TypeScript + Tailwind CSS):**
  - Excel-inspired workspace featuring ribbon navigation, name box, formula bar, and an AG Grid-powered spreadsheet prototype.
  - Exercise side panel that previews certification-aligned task delivery.
  - Roadmap dashboard communicating the phased delivery plan for core capabilities.

- **Backend (Node.js + Express):**
  - Hardened Express server configured with Helmet, CORS, and Socket.IO for future real-time collaboration features.
  - REST endpoints for health checks and roadmap metadata that align with the frontend dashboard.

- **State Management:**
  - Zustand store prepared to manage workbook data, selections, and future formula evaluation integration via HyperFormula.

## Getting Started

The project is organized as a polyrepo structure with dedicated `frontend` and `backend` directories. Each application exposes familiar npm scripts for development, testing, and production builds.

```bash
# Install dependencies
(cd frontend && npm install)
(cd backend && npm install)

# Start development servers
tmux \ 
  new-session "cd backend && npm run dev" \;
  split-window "cd frontend && npm run dev"
```

Once both servers are running, open `http://localhost:3000` to explore the Excel workspace prototype. The frontend expects the backend to be available at `http://localhost:5000` for roadmap data.

## Next Steps

- Integrate HyperFormula-driven recalculation and validation logic.
- Expand the workbook model to persist formatting, validation, and collaborative editing state.
- Implement the exercise evaluation pipeline defined in the specification, including scoring and feedback.
- Extend the instructor analytics dashboard and exercise authoring tools.

Refer to the `/docs` directory for upcoming technical and instructional documentation.
