import sys
from datetime import datetime
from generator.clima_generator import ClimaGenerator
from besser.BUML.metamodel.structural.structural import DomainModel
from besser.BUML.notations.structuralPlantUML import plantuml_to_buml
from besser.generators.sql_alchemy import SQLAlchemyGenerator
from besser.generators.sql import SQLGenerator

from textx import metamodel_from_file
import os
from jinja2 import Environment, FileSystemLoader

import json

from utils.utils import topological_sort




def plantuml_to_object(model_path: str):
    """
    Converts a PlantUML model to a model conforms to B-UML.

    Args:
        model_path (str): The path to the PlantUML model file.

    Returns:
        DomainModel: The resulting model conforms to B-UML.
    """

    grammar_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "plantumlobject.tx"
    )
    plantUML_mm = metamodel_from_file(grammar_path)
    textx_model = plantUML_mm.model_from_file(model_path)

    res = topological_sort(textx_model.relationships)
    objects = []
    dependencies = {}
    dependency_of = {}
    zwischenspeicher = {}
    for o in textx_model.objects:
        zwischenspeicher[o.alias] = o
        dependency_of[o.alias] = []
    for object in res:
        for element in textx_model.objects:
            if object == element.alias:
                deps = []
                for rel in textx_model.relationships:
                    if rel.source == element.alias:
                        deps.append(dependencies[rel.target])
                        dependency_of[rel.target].append(zwischenspeicher[rel.source])
                dependencies[element.alias] = element
                element.deps = deps
                objects.append(element)
                textx_model.objects.remove(element)
    objects += textx_model.objects
    for object in objects:
        object.dep_from = dependency_of[object.alias]
        attribute_dict = {}
        for attribute in object.attributes:
            attribute_dict[attribute.name] = attribute.value
        object.attribute_dict = attribute_dict
    return objects

# start creation of metamodel and generate classes

domain: DomainModel = plantuml_to_buml("clima_model/metamodel.plantuml")

generator = ClimaGenerator(output_dir="generator/generated_output", model=domain)
generator.generate()
sqlalc = SQLAlchemyGenerator(output_dir="generator/generated_output", model=domain)
sqlalc.generate()

# instantiate objects given classes and object model

objects = plantuml_to_object("clima_model/plantumlobject.plantuml")
jsonObjects = dict()
for obj in objects:
    if (obj.name == "City"):
        city = dict()
        if hasattr(obj, 'deps') and obj.deps:
            for kpi in obj.deps:
                kpi_json = dict()
                print(kpi)
                for attribute in kpi.attribute_dict:
                    print(attribute)
                    kpi_json[attribute] = kpi.attribute_dict[attribute]
                city[kpi.name] = kpi_json
        jsonObjects[obj.className.name] = city
        
# Specify the file name
file_name = "data.json"

# Open the file in write mode and use json.dump to write the object
with open(file_name, 'w') as json_file:
    json.dump(jsonObjects, json_file, indent=4)

env = Environment(loader=FileSystemLoader("generator/templates"))
file_name = "objects.py"
template = env.get_template("objects.py.j2")
file_path = os.path.join("generator/generated_output", file_name)
with open(file_path, "w") as f:
    generated_code = template.render(objects=objects)
    f.write(generated_code)


# generate api interfaces for API calls
file_name = "api_interface_objects.py"
template = env.get_template("fastapiinterface_template_objects.py")
file_path = os.path.join("generator/generated_output", file_name)
with open(file_path, "w") as f:
    generated_code = template.render(
        objects=objects[::-1], classes=domain.classes_sorted_by_inheritance()
    )
    f.write(generated_code)
