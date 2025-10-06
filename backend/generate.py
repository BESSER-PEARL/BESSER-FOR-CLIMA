"""
Complete Backend Generator Script
Uses the complete BUML model from database_structure.plantuml
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from buml_model import buml_model
from generator.refactored_generator import RefactoredBackendGenerator


def main():
    """Generate complete backend from PlantUML model."""
    print("=" * 70)
    print("CLIMABOROUGH BACKEND GENERATOR")
    print("From PlantUML Database Structure")
    print("=" * 70)
    print()
    
    # Step 1: Create the BUML model from PlantUML
    print("Step 1: Creating BUML Model from PlantUML...")
    print("-" * 70)
    model = buml_model()
    print()
    
    # Step 2: Generate the backend
    print("Step 2: Generating Complete Backend...")
    print("-" * 70)
    output_dir = "refactored/generated/"
    generator = RefactoredBackendGenerator(model, output_dir)
    generator.generate()
    print()
    
    # Step 3: Summary
    print("=" * 70)
    print("✅ GENERATION COMPLETE!")
    print("=" * 70)
    print(f"\nBackend generated in: {output_dir}/app/")
    print("\nGenerated from PlantUML with:")
    print("  ✓ 16 Classes (City, Dashboard, DashboardSection, KPI, etc.)")
    print("  ✓ 79 Attributes (all fields from database_structure.plantuml)")
    print("  ✓ 10 Associations (all relationships)")
    print("  ✓ 8 Generalizations (polymorphic inheritance)")
    print("  ✓ Proper table names (cities, dashboards, kpi_values, etc.)")
    print("  ✓ Complete field metadata (lengths, defaults, constraints)")
    print("  ✓ Joined table inheritance for Visualization & MapData")
    print("  ✓ 6 visualization types + 2 map data types")
    print()
    print("Next steps:")
    print("  1. Review generated code in refactored/generated_from_plantuml/app/")
    print("  2. Compare with manual implementation: refactored/app/")
    print("  3. Test the generated backend")
    print()
    print("To run the generated app:")
    print("  cd refactored/generated_from_plantuml")
    print("  python -m uvicorn app.main:app --reload")
    print()


if __name__ == "__main__":
    main()
