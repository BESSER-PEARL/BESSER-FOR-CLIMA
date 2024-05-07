from besser.BUML.metamodel.structural import NamedElement, DomainModel, Type, Class, \
        Property, PrimitiveDataType, Multiplicity, Association, BinaryAssociation, Generalization, \
        GeneralizationSet, AssociationClass 

# Primitive Data Types 
datetime_type = PrimitiveDataType("datetime")
int_type = PrimitiveDataType("int")
str_type = PrimitiveDataType("str")

# City class definition 
City_name: Property = Property(name="name", property_type=str_type)
City: Class = Class(name="City", attributes={City_name})

# KPI class definition 
KPI_id_kpi: Property = Property(name="id_kpi", property_type=str_type)
KPI_name: Property = Property(name="name", property_type=str_type)
KPI_category: Property = Property(name="category", property_type=str_type)
KPI_description: Property = Property(name="description", property_type=str_type)
KPI_provider: Property = Property(name="provider", property_type=str_type)
KPI_calculationFrequency: Property = Property(name="calculationFrequency", property_type=str_type)
KPI_unitText: Property = Property(name="unitText", property_type=str_type)
KPI: Class = Class(name="KPI", attributes={KPI_id_kpi, KPI_name, KPI_category, KPI_description, KPI_provider, KPI_calculationFrequency, KPI_unitText}, is_abstract=True)

# KPIValue class definition 
KPIValue_kpiValue: Property = Property(name="kpiValue", property_type=int_type)
KPIValue_timestamp: Property = Property(name="timestamp", property_type=datetime_type)
KPIValue_currentStanding: Property = Property(name="currentStanding", property_type=str_type)
KPIValue: Class = Class(name="KPIValue", attributes={KPIValue_kpiValue, KPIValue_timestamp, KPIValue_currentStanding})

# KPITemp class definition 
KPITemp_threshold: Property = Property(name="threshold", property_type=int_type)
KPITemp: Class = Class(name="KPITemp", attributes={KPITemp_threshold})

# KPITraffic class definition 
KPITraffic_target: Property = Property(name="target", property_type=int_type)
KPITraffic: Class = Class(name="KPITraffic", attributes={KPITraffic_target})

# KPIMoney class definition 
KPIMoney_target: Property = Property(name="target", property_type=int_type)
KPIMoney: Class = Class(name="KPIMoney", attributes={KPIMoney_target})

# Visualization class definition 
Visualization_xposition: Property = Property(name="xposition", property_type=int_type)
Visualization_yposition: Property = Property(name="yposition", property_type=int_type)
Visualization_width: Property = Property(name="width", property_type=int_type)
Visualization_height: Property = Property(name="height", property_type=int_type)
Visualization_chartType: Property = Property(name="chartType", property_type=str_type)
Visualization_title: Property = Property(name="title", property_type=str_type)
Visualization_i: Property = Property(name="i", property_type=str_type)
Visualization: Class = Class(name="Visualization", attributes={Visualization_xposition, Visualization_yposition, Visualization_width, Visualization_height, Visualization_chartType, Visualization_title, Visualization_i}, is_abstract=True)

# Table class definition 
Table: Class = Class(name="Table", attributes=set())

# PieChart class definition 
PieChart: Class = Class(name="PieChart", attributes=set())

# StatChart class definition 
StatChart_unit: Property = Property(name="unit", property_type=str_type)
StatChart: Class = Class(name="StatChart", attributes={StatChart_unit})

# LineChart class definition 
LineChart_xtitle: Property = Property(name="xtitle", property_type=str_type)
LineChart_ytitle: Property = Property(name="ytitle", property_type=str_type)
LineChart_color: Property = Property(name="color", property_type=str_type)
LineChart: Class = Class(name="LineChart", attributes={LineChart_xtitle, LineChart_ytitle, LineChart_color})

# TableColumn class definition 
TableColumn_name: Property = Property(name="name", property_type=str_type)
TableColumn: Class = Class(name="TableColumn", attributes={TableColumn_name})

# Map class definition 
Map: Class = Class(name="Map", attributes=set())

# Dashboard class definition 
Dashboard_code: Property = Property(name="code", property_type=str_type)
Dashboard: Class = Class(name="Dashboard", attributes={Dashboard_code})

# Relationships
values: BinaryAssociation = BinaryAssociation(name="values", ends={
        Property(name="values", property_type=KPI, multiplicity=Multiplicity(1, 1), is_navigable=False),
        Property(name="values", property_type=KPIValue, multiplicity=Multiplicity(0, "*"), is_navigable=True)})
kpis: BinaryAssociation = BinaryAssociation(name="kpis", ends={
        Property(name="kpis", property_type=City, multiplicity=Multiplicity(1, 1), is_navigable=False),
        Property(name="kpis", property_type=KPI, multiplicity=Multiplicity(0, "*"), is_navigable=True)})
visualizedBy: BinaryAssociation = BinaryAssociation(name="visualizedBy", ends={
        Property(name="visualizedBy", property_type=Visualization, multiplicity=Multiplicity(0, "*"), is_navigable=True),
        Property(name="visualizedBy", property_type=KPI, multiplicity=Multiplicity(1, 1), is_navigable=False)})
has: BinaryAssociation = BinaryAssociation(name="has", ends={
        Property(name="has", property_type=City, multiplicity=Multiplicity(1, 1), is_navigable=False),
        Property(name="has", property_type=Dashboard, multiplicity=Multiplicity(0, "*"), is_navigable=True)})
consistsOf: BinaryAssociation = BinaryAssociation(name="consistsOf", ends={
        Property(name="consistsOf", property_type=Dashboard, multiplicity=Multiplicity(1, 1), is_navigable=False),
        Property(name="consistsOf", property_type=Visualization, multiplicity=Multiplicity(0, "*"), is_navigable=True)})
shows: BinaryAssociation = BinaryAssociation(name="shows", ends={
        Property(name="shows", property_type=Table, multiplicity=Multiplicity(1, 1), is_navigable=False),
        Property(name="shows", property_type=TableColumn, multiplicity=Multiplicity(0, "*"), is_navigable=True)})

# Generalizations
gen_KPI_KPITemp: Generalization = Generalization(general=KPI, specific=KPITemp)
gen_KPI_KPITraffic: Generalization = Generalization(general=KPI, specific=KPITraffic)
gen_KPI_KPIMoney: Generalization = Generalization(general=KPI, specific=KPIMoney)
gen_Visualization_Table: Generalization = Generalization(general=Visualization, specific=Table)
gen_Visualization_PieChart: Generalization = Generalization(general=Visualization, specific=PieChart)
gen_Visualization_StatChart: Generalization = Generalization(general=Visualization, specific=StatChart)
gen_Visualization_LineChart: Generalization = Generalization(general=Visualization, specific=LineChart)
gen_Visualization_Map: Generalization = Generalization(general=Visualization, specific=Map)


# Domain Model
domain: DomainModel = DomainModel(name="Domain Model", types={City, KPI, KPIValue, KPITemp, KPITraffic, KPIMoney, Visualization, Table, PieChart, StatChart, LineChart, TableColumn, Map, Dashboard}, associations={values, kpis, visualizedBy, has, consistsOf, shows}, generalizations={gen_KPI_KPITemp, gen_KPI_KPITraffic, gen_KPI_KPIMoney, gen_Visualization_Table, gen_Visualization_PieChart, gen_Visualization_StatChart, gen_Visualization_LineChart, gen_Visualization_Map})