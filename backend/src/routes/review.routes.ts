import { Router } from 'express';
import { ReviewController } from '../controllers/review.controller';

const router = Router();

// Obtener todas las reseñas
router.get('/', ReviewController.getAllReviews);

// Crear una nueva reseña
router.post('/', ReviewController.createReview);

// Buscar reseñas
router.get('/search', ReviewController.searchReviews);

// Obtener estadísticas
router.get('/stats', ReviewController.getStats);

// Obtener sugerencias para un producto
router.get('/:productId/suggestions', ReviewController.getSuggestions);

export const reviewRouter = router; 