import { Request, Response } from 'express';
import Review, { IReview } from '../models/review.model';
import multer, { FileFilterCallback } from 'multer';
import path from 'path';
import fs from 'fs/promises';
import { ReviewAnalysisService } from '../services/review-analysis.service';

// Configurar multer para la subida de archivos
const storage = multer.diskStorage({
  destination: './uploads/',
  filename: (req: Request, file: Express.Multer.File, cb: (error: Error | null, filename: string) => void) => {
    cb(null, `${Date.now()}-${file.originalname}`);
  }
});

export const upload = multer({ 
  storage,
  fileFilter: (req: Request, file: Express.Multer.File, cb: FileFilterCallback) => {
    if (file.mimetype === 'text/plain') {
      cb(null, true);
    } else {
      cb(new Error('Solo se permiten archivos .txt'));
    }
  }
});

export class ReviewController {
  /**
   * Procesa y guarda una nueva reseña
   */
  static async createReview(req: Request, res: Response): Promise<void> {
    try {
      const { text, product, rating } = req.body;

      // Validar campos requeridos
      if (!text) {
        res.status(400).json({ error: 'El texto de la reseña es requerido' });
        return;
      }

      console.log('Procesando reseña:', { text, product, rating });

      // Analizar la reseña con Gemini
      const analysis = await ReviewAnalysisService.analyzeReview(text);
      
      console.log('Análisis completado:', analysis);

      // Crear nueva reseña con el análisis
      const review = new Review({
        product,
        text,
        rating,
        sentiment: analysis.sentiment,
        aspects: analysis.aspects,
        summary: analysis.summary
      });

      await review.save();

      res.status(201).json(review);
    } catch (error) {
      console.error('Error detallado al crear reseña:', error);
      
      // Determinar si es un error de validación o un error del servicio
      if (error instanceof Error) {
        res.status(500).json({ 
          error: 'Error al procesar la reseña',
          details: error.message,
          stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
        });
      } else {
        res.status(500).json({ 
          error: 'Error al procesar la reseña',
          details: 'Error desconocido'
        });
      }
    }
  }

  /**
   * Busca reseñas por criterios
   */
  static async searchReviews(req: Request, res: Response): Promise<void> {
    try {
      const { query, sentiment, minRating } = req.query;
      
      const searchCriteria: Record<string, any> = {};
      
      if (query) {
        searchCriteria.$text = { $search: query as string };
      }
      
      if (sentiment) {
        searchCriteria.sentiment = sentiment;
      }
      
      if (minRating) {
        searchCriteria.rating = { $gte: Number(minRating) };
      }

      const reviews = await Review.find(searchCriteria)
        .sort({ createdAt: -1 })
        .limit(20);

      res.json(reviews);
    } catch (error) {
      console.error('Error en búsqueda:', error);
      res.status(500).json({ error: 'Error al buscar reseñas' });
    }
  }

  /**
   * Obtiene estadísticas de reseñas
   */
  static async getStats(req: Request, res: Response): Promise<void> {
    try {
      const stats = await Review.aggregate([
        {
          $group: {
            _id: null,
            totalReviews: { $sum: 1 },
            avgRating: { $avg: '$rating' },
            sentimentCounts: {
              $push: '$sentiment'
            }
          }
        }
      ]);

      const sentimentDistribution = stats[0].sentimentCounts.reduce((acc: Record<string, number>, sentiment: string) => {
        acc[sentiment] = (acc[sentiment] || 0) + 1;
        return acc;
      }, {});

      res.json({
        totalReviews: stats[0].totalReviews,
        averageRating: stats[0].avgRating,
        sentimentDistribution
      });
    } catch (error) {
      console.error('Error al obtener estadísticas:', error);
      res.status(500).json({ error: 'Error al obtener estadísticas' });
    }
  }

  /**
   * Obtiene sugerencias basadas en reseñas
   */
  static async getSuggestions(req: Request, res: Response): Promise<void> {
    try {
      const { productId } = req.params;

      // Obtener aspectos positivos y negativos de las reseñas
      const reviews = await Review.find({ product: productId });
      
      const aspects = reviews.reduce((acc: { positive: string[], negative: string[] }, review: IReview) => {
        if (review.sentiment === 'positivo') {
          acc.positive.push(...(review.aspects || []));
        } else if (review.sentiment === 'negativo') {
          acc.negative.push(...(review.aspects || []));
        }
        return acc;
      }, { positive: [], negative: [] });

      // Generar sugerencias usando Gemini
      const suggestions = await ReviewAnalysisService.generateSuggestions(aspects);

      res.json({ suggestions });
    } catch (error) {
      console.error('Error al generar sugerencias:', error);
      res.status(500).json({ error: 'Error al generar sugerencias' });
    }
  }

  /**
   * Obtiene todas las reseñas
   */
  static async getAllReviews(req: Request, res: Response): Promise<void> {
    try {
      const reviews = await Review.find()
        .sort({ createdAt: -1 })
        .limit(20);
      res.json(reviews);
    } catch (error) {
      console.error('Error al obtener reseñas:', error);
      res.status(500).json({ error: 'Error al obtener reseñas' });
    }
  }
} 