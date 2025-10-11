# =============================================================================
#  Filename: training_data.py
#
#  Short Description: Modular training data for VannaAI SQL generation
#
#  Creation date: 2025-10-11
#  Author: Shrinivas Deshpande
# =============================================================================

"""
Training Data Module

Centralized, modular training examples for VannaAI.
All SQL query examples organized by category for easy maintenance.
"""

from typing import List, Dict


class VannaTrainingData:
    """Centralized training data for VannaAI SQL generation."""
    
    # =========================================================================
    # Category 1: Cheapest Rate Queries
    # =========================================================================
    
    CHEAPEST_RATE_EXAMPLES: List[Dict[str, str]] = [
        {
            "question": "What is the cheapest rate for Zone 3?",
            "sql": "SELECT MIN(FedEx_Express_Saver) FROM fedex_rates WHERE Zone = 3;"
        },
        {
            "question": "Find the cheapest Express Saver rate for Zone 3",
            "sql": "SELECT MIN(FedEx_Express_Saver) as cheapest_rate FROM fedex_rates WHERE Zone = 3;"
        },
        {
            "question": "What is the cheapest rate for Zone 5?",
            "sql": "SELECT MIN(FedEx_Express_Saver) as cheapest_rate FROM fedex_rates WHERE Zone = 5 AND FedEx_Express_Saver IS NOT NULL;"
        },
        {
            "question": "Find the cheapest shipping option for Zone 3",
            "sql": "SELECT MIN(FedEx_Express_Saver) as cheapest_rate FROM fedex_rates WHERE Zone = 3 AND FedEx_Express_Saver IS NOT NULL;"
        },
        {
            "question": "What's the lowest cost service for Zone 7?",
            "sql": "SELECT MIN(FedEx_Express_Saver) as lowest_cost FROM fedex_rates WHERE Zone = 7 AND FedEx_Express_Saver IS NOT NULL;"
        },
        {
            "question": "Show the most economical rate for Zone 4",
            "sql": "SELECT MIN(FedEx_Express_Saver) as economical_rate FROM fedex_rates WHERE Zone = 4 AND FedEx_Express_Saver IS NOT NULL;"
        },
        {
            "question": "What's the best value shipping for Zone 6?",
            "sql": "SELECT MIN(FedEx_Express_Saver) as best_value FROM fedex_rates WHERE Zone = 6 AND FedEx_Express_Saver IS NOT NULL;"
        },
        {
            "question": "What's the most affordable option for Zone 8?",
            "sql": "SELECT MIN(FedEx_Express_Saver) as most_affordable FROM fedex_rates WHERE Zone = 8 AND FedEx_Express_Saver IS NOT NULL;"
        },
    ]
    
    # =========================================================================
    # Category 2: Specific Weight and Zone Queries
    # =========================================================================
    
    WEIGHT_ZONE_EXAMPLES: List[Dict[str, str]] = [
        {
            "question": "What are the rates for Zone 3 packages under 10 pounds?",
            "sql": "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 3 AND Weight <= 10;"
        },
        {
            "question": "Show rates for Zone 3 under 10 lbs",
            "sql": "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 3 AND Weight <= 10;"
        },
        {
            "question": "What are all the rates for Zone 2?",
            "sql": "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 2;"
        },
        {
            "question": "Show all rates for Zone 4, 25 lbs",
            "sql": "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 4 AND Weight = 25;"
        },
        {
            "question": "Show rates for all zones at 25 pounds",
            "sql": "SELECT Zone, Weight, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Weight = 25 ORDER BY Zone;"
        },
    ]
    
    # =========================================================================
    # Category 3: Specific Service Queries
    # =========================================================================
    
    SPECIFIC_SERVICE_EXAMPLES: List[Dict[str, str]] = [
        {
            "question": "Show Priority Overnight rates for Zone 5",
            "sql": "SELECT Zone, Weight, FedEx_Priority_Overnight FROM fedex_rates WHERE Zone = 5 ORDER BY Weight;"
        },
        {
            "question": "What is the FedEx 2Day rate for Zone 2, 10 lbs?",
            "sql": "SELECT Zone, Weight, FedEx_2Day FROM fedex_rates WHERE Zone = 2 AND Weight = 10;"
        },
        {
            "question": "Show the top 3 cheapest FedEx 2Day rates",
            "sql": "SELECT Zone, Weight, FedEx_2Day FROM fedex_rates WHERE FedEx_2Day IS NOT NULL ORDER BY FedEx_2Day ASC LIMIT 3;"
        },
        {
            "question": "What is rate for 4 lbs package to zone 6 that delivers next day 9 am?",
            "sql": "SELECT FedEx_First_Overnight FROM fedex_rates WHERE Zone = 6 AND Weight = 4 AND FedEx_First_Overnight IS NOT NULL;"
        },
    ]
    
    # =========================================================================
    # Category 4: Complex Queries with Budget/Comparison
    # =========================================================================
    
    BUDGET_COMPARISON_EXAMPLES: List[Dict[str, str]] = [
        {
            "question": "Ship 15 lbs to Zone 8 within $200 budget",
            "sql": "SELECT Zone, Weight, FedEx_Express_Saver, FedEx_2Day, FedEx_2Day_AM FROM fedex_rates WHERE Zone = 8 AND Weight = 15;"
        },
        {
            "question": "Show all rates for 15 lbs to Zone 8",
            "sql": "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 8 AND Weight = 15;"
        },
        {
            "question": "Find rates for Zone 5, 10 lbs, budget $100",
            "sql": "SELECT Zone, Weight, FedEx_Express_Saver, FedEx_2Day FROM fedex_rates WHERE Zone = 5 AND Weight = 10;"
        },
        {
            "question": "What's the cheapest service for Zone 6, 15 lbs?",
            "sql": "SELECT Zone, Weight, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 6 AND Weight = 15;"
        },
        {
            "question": "Show the cheapest rate for each zone at 15 lbs",
            "sql": "SELECT Zone, Weight, MIN(FedEx_Express_Saver) as cheapest_rate FROM fedex_rates WHERE Weight = 15 GROUP BY Zone ORDER BY Zone;"
        },
        {
            "question": "What is cheapest rate for 10lbs for zone 5?",
            "sql": "SELECT Zone, Weight, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 5 AND Weight = 10;"
        },
        {
            "question": "What is the cheapest rate for Zone 5?",
            "sql": "SELECT Zone, Weight, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 5 AND Weight = 10;"
        },
        {
            "question": "Find the cheapest shipping option for Zone 3",
            "sql": "SELECT Zone, Weight, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 3 AND Weight = 10;"
        },
        {
            "question": "What's the lowest cost service for Zone 7?",
            "sql": "SELECT Zone, Weight, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 7 AND Weight = 10;"
        },
        {
            "question": "I want to send 5 lbs package from San Francisco to New York. I have budget of 100$. Whats my best option",
            "sql": "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 8 AND Weight = 5;"
        },
        {
            "question": "Send 10 lbs to Chicago with $150 budget",
            "sql": "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 8 AND Weight = 10;"
        },
        {
            "question": "Package weighing 15 lbs to Boston, budget $200",
            "sql": "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 7 AND Weight = 15;"
        },
        {
            "question": "I want to send 30lbs from Fremont, CA to San Francisco, CA. What are the cheapest, fastest services?",
            "sql": "SELECT Zone, Weight, FedEx_Express_Saver, FedEx_2Day, FedEx_Standard_Overnight FROM fedex_rates WHERE Zone = 2 AND Weight = 30;"
        },
        {
            "question": "Send 30 lbs package what are my options",
            "sql": "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight, FedEx_2Day_AM, FedEx_2Day, FedEx_Express_Saver FROM fedex_rates WHERE Weight = 30 ORDER BY Zone;"
        },
        {
            "question": "Ship 25 lbs from Los Angeles to San Diego, need cheap and fast",
            "sql": "SELECT Zone, Weight, FedEx_Express_Saver, FedEx_2Day, FedEx_Standard_Overnight FROM fedex_rates WHERE Zone = 2 AND Weight = 25;"
        },
    ]
    
    # =========================================================================
    # Category 5: Aggregate and Statistical Queries
    # =========================================================================
    
    AGGREGATE_EXAMPLES: List[Dict[str, str]] = [
        {
            "question": "What are the average rates for each zone?",
            "sql": "SELECT Zone, ROUND(AVG(FedEx_2Day), 2) as avg_2day_rate, ROUND(AVG(FedEx_Express_Saver), 2) as avg_express_saver FROM fedex_rates GROUP BY Zone ORDER BY Zone;"
        },
        {
            "question": "Find the top 3 cheapest 2Day rates across all zones",
            "sql": "SELECT Zone, Weight, FedEx_2Day FROM fedex_rates WHERE FedEx_2Day IS NOT NULL ORDER BY FedEx_2Day ASC LIMIT 3;"
        },
    ]
    
    # =========================================================================
    # Category 6: Real-World Shipping Scenarios
    # =========================================================================
    
    REAL_WORLD_EXAMPLES: List[Dict[str, str]] = [
        {
            "question": "Ship 15 lbs from CA to NY budget $200",
            "sql": "SELECT Zone, Weight, FedEx_Express_Saver, FedEx_2Day, FedEx_2Day_AM, FedEx_Standard_Overnight FROM fedex_rates WHERE Zone = 8 AND Weight = 15;"
        },
        {
            "question": "Send 1 lb document from San Francisco to Los Angeles cheapest option",
            "sql": "SELECT Zone, Weight, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 2 AND Weight = 1;"
        },
        {
            "question": "Overnight delivery 20 lbs to New York",
            "sql": "SELECT Zone, Weight, FedEx_First_Overnight, FedEx_Priority_Overnight, FedEx_Standard_Overnight FROM fedex_rates WHERE Zone = 8 AND Weight = 20;"
        },
        {
            "question": "2-day shipping 30 lbs to Chicago",
            "sql": "SELECT Zone, Weight, FedEx_2Day, FedEx_2Day_AM FROM fedex_rates WHERE Zone = 5 AND Weight = 30;"
        },
        {
            "question": "Cheapest way to ship 5 lbs to Boston",
            "sql": "SELECT Zone, Weight, FedEx_Express_Saver FROM fedex_rates WHERE Zone = 7 AND Weight = 5;"
        },
    ]
    
    # =========================================================================
    # Consolidated Training Data
    # =========================================================================
    
    @classmethod
    def get_all_examples(cls) -> List[Dict[str, str]]:
        """
        Get all training examples combined.
        
        Returns:
            List of all training examples across all categories
        """
        return (
            cls.CHEAPEST_RATE_EXAMPLES +
            cls.WEIGHT_ZONE_EXAMPLES +
            cls.SPECIFIC_SERVICE_EXAMPLES +
            cls.BUDGET_COMPARISON_EXAMPLES +
            cls.AGGREGATE_EXAMPLES +
            cls.REAL_WORLD_EXAMPLES
        )
    
    @classmethod
    def get_examples_by_category(cls, category: str) -> List[Dict[str, str]]:
        """
        Get training examples for a specific category.
        
        Args:
            category: Category name (e.g., 'cheapest', 'weight_zone', etc.)
            
        Returns:
            List of training examples for that category
        """
        categories = {
            'cheapest': cls.CHEAPEST_RATE_EXAMPLES,
            'weight_zone': cls.WEIGHT_ZONE_EXAMPLES,
            'specific_service': cls.SPECIFIC_SERVICE_EXAMPLES,
            'budget': cls.BUDGET_COMPARISON_EXAMPLES,
            'aggregate': cls.AGGREGATE_EXAMPLES,
            'real_world': cls.REAL_WORLD_EXAMPLES,
        }
        return categories.get(category, [])
    
    @classmethod
    def get_training_count(cls) -> Dict[str, int]:
        """
        Get count of training examples by category.
        
        Returns:
            Dictionary with category names and counts
        """
        return {
            'cheapest_rate': len(cls.CHEAPEST_RATE_EXAMPLES),
            'weight_zone': len(cls.WEIGHT_ZONE_EXAMPLES),
            'specific_service': len(cls.SPECIFIC_SERVICE_EXAMPLES),
            'budget_comparison': len(cls.BUDGET_COMPARISON_EXAMPLES),
            'aggregate': len(cls.AGGREGATE_EXAMPLES),
            'real_world': len(cls.REAL_WORLD_EXAMPLES),
            'total': len(cls.get_all_examples())
        }


# Convenience function
def get_all_training_examples() -> List[Dict[str, str]]:
    """Get all training examples for VannaAI."""
    return VannaTrainingData.get_all_examples()


# Print summary when run as script
if __name__ == "__main__":
    counts = VannaTrainingData.get_training_count()
    print("VannaAI Training Data Summary")
    print("=" * 60)
    print(f"Cheapest Rate Examples: {counts['cheapest_rate']}")
    print(f"Weight & Zone Examples: {counts['weight_zone']}")
    print(f"Specific Service Examples: {counts['specific_service']}")
    print(f"Budget Comparison Examples: {counts['budget_comparison']}")
    print(f"Aggregate Examples: {counts['aggregate']}")
    print(f"Real-World Examples: {counts['real_world']}")
    print("-" * 60)
    print(f"TOTAL EXAMPLES: {counts['total']}")
    print("=" * 60)
    
    print("\nSample Examples:")
    print("-" * 60)
    for i, example in enumerate(VannaTrainingData.get_all_examples()[:3], 1):
        print(f"\n{i}. Question: {example['question']}")
        print(f"   SQL: {example['sql'][:80]}...")

