import os
from besser.BUML.metamodel.structural import DomainModel, Class, Property
from jinja2 import Environment, FileSystemLoader
from besser.generators.generator_interface import GeneratorInterface

class ClimaGenerator(GeneratorInterface):
    def __init__(self, model: DomainModel, output_dir: str = None):
        super().__init__(model, output_dir)

    def generate(self):
        env = Environment(loader=FileSystemLoader('generator/templates'))
        # generate pydantic classes for API calls
        file_name = "pydantic_classes.py"
        template = env.get_template('pydantic_classes_template.py.j2')
        file_path = os.path.join(self.output_dir, file_name)
        with open(file_path, "w") as f:
            generated_code = template.render(classes=self.model.classes_sorted_by_inheritance())
            f.write(generated_code)
        

