from textx import metamodel_from_file
import os
from jinja2 import Environment, FileSystemLoader
from collections import deque, defaultdict


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

def plantuml_to_object(model_path:str):
    """
    Converts a PlantUML model to a model conforms to B-UML.

    Args:
        model_path (str): The path to the PlantUML model file.

    Returns:
        DomainModel: The resulting model conforms to B-UML.
    """
    
    grammar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plantumlobject.tx')
    plantUML_mm = metamodel_from_file(grammar_path)
    textx_model = plantUML_mm.model_from_file(model_path)
    
    for rel in textx_model.relationships:
        print("rel")
        print(rel.source)
        print(rel.target)
    res = topological_sort(textx_model.relationships)
    objects = []
    dependencies = {}
    for object in res:
        for element in textx_model.objects:
            if object == element.alias:
                deps = []
                for rel in textx_model.relationships:
                    if rel.source == element.alias:
                        deps.append(dependencies[rel.target])
                dependencies[element.alias] = element
                element.deps = deps
                objects.append(element)
                textx_model.objects.remove(element)
    objects += textx_model.objects
    print(res)
    print(objects)
    return objects


objects = plantuml_to_object("clima_model/differdangeobject.txt")
env = Environment(loader=FileSystemLoader('generator/templates'))
# generate pydantic classes for API calls
file_name = "objects.py"
template = env.get_template('objects.py.j2')
file_path = os.path.join("generator/generated_output", file_name)
with open(file_path, "w") as f:
    generated_code = template.render(objects=objects)
    f.write(generated_code)


# generate api interfaces for API calls
file_name = "api_interface_objects.py"
template = env.get_template('fastapiinterface_template_objects.py.j2')
file_path = os.path.join("generator/generated_output", file_name)
with open(file_path, "w") as f:
    generated_code = template.render(objects=objects, classes=domain.)
    f.write(generated_code)
