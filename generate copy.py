import sys
from datetime import datetime
from generator.clima_generator import ClimaGenerator
from besser.BUML.metamodel.structural.structural import DomainModel
from besser.BUML.notations.plantUML.plantuml_to_buml import plantuml_to_buml
from besser.generators.sql_alchemy import SQLAlchemyGenerator
from besser.generators.python_classes import Python_Generator
from besser.generators.sql import SQLGenerator

from textx import metamodel_from_file
import os
from jinja2 import Environment, FileSystemLoader
from collections import deque, defaultdict


# import and build clima DSL from given plantuml model and transform it into BUML
domain: DomainModel = plantuml_to_buml('clima_model/metamodel.txt')

generator = ClimaGenerator(output_dir="generator/generated_output", model=domain)
generator.generate()
sqlalc = SQLAlchemyGenerator(output_dir="generator/generated_output", model=domain)
sqlalc.generate()
py = Python_Generator(output_dir="generator/generated_output", model=domain)
py.generate()
db = SQLGenerator(output_dir="generator/generated_output", model=domain)
db.generate()




