import os
import nltk
import ssl

def setup_nltk():
    """
    Set up NLTK data in a local directory
    """
    # Create nltk_data directory if it doesn't exist
    nltk_data_dir = os.path.join(os.path.dirname(__file__), 'nltk_data')
    os.makedirs(nltk_data_dir, exist_ok=True)
    
    # Set NLTK data path
    nltk.data.path.append(nltk_data_dir)
    
    # Required NLTK downloads
    required_packages = [
        'punkt',
        'stopwords',
        'wordnet',
        'omw-1.4',  # Open Multilingual Wordnet
        'averaged_perceptron_tagger'
    ]
    
    try:
        # Handle SSL certificate issues
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context
        
        # Download required packages
        for package in required_packages:
            try:
                nltk.download(package, download_dir=nltk_data_dir, quiet=True)
                print(f"Successfully downloaded {package}")
            except Exception as e:
                print(f"Error downloading {package}: {str(e)}")
                
    except Exception as e:
        print(f"Error during NLTK setup: {str(e)}")
        raise

if __name__ == "__main__":
    setup_nltk() 