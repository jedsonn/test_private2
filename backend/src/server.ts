import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { createServer } from 'http';
import { Server as SocketIOServer } from 'socket.io';

const app = express();
app.use(cors());
app.use(express.json());
app.use(helmet());

const apiRouter = express.Router();

apiRouter.get('/health', (_req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

apiRouter.get('/roadmap', (_req, res) => {
  res.json({
    phases: [
      { id: 'phase-1', title: 'Core Excel Engine', status: 'in-progress' },
      { id: 'phase-2', title: 'Exercise System', status: 'planned' },
      { id: 'phase-3', title: 'Student & Instructor Experience', status: 'planned' }
    ]
  });
});

app.use('/api', apiRouter);

const httpServer = createServer(app);
const io = new SocketIOServer(httpServer, {
  cors: {
    origin: '*'
  }
});

io.on('connection', (socket) => {
  socket.emit('status', { message: 'Connected to Excel training prototype channel.' });
});

const port = Number(process.env.PORT ?? 5000);
httpServer.listen(port, () => {
  // eslint-disable-next-line no-console
  console.log(`Backend listening on port ${port}`);
});
