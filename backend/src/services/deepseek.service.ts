import { GoogleGenerativeAI, GenerativeModel } from '@google/generative-ai';
import dotenv from 'dotenv';

dotenv.config();

interface ReviewAnalysis {
  sentiment: string;
  aspects: string[];
  summary: string;
}

export class ReviewAnalysisService {
  private static readonly client = new GoogleGenerativeAI(process.env.GEMINI_API_KEY ?? '');
  private static readonly model: GenerativeModel = ReviewAnalysisService.client.getGenerativeModel({ 
    model: "gemini-pro",
    generationConfig: {
      maxOutputTokens: 300,
      temperature: 0.3
    }
  });

  /**
   * Analiza el sentimiento y aspectos clave de una reseña
   */
  static async analyzeReview(text: string): Promise<ReviewAnalysis> {
    try {
      const prompt = `
Analiza la siguiente reseña de producto y proporciona:
1. Sentimiento general (positivo, negativo, neutral)
2. Aspectos clave mencionados
3. Resumen breve

Reseña: "${text}"

Responde en formato JSON con esta estructura exacta:
{
  "sentiment": "positivo|negativo|neutral",
  "aspects": ["aspecto1", "aspecto2", ...],
  "summary": "resumen conciso"
}`;

      console.log('Enviando petición a Gemini...');
      
      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      console.log('Respuesta de Gemini:', response.text());

      const analysis = JSON.parse(response.text()) as ReviewAnalysis;
      
      return {
        sentiment: analysis.sentiment,
        aspects: analysis.aspects,
        summary: analysis.summary
      };
    } catch (error) {
      console.error('Error en el análisis de la reseña:', error);
      throw new Error('Error en el análisis de la reseña');
    }
  }

  /**
   * Genera sugerencias basadas en aspectos positivos y negativos
   */
  static async generateSuggestions(aspects: { positive: string[], negative: string[] }): Promise<string[]> {
    try {
      const prompt = `
Basado en estos aspectos de un producto:
Positivos: ${aspects.positive.join(', ')}
Negativos: ${aspects.negative.join(', ')}

Genera 3 sugerencias concretas de mejora.

Responde solo con las sugerencias, una por línea.`;

      const result = await this.model.generateContent(prompt);
      const response = await result.response;

      const suggestions = response.text()
        .split('\n')
        .filter((line: string) => line.trim().length > 0)
        .map((line: string) => `${line} 💡`);

      return suggestions;
    } catch (error) {
      console.error('Error al generar sugerencias:', error);
      throw new Error('Error al generar sugerencias');
    }
  }
} 