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
domain: DomainModel = plantuml_to_buml("clima_model/metamodelvis.txt")

generator = ClimaGenerator(output_dir="generator/generated_output", model=domain)
generator.generate()
sqlalc = SQLAlchemyGenerator(output_dir="generator/generated_output", model=domain)
sqlalc.generate()
py = Python_Generator(output_dir="generator/generated_output", model=domain)
py.generate()
db = SQLGenerator(output_dir="generator/generated_output", model=domain)
db.generate()


def topological_sort(relations):
    # Creating a graph
    graph = defaultdict(list)
    in_degree = defaultdict(int)

    # Filling the graph and in-degree dictionary
    for relation in relations:
        graph[relation.target].append(relation.source)
        in_degree[relation.source] += 1
        if relation.target not in in_degree:
            in_degree[relation.target] = 0

    # Initialize the queue with nodes having in-degree 0
    queue = deque([node for node in in_degree if in_degree[node] == 0])

    sorted_order = []

    # Process until the queue is empty
    while queue:
        node = queue.popleft()
        sorted_order.append(node)

        # Decrease the in-degree of dependent nodes
        for dependent in graph[node]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    # Check for cycle in the graph
    if len(sorted_order) != len(in_degree):
        return "Cycle detected in graph, sorting not possible"

    return sorted_order[::]  # reverse to get highest hierarchy first


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


objects = plantuml_to_object("clima_model/plantumlobject.txt")

env = Environment(loader=FileSystemLoader("generator/templates"))
# generate pydantic classes for API calls
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

# generate grafana dashboard specification
""" file_name = "dashboards/"
template = env.get_template('dashboard_template.json.j2') 
os.system('del /q generator\generated_output\dashboards\*')
for object in objects:
    if object.name == "City":
        file_path = os.path.join("generator/generated_output", file_name + object.className.name + ".json")
        with open(file_path, "w") as f:
            generated_code = template.render(kpis=object.deps, city=object.className.name)
            f.write(generated_code) """


example_datetime = datetime(2023, 1, 4, 15, 30, 45)
print(example_datetime)
