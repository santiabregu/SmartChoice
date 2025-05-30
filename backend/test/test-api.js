const axios = require('axios');

const API_URL = 'http://localhost:3000/api';

async function testAPI() {
  try {
    // 1. Crear una nueva reseña
    console.log('1. Creando nueva reseña...');
    const reviewData = {
      product: 'Smartphone XYZ',
      text: 'Este teléfono es excelente. La batería dura todo el día y la cámara toma fotos increíbles. Sin embargo, el precio es un poco alto.',
      rating: 4
    };

    console.log('Enviando datos:', reviewData);
    const createResponse = await axios.post(`${API_URL}/reviews`, reviewData);
    console.log('Reseña creada:', createResponse.data);
    const reviewId = createResponse.data._id;

    // 2. Buscar reseñas
    console.log('\n2. Buscando reseñas...');
    const searchResponse = await axios.get(`${API_URL}/reviews/search`, {
      params: {
        query: 'batería',
        minRating: 4
      }
    });
    console.log('Resultados de búsqueda:', searchResponse.data);

    // 3. Obtener estadísticas
    console.log('\n3. Obteniendo estadísticas...');
    const statsResponse = await axios.get(`${API_URL}/reviews/stats`);
    console.log('Estadísticas:', statsResponse.data);

    // 4. Obtener sugerencias
    console.log('\n4. Obteniendo sugerencias...');
    const suggestionsResponse = await axios.get(`${API_URL}/reviews/${reviewId}/suggestions`);
    console.log('Sugerencias:', suggestionsResponse.data);

  } catch (error) {
    console.error('Error en las pruebas:');
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('Response data:', error.response.data);
      console.error('Status code:', error.response.status);
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received from server');
      console.error(error.message);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Error setting up request:', error.message);
    }
  }
}

testAPI(); 