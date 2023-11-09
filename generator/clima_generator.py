import os
from metamodel.structural import DomainModel, Class
from jinja2 import Environment, FileSystemLoader
from generators.generator_interface import GeneratorInterface

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
        
        # generate api interface
        file_name = "api_interface.py"
        file_path = os.path.join(self.output_dir, file_name)     
        template = env.get_template('fastapiinterface_template.py')   
        with open(file_path, "w") as f:
            generated_code = template.render(classes=self.model.get_classes())
            f.write(generated_code)
        
        # generate grafana dashboard specification
        file_name = "dashboards/"
        template = env.get_template('dashboard_template.json.j2')   
        for c in self.model.classes_sorted_by_inheritance():
            for parent in c.all_parents():
                if parent.name == "City":
                    print("city" + c.name)
                    file_path = os.path.join(self.output_dir, file_name + c.name + ".json")
                    with open(file_path, "w") as f:
                        generated_code = template.render(classes=self.model.get_classes())
                        f.write(generated_code)  
