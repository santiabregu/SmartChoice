import { Schema, model, Document } from 'mongoose';

export interface IReview extends Document {
  product: string;
  text: string;
  rating: number;
  sentiment: 'positivo' | 'negativo' | 'neutral';
  aspects: string[];
  summary: string;
  createdAt: Date;
}

const reviewSchema = new Schema<IReview>({
  product: {
    type: String,
    required: true,
    index: true
  },
  text: {
    type: String,
    required: true,
    text: true // Habilitar búsqueda de texto
  },
  rating: {
    type: Number,
    required: true,
    min: 1,
    max: 5
  },
  sentiment: {
    type: String,
    enum: ['positivo', 'negativo', 'neutral'],
    required: true
  },
  aspects: [{
    type: String
  }],
  summary: {
    type: String,
    required: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

// Crear índice de texto para búsqueda
reviewSchema.index({ text: 'text', summary: 'text' });

export default model<IReview>('Review', reviewSchema); 