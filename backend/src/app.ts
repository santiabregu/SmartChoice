import express from 'express';
import cors from 'cors';
import axios, { AxiosError } from 'axios';
import { config } from 'dotenv';

config();

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

const PYTHON_SERVICE_URL = process.env.PYTHON_SERVICE_URL || 'http://localhost:8000';

// Proxy routes to Python service
app.post('/api/reviews', async (req, res) => {
  try {
    const response = await axios.post(`${PYTHON_SERVICE_URL}/process_review`, req.body);
    res.json(response.data);
  } catch (error) {
    const axiosError = error as AxiosError;
    res.status(axiosError.response?.status || 500).json({ 
      error: axiosError.response?.data || axiosError.message 
    });
  }
});

app.post('/api/search', async (req, res) => {
  try {
    const response = await axios.post(`${PYTHON_SERVICE_URL}/search`, req.body);
    res.json(response.data);
  } catch (error) {
    const axiosError = error as AxiosError;
    res.status(axiosError.response?.status || 500).json({ 
      error: axiosError.response?.data || axiosError.message 
    });
  }
});

app.get('/api/statistics', async (_req, res) => {
  try {
    const response = await axios.get(`${PYTHON_SERVICE_URL}/statistics`);
    res.json(response.data);
  } catch (error) {
    const axiosError = error as AxiosError;
    res.status(axiosError.response?.status || 500).json({ 
      error: axiosError.response?.data || axiosError.message 
    });
  }
});

export default app; 