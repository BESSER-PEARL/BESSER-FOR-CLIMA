from generator.clima_generator import ClimaGenerator
from metamodel.structural.structural import DomainModel
from notations.textx.textx_to_buml import textx_to_buml, build_buml_mm_from_grammar


# import and build clima DSL from given plantuml model and transform it into BUML
climaborough_model = build_buml_mm_from_grammar().model_from_file('clima_model/plantuml.txt')
domain: DomainModel = textx_to_buml(climaborough_model)

# generate code based on model
generator = ClimaGenerator(output_dir="generator/generated_output", model=domain)
generator.generate()





