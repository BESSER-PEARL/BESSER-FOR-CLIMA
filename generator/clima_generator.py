import os

from metamodel.structural.structural import DomainModel
from generators.django.auxiliary import get_constraints_for_class
from jinja2 import Environment, FileSystemLoader

class ClimaGenerator:
    def __init__(self, model: DomainModel, output_dir: str):
        self.model = model
        self.output_dir = output_dir

    def generate(self):
        # Start generation of basic python classes
        file_name = "classes.py"
        file_path = os.path.join(self.output_dir, file_name)
        env = Environment(loader=FileSystemLoader('generator/templates'))
        template = env.get_template('classes_template.py')
        with open(file_path, "w") as f:
            generated_code = template.render(classes=self.model.get_classes())
            f.write(generated_code)
        
        # generate pydantic classes for API calls
        file_name = "pydantic_classes.py"
        template = env.get_template('pydantic_classes_template.py')
        file_path = os.path.join(self.output_dir, file_name)        
        with open(file_path, "w") as f:
            generated_code = template.render(classes=self.model.get_classes())
            f.write(generated_code)
        
        # generate api interface
        file_name = "api_interface.py"
        file_path = os.path.join(self.output_dir, file_name)     
        template = env.get_template('fastapiinterface_template.py')   
        with open(file_path, "w") as f:
            generated_code = template.render(classes=self.model.get_classes())
            f.write(generated_code)
        
        # generate grafana dashboard specification
        file_name = "dashboard.json"
        file_path = os.path.join(self.output_dir, file_name)     
        template = env.get_template('dashboard_template.json')   
        with open(file_path, "w") as f:
            generated_code = template.render(classes=self.model.get_classes())
            f.write(generated_code)
            

