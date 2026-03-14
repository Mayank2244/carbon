"""
Tests for Advanced Features (A/B Testing & Auto-tuning)
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from app.modules.model_selector import (
    ABTestManager,
    ABTestResult,
    ThresholdTuner,
    ModelConfig,
    ModelTier
)


class TestABTesting:
    """Test cases for ABTestManager."""
    
    def test_initialization(self):
        """Test manager initialization."""
        manager = ABTestManager(experiment_rate=0.5)
        assert manager.experiment_rate == 0.5
        assert len(manager.results) == 0
    
    def test_should_run_test(self):
        """Test probabilistic test trigger."""
        manager = ABTestManager(experiment_rate=1.0)  # Always run
        assert manager.should_run_test("query") is True
        
        manager = ABTestManager(experiment_rate=0.0)  # Never run
        assert manager.should_run_test("query") is False
    
    def test_evaluate_comparison(self):
        """Test comparison evaluation."""
        manager = ABTestManager()
        
        # Mock configs
        config_a = Mock(spec=ModelConfig)
        config_a.name = "ModelA"
        config_a.tier = ModelTier.SMALL
        config_a.carbon_per_1k_tokens = 2.0
        
        config_b = Mock(spec=ModelConfig)
        config_b.name = "ModelB"
        config_b.tier = ModelTier.MEDIUM
        config_b.carbon_per_1k_tokens = 8.0
        
        # Mock evaluator
        manager.quality_evaluator = Mock()
        manager.quality_evaluator.evaluate.side_effect = [
            Mock(overall_score=0.8),  # A
            Mock(overall_score=0.9)   # B
        ]
        
        result = manager.evaluate_comparison(
            query="test",
            result_a={'text': "A", 'latency': 100},
            result_b={'text': "B", 'latency': 200},
            model_config_a=config_a,
            model_config_b=config_b
        )
        
        assert isinstance(result, ABTestResult)
        assert result.winner == 'tie'  # 0.1 difference within margin
        assert len(manager.results) == 1


class TestThresholdTuner:
    """Test cases for ThresholdTuner."""
    
    def test_initialization(self):
        """Test tuner initialization."""
        tuner = ThresholdTuner(initial_threshold=0.7)
        assert tuner.current_threshold == 0.7
    
    def test_update_window(self):
        """Test history update window."""
        tuner = ThresholdTuner(window_size=5)
        
        for i in range(10):
            tuner.update(0.8, False)
            
        assert len(tuner.history) == 5
    
    def test_tuning_logic(self):
        """Test threshold adjustment logic."""
        tuner = ThresholdTuner(
            initial_threshold=0.7,
            window_size=5,
            learning_rate=0.1
        )
        
        # Simulate high escalation -> should lower threshold
        for _ in range(5):
            tuner.update(0.6, True)  # Escalated
            
        # Tuner logic: 100% escalation > 10% target -> lower threshold
        assert tuner.current_threshold < 0.7
        
        # Simulate low escalation -> should raise threshold
        for _ in range(5):
            tuner.update(0.9, False)  # Not escalated
            
        # Tuner logic: 0% escalation < 10% target -> raise threshold
        assert tuner.current_threshold > 0.6  # Should have bounced back up


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
