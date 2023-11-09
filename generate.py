from generator.clima_generator import ClimaGenerator
from BUML.metamodel.structural.structural import DomainModel
from BUML.notations.plantUML.plantuml_to_buml import plantuml_to_buml, build_buml_mm_from_grammar
from generators.sql_alchemy import SQLAlchemyGenerator
# import and build clima DSL from given plantuml model and transform it into BUML
domain: DomainModel = plantuml_to_buml('clima_model/plantuml.txt')

# generate code based on model
generator = ClimaGenerator(output_dir="generator/generated_output", model=domain)
generator.generate()
sqlalc = SQLAlchemyGenerator(output_dir="generator/generated_output", model=domain)
sqlalc.generate()
