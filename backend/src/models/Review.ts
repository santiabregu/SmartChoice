import { Schema, model, Document } from 'mongoose';

interface ISentimentAnalysis {
  overall: number;
  aspects: {
    [key: string]: number;
  };
}

export interface IReview extends Document {
  producto: string;
  categoria: string;
  resena: string;
  puntuacion: number;
  fecha: Date;
  sentimiento: ISentimentAnalysis;
  aspectos_clave: string[];
  resumen: string;
  metadata: {
    filename: string;
    processingDate: Date;
    aiModel: string;
  };
}

const ReviewSchema = new Schema<IReview>({
  producto: { type: String, required: true, index: true },
  categoria: { type: String, required: true, index: true },
  resena: { type: String, required: true },
  puntuacion: { type: Number, min: 0, max: 5 },
  fecha: { type: Date, default: Date.now },
  sentimiento: {
    overall: Number,
    aspects: {
      type: Map,
      of: Number
    }
  },
  aspectos_clave: [String],
  resumen: String,
  metadata: {
    filename: String,
    processingDate: Date,
    aiModel: String
  }
});

// Índices para búsqueda eficiente
ReviewSchema.index({ resena: 'text' });
ReviewSchema.index({ aspectos_clave: 1 });

export const Review = model<IReview>('Review', ReviewSchema); 