import { Schema, model, Document } from 'mongoose';

interface ITextAnalysis {
  tokens: string[];
  lemmatized: string[];
  stems: string[];
  tf_idf_vector?: { [term: string]: number };
}

export interface IReview extends Document {
  producto: string;
  categoria: string;
  resena: string;
  puntuacion: number;
  fecha: Date;
  website: {
    url: string;
    nombre: string;
    fecha_extraccion: Date;
  };
  analisis_texto: ITextAnalysis;
  metadata: {
    filename: string;
    processingDate: Date;
    language: string;
  };
}

const ReviewSchema = new Schema<IReview>({
  producto: { type: String, required: true, index: true },
  categoria: { type: String, required: true, index: true },
  resena: { type: String, required: true },
  puntuacion: { type: Number, min: 0, max: 5 },
  fecha: { type: Date, default: Date.now },
  website: {
    url: { type: String, required: true },
    nombre: { type: String, required: true },
    fecha_extraccion: { type: Date, default: Date.now }
  },
  analisis_texto: {
    tokens: [String],
    lemmatized: [String],
    stems: [String],
    tf_idf_vector: { type: Map, of: Number }
  },
  metadata: {
    filename: String,
    processingDate: { type: Date, default: Date.now },
    language: { type: String, default: 'es' }
  }
});

// Índices para búsqueda eficiente
ReviewSchema.index({ resena: 'text' });
ReviewSchema.index({ 'analisis_texto.tokens': 1 });
ReviewSchema.index({ 'analisis_texto.lemmatized': 1 });
ReviewSchema.index({ 'website.url': 1 });
ReviewSchema.index({ 'website.nombre': 1 });

export const Review = model<IReview>('Review', ReviewSchema); 