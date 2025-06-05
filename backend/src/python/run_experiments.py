from experiments import ExperimentRunner
import json
import os
from pathlib import Path

def main():
    # Initialize the experiment runner
    runner = ExperimentRunner()
    
    # Load information needs
    with open(os.path.join(os.path.dirname(__file__), 'data/necesidades_informacion.json'), 'r', encoding='utf-8') as f:
        necesidades = json.load(f)['necesidades']
    
    print(f"\nLoaded {len(necesidades)} information needs")
    
    # Run timing experiments for each need
    timing_results = {
        'boolean_search': [],
        'tfidf_search': []
    }
    
    for need in necesidades:
        print(f"\nProcessing need {need['id']}: {need['descripcion']}")
        
        # Boolean search timing
        bool_results = runner.run_timing_experiments(
            queries=[need['consulta_booleana']],
            search_type='boolean'
        )
        timing_results['boolean_search'].extend(bool_results['boolean_search'])
        
        # TF-IDF search timing
        tfidf_results = runner.run_timing_experiments(
            queries=[need['consulta_libre']],
            search_type='tf_idf'
        )
        timing_results['tfidf_search'].extend(tfidf_results['tfidf_search'])
    
    # Save timing results
    runner._save_results('timing_experiments.json', timing_results)
    
    # Run synonym impact analysis
    print("\nAnalyzing synonym impact...")
    synonym_results = runner.evaluate_synonym_impact(necesidades)
    runner._save_results('synonym_impact.json', synonym_results)
    
    # Run threshold analysis
    print("\nAnalyzing threshold impact...")
    threshold_results = runner.analyze_thresholds(necesidades)
    runner._save_results('threshold_analysis.json', threshold_results)
    
    print("\nAll experiments completed. Results saved in experiment_results/")

if __name__ == "__main__":
    main() 