from flask import Flask, render_template_string, url_for, request, redirect
import json
# Assuming model is already defined with classes and a get_classes() method
# Example structure of your model and KPI class:

# Example KPI class

import sys
from datetime import datetime
from besser.BUML.metamodel.structural.structural import DomainModel
from besser.BUML.notations.plantUML.plantuml_to_buml import plantuml_to_buml

from generate import plantuml_to_object

model: DomainModel = plantuml_to_buml("clima_model/metamodel.txt")
objects = plantuml_to_object("clima_model/plantumlobject.txt")
jsonObjects = dict()
for obj in objects:
    if (obj.name == "City"):
        city = dict()
        for kpi in obj.deps:
            kpi_json = dict()
            for attribute in kpi.attribute_dict:
                kpi_json[attribute] = kpi.attribute_dict[attribute]
            city[kpi.name] =  kpi_json
        jsonObjects[obj.className.name] = city
# Create the Flask application
app = Flask(__name__)

# Extract all classes that inherit from KPI and put them in a list

kpi_classes = []

for cls in model.get_classes():
    for parent in cls.parents():
        if parent.name == "KPI":
            kpi_classes.append(cls)


@app.route('/')
def index():
    # Create a list of class names and their corresponding URLs
    city_links = [(city, url_for('city_detail', city_name=city)) for city in jsonObjects.keys()]
    # Render an HTML template with clickable links
    return render_template_string("""
        <h1>Cities</h1>
        <ul>
        {% for name, link in city_links %}
            <li><a href="{{ link }}">{{ name }}</a></li>
        {% endfor %}
        </ul>
    """, city_links=city_links)

# Flask route to display the attributes of the selected KPI class
@app.route('/<city_name>/kpis/')
def city_detail(city_name):
    # Find the class corresponding to the given kpi_name
    kpis = [(kpi, url_for('kpi_detail', kpi_name= kpi, city_name=city_name)) for kpi in jsonObjects[city_name].keys()]
    
    if kpis:
        # Retrieve the attributes using the class's all_attributes() method
        attributes = kpis
    else:
        attributes = {"error": "KPI class not found."}
    
    # Render an HTML template to display the attributes
    return render_template_string("""
        <h1>{{ city_name }} KPIs</h1>
        <ul>
        {% for kpi, link in kpis %}
            <li><strong><a href="{{ link }}">{{ kpi }}</a></strong></li>
        {% endfor %}
        </ul>
        <a href="{{ url_for('index') }}">Back to City list</a>
    """, city_name=city_name, kpis=kpis)

# Flask route to display the attributes of the selected KPI class
@app.route('/<city_name>/kpi/<kpi_name>', methods=['GET', 'POST'])
def kpi_detail(city_name, kpi_name):
    # Find the class corresponding to the given kpi_name
    kpis = jsonObjects[city_name]
    attributes =  kpis[kpi_name]
    
    if request.method == 'POST':
        # Update the jsonObjects with the new values from the form
        for key in attributes.keys():
            if key in request.form:
                attributes[key] = request.form[key]
        kpis[kpi_name] = attributes
        jsonObjects[city_name] = kpis
        file_name = "data.json"
        with open(file_name, 'w') as json_file:
            json.dump(jsonObjects, json_file, indent=4)
        # Redirect back to the same page after saving
        return redirect(url_for('kpi_detail', city_name=city_name, kpi_name=kpi_name))
    
    if attributes:
        # Retrieve the attributes using the class's all_attributes() method
        print("good")
    else:
        attributes = {"error": "KPI class not found."}
    
    # Render an HTML template to display the attributes
    return render_template_string("""
        <h1>{{ kpi_name }} KPIs</h1>
        <form method="POST">
            <ul>
            {% for name, value in attributes.items() %}
                <li><strong>{{ name }}:</strong></li>
                <input type="text" name="{{ name }}" value="{{ value }}"></input>
            {% endfor %}
            </ul>
            <button type="submit">Save</button>
        </form>
        <a href="{{ url_for('index') }}">Back to City list</a>
    """, kpi_name=kpi_name, attributes=attributes)


if __name__ == '__main__':
    app.run(debug=True)
