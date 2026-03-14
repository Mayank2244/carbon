import numpy as np
from scipy import stats

def perform_statistical_tests(cs_results, baseline_results):
    """
    Perform comprehensive statistical testing to validate results.
    
    Args:
        cs_results (list): List of dictionaries containing CarbonSense metrics.
        baseline_results (list): List of dictionaries containing baseline metrics.
        
    Returns:
        dict: Statistical metrics and significance results.
    """
    # Extract carbon data
    cs_carbon = [r['carbon'] for r in cs_results]
    baseline_carbon = [r['carbon'] for r in baseline_results]
    
    # Extract satisfaction data
    cs_satisfaction = [r['satisfaction'] for r in cs_results]
    baseline_satisfaction = [r['satisfaction'] for r in baseline_results]
    
    # T-test for carbon reduction
    carbon_ttest = stats.ttest_ind(cs_carbon, baseline_carbon)
    
    # T-test for user satisfaction
    quality_ttest = stats.ttest_ind(cs_satisfaction, baseline_satisfaction)
    
    # Cohen's d effect size for carbon
    cs_carbon_mean = np.mean(cs_carbon)
    baseline_carbon_mean = np.mean(baseline_carbon)
    pooled_std = np.sqrt((np.std(cs_carbon, ddof=1)**2 + np.std(baseline_carbon, ddof=1)**2) / 2)
    cohens_d = (cs_carbon_mean - baseline_carbon_mean) / pooled_std
    
    # Confidence intervals (95%) for CarbonSense Carbon
    cs_carbon_ci = stats.t.interval(
        0.95,
        len(cs_carbon) - 1,
        loc=cs_carbon_mean,
        scale=stats.sem(cs_carbon)
    )
    
    return {
        'carbon_pvalue': float(carbon_ttest.pvalue),
        'carbon_significant': bool(carbon_ttest.pvalue < 0.05),
        'quality_pvalue': float(quality_ttest.pvalue),
        'quality_significant': bool(quality_ttest.pvalue < 0.05),
        'effect_size': float(cohens_d),
        'effect_interpretation': interpret_cohens_d(cohens_d),
        'carbon_ci_95': [float(ci) for ci in cs_carbon_ci]
    }

def interpret_cohens_d(d):
    """Interpret Cohen's d effect size"""
    abs_d = abs(d)
    if abs_d < 0.2:
        return "negligible"
    elif abs_d < 0.5:
        return "small"
    elif abs_d < 0.8:
        return "medium"
    else:
        return "large"

def calculate_confidence_intervals(data, confidence=0.95):
    """Calculate confidence intervals for a dataset."""
    n = len(data)
    m, se = np.mean(data), stats.sem(data)
    h = se * stats.t.ppf((1 + confidence) / 2., n-1)
    return m, m-h, m+h
