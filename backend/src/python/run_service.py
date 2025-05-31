import uvicorn
import nltk
import os
import ssl

# Configurar el directorio de datos de NLTK
nltk_data_dir = os.path.join(os.path.dirname(__file__), 'nltk_data')
os.makedirs(nltk_data_dir, exist_ok=True)
nltk.data.path.append(nltk_data_dir)

# Descargar recursos necesarios
def download_nltk_data():
    try:
        # Manejar problemas de SSL
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context

        # Descargar recursos
        resources = ['punkt', 'stopwords', 'wordnet', 'omw-1.4']
        for resource in resources:
            try:
                nltk.download(resource, download_dir=nltk_data_dir)
                print(f"Downloaded {resource}")
            except Exception as e:
                print(f"Error downloading {resource}: {e}")
    except Exception as e:
        print(f"Error in download_nltk_data: {e}")

if __name__ == "__main__":
    # Descargar datos de NLTK
    download_nltk_data()
    
    from text_service import app
    
    # Ejecutar servidor
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    ) 