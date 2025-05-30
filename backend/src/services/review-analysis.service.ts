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
    model: "gemini-2.5-flash-preview-05-20",
    generationConfig: {
      maxOutputTokens: 1024,
      temperature: 0.3,
      topP: 0.8,
      topK: 40
    }
  });

  /**
   * Analiza el sentimiento y aspectos clave de una reseña
   */
  static async analyzeReview(text: string): Promise<ReviewAnalysis> {
    try {
      if (!text || typeof text !== 'string') {
        throw new Error('El texto de la reseña es inválido');
      }

      const prompt = `Tu tarea es analizar la siguiente reseña y devolver un objeto JSON con un formato específico.

Reseña: "${text}"

Instrucciones:
1. Analiza el sentimiento general (DEBE ser exactamente "positivo", "negativo" o "neutral")
2. Identifica aspectos clave mencionados (palabras o frases cortas del texto)
3. Crea un resumen breve

IMPORTANTE: 
- Debes responder SOLAMENTE con un objeto JSON válido
- No incluyas explicaciones ni texto adicional
- Usa exactamente esta estructura:

{
  "sentiment": "positivo",
  "aspects": ["aspecto1", "aspecto2"],
  "summary": "resumen breve"
}`;

      console.log('Enviando prompt a Gemini:', prompt);
      
      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const responseText = response.text().trim();
      
      console.log('Respuesta cruda de Gemini:', responseText);

      // Intentar extraer JSON si la respuesta contiene texto adicional
      let jsonStr = responseText;
      const jsonMatch = responseText.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        jsonStr = jsonMatch[0];
        console.log('JSON extraído de la respuesta:', jsonStr);
      }

      try {
        const analysis = JSON.parse(jsonStr) as ReviewAnalysis;
        
        // Validar y normalizar la respuesta
        if (!analysis.sentiment || !Array.isArray(analysis.aspects) || !analysis.summary) {
          console.error('Respuesta con formato inválido:', analysis);
          throw new Error('La respuesta no contiene todos los campos requeridos');
        }

        // Normalizar el sentimiento
        analysis.sentiment = analysis.sentiment.toLowerCase().trim();
        if (!['positivo', 'negativo', 'neutral'].includes(analysis.sentiment)) {
          console.log(`Normalizando sentimiento inválido "${analysis.sentiment}" a "neutral"`);
          analysis.sentiment = 'neutral';
        }

        // Normalizar aspects
        analysis.aspects = analysis.aspects
          .filter(aspect => typeof aspect === 'string' && aspect.trim().length > 0)
          .map(aspect => aspect.trim());

        if (analysis.aspects.length === 0) {
          analysis.aspects = ['general'];
        }

        // Normalizar summary
        analysis.summary = analysis.summary.trim();
        if (!analysis.summary) {
          analysis.summary = 'No se proporcionó resumen';
        }
        
        console.log('Análisis normalizado:', analysis);
        return analysis;

      } catch (parseError: any) {
        console.error('Error al parsear la respuesta de Gemini:', parseError);
        console.error('Respuesta que causó el error:', responseText);
        throw new Error(`Error al procesar la respuesta de Gemini: ${parseError?.message || 'Error desconocido'}`);
      }
    } catch (error) {
      console.error('Error en el análisis de la reseña:', error);
      throw error;
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
Cada sugerencia debe ser específica y accionable.
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