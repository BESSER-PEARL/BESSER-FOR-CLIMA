from besser.BUML.metamodel.structural import NamedElement, DomainModel, Type, Class, \
        Property, PrimitiveDataType, Multiplicity, Association, BinaryAssociation, Generalization, \
        GeneralizationSet, AssociationClass 

# Primitive Data Types 
int_type = PrimitiveDataType("int")
datetime_type = PrimitiveDataType("datetime")
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

# KPICollectedWaste class definition 
KPICollectedWaste_target: Property = Property(name="target", property_type=int_type)
KPICollectedWaste: Class = Class(name="KPICollectedWaste", attributes={KPICollectedWaste_target})

# KPISecondHandCustomers class definition 
KPISecondHandCustomers_target: Property = Property(name="target", property_type=int_type)
KPISecondHandCustomers: Class = Class(name="KPISecondHandCustomers", attributes={KPISecondHandCustomers_target})

# KPIMoney class definition 
KPIMoney_target: Property = Property(name="target", property_type=int_type)
KPIMoney: Class = Class(name="KPIMoney", attributes={KPIMoney_target})

# KPITotalRenewableEnergy class definition 
KPITotalRenewableEnergy_target: Property = Property(name="target", property_type=int_type)
KPITotalRenewableEnergy: Class = Class(name="KPITotalRenewableEnergy", attributes={KPITotalRenewableEnergy_target})

# KPINumberHouseholdRenewableEnergy class definition 
KPINumberHouseholdRenewableEnergy_target: Property = Property(name="target", property_type=int_type)
KPINumberHouseholdRenewableEnergy: Class = Class(name="KPINumberHouseholdRenewableEnergy", attributes={KPINumberHouseholdRenewableEnergy_target})

# KPIPeakSolarEnergy class definition 
KPIPeakSolarEnergy_target: Property = Property(name="target", property_type=int_type)
KPIPeakSolarEnergy: Class = Class(name="KPIPeakSolarEnergy", attributes={KPIPeakSolarEnergy_target})

# Visualisation class definition 
Visualisation_xposition: Property = Property(name="xposition", property_type=int_type)
Visualisation_yposition: Property = Property(name="yposition", property_type=int_type)
Visualisation_width: Property = Property(name="width", property_type=int_type)
Visualisation_height: Property = Property(name="height", property_type=int_type)
Visualisation_chartType: Property = Property(name="chartType", property_type=str_type)
Visualisation_title: Property = Property(name="title", property_type=str_type)
Visualisation_i: Property = Property(name="i", property_type=str_type)
Visualisation_section: Property = Property(name="section", property_type=str_type)
Visualisation: Class = Class(name="Visualisation", attributes={Visualisation_xposition, Visualisation_yposition, Visualisation_width, Visualisation_height, Visualisation_chartType, Visualisation_title, Visualisation_i, Visualisation_section}, is_abstract=True)

# Table class definition 
Table: Class = Class(name="Table", attributes=set())

# PieChart class definition 
PieChart: Class = Class(name="PieChart", attributes=set())

# StatChart class definition 
StatChart_unit: Property = Property(name="unit", property_type=str_type)
StatChart_target: Property = Property(name="target", property_type=int_type)
StatChart: Class = Class(name="StatChart", attributes={StatChart_unit, StatChart_target})

# LineChart class definition 
LineChart_xtitle: Property = Property(name="xtitle", property_type=str_type)
LineChart_ytitle: Property = Property(name="ytitle", property_type=str_type)
LineChart_color: Property = Property(name="color", property_type=str_type)
LineChart_target: Property = Property(name="target", property_type=int_type)
LineChart: Class = Class(name="LineChart", attributes={LineChart_xtitle, LineChart_ytitle, LineChart_color, LineChart_target})

# TableColumn class definition 
TableColumn_name: Property = Property(name="name", property_type=str_type)
TableColumn: Class = Class(name="TableColumn", attributes={TableColumn_name})

# Map class definition 
Map: Class = Class(name="Map", attributes=set())

# User class definition 
User_password: Property = Property(name="password", property_type=str_type)
User_email: Property = Property(name="email", property_type=str_type)
User_firstName: Property = Property(name="firstName", property_type=str_type)
User_lastName: Property = Property(name="lastName", property_type=str_type)
User: Class = Class(name="User", attributes={User_password, User_email, User_firstName, User_lastName}, is_abstract=True)

# Admin class definition 
Admin: Class = Class(name="Admin", attributes=set())

# CityUser class definition 
CityUser: Class = Class(name="CityUser", attributes=set())

# CityAngel class definition 
CityAngel: Class = Class(name="CityAngel", attributes=set())

# SolutionProvider class definition 
SolutionProvider: Class = Class(name="SolutionProvider", attributes=set())

# Citizen class definition 
Citizen: Class = Class(name="Citizen", attributes=set())

# Dashboard class definition 
Dashboard_code: Property = Property(name="code", property_type=str_type)
Dashboard: Class = Class(name="Dashboard", attributes={Dashboard_code})

# MapData class definition 
MapData_title: Property = Property(name="title", property_type=str_type)
MapData: Class = Class(name="MapData", attributes={MapData_title}, is_abstract=True)

# GeoJson class definition 
GeoJson_data: Property = Property(name="data", property_type=str_type)
GeoJson: Class = Class(name="GeoJson", attributes={GeoJson_data})

# WMS class definition 
WMS_url: Property = Property(name="url", property_type=str_type)
WMS_name: Property = Property(name="name", property_type=str_type)
WMS: Class = Class(name="WMS", attributes={WMS_url, WMS_name})

# KPIParticipants class definition 
KPIParticipants_target: Property = Property(name="target", property_type=int_type)
KPIParticipants: Class = Class(name="KPIParticipants", attributes={KPIParticipants_target})

# KPIWasteAvoided class definition 
KPIWasteAvoided_target: Property = Property(name="target", property_type=int_type)
KPIWasteAvoided: Class = Class(name="KPIWasteAvoided", attributes={KPIWasteAvoided_target})

# KPICo2Avoided class definition 
KPICo2Avoided_target: Property = Property(name="target", property_type=int_type)
KPICo2Avoided: Class = Class(name="KPICo2Avoided", attributes={KPICo2Avoided_target})

# KPIWasteSorted class definition 
KPIWasteSorted_target: Property = Property(name="target", property_type=int_type)
KPIWasteSorted: Class = Class(name="KPIWasteSorted", attributes={KPIWasteSorted_target})

# KPITextileWastePerPerson class definition 
KPITextileWastePerPerson: Class = Class(name="KPITextileWastePerPerson", attributes=set())

# Relationships
values: BinaryAssociation = BinaryAssociation(name="values", ends={
        Property(name="values", property_type=KPI, multiplicity=Multiplicity(1, 1), is_navigable=False),
        Property(name="values", property_type=KPIValue, multiplicity=Multiplicity(0, "*"), is_navigable=True)})
kpis: BinaryAssociation = BinaryAssociation(name="kpis", ends={
        Property(name="kpis", property_type=City, multiplicity=Multiplicity(1, 1), is_navigable=False),
        Property(name="kpis", property_type=KPI, multiplicity=Multiplicity(0, "*"), is_navigable=True)})
visualizedBy: BinaryAssociation = BinaryAssociation(name="visualizedBy", ends={
        Property(name="visualizedBy", property_type=Visualisation, multiplicity=Multiplicity(0, "*"), is_navigable=True),
        Property(name="visualizedBy", property_type=KPI, multiplicity=Multiplicity(1, 1), is_navigable=False)})
has: BinaryAssociation = BinaryAssociation(name="has", ends={
        Property(name="has", property_type=City, multiplicity=Multiplicity(1, 1), is_navigable=False),
        Property(name="has", property_type=Dashboard, multiplicity=Multiplicity(0, "*"), is_navigable=True)})
consistsOf: BinaryAssociation = BinaryAssociation(name="consistsOf", ends={
        Property(name="consistsOf", property_type=Dashboard, multiplicity=Multiplicity(1, 1), is_navigable=False),
        Property(name="consistsOf", property_type=Visualisation, multiplicity=Multiplicity(0, "*"), is_navigable=True)})
shows: BinaryAssociation = BinaryAssociation(name="shows", ends={
        Property(name="shows", property_type=Table, multiplicity=Multiplicity(1, 1), is_navigable=False),
        Property(name="shows", property_type=TableColumn, multiplicity=Multiplicity(0, "*"), is_navigable=True)})
operatedBy: BinaryAssociation = BinaryAssociation(name="operatedBy", ends={
        Property(name="operatedBy", property_type=City, multiplicity=Multiplicity(1, 1), is_navigable=False),
        Property(name="operatedBy", property_type=User, multiplicity=Multiplicity(0, "*"), is_navigable=True)})
hasMapData: BinaryAssociation = BinaryAssociation(name="hasMapData", ends={
        Property(name="hasMapData", property_type=City, multiplicity=Multiplicity(1, 1), is_navigable=False),
        Property(name="hasMapData", property_type=MapData, multiplicity=Multiplicity(0, "*"), is_navigable=True)})
isDisplayedOnMap: BinaryAssociation = BinaryAssociation(name="isDisplayedOnMap", ends={
        Property(name="isDisplayedOnMap", property_type=Map, multiplicity=Multiplicity(0, "*"), is_navigable=True),
        Property(name="isDisplayedOnMap", property_type=MapData, multiplicity=Multiplicity(1, 1), is_navigable=False)})

# Generalizations
gen_KPI_KPICollectedWaste: Generalization = Generalization(general=KPI, specific=KPICollectedWaste)
gen_KPI_KPISecondHandCustomers: Generalization = Generalization(general=KPI, specific=KPISecondHandCustomers)
gen_KPI_KPITotalRenewableEnergy: Generalization = Generalization(general=KPI, specific=KPITotalRenewableEnergy)
gen_KPI_KPINumberHouseholdRenewableEnergy: Generalization = Generalization(general=KPI, specific=KPINumberHouseholdRenewableEnergy)
gen_KPI_KPIPeakSolarEnergy: Generalization = Generalization(general=KPI, specific=KPIPeakSolarEnergy)
gen_KPI_KPITemp: Generalization = Generalization(general=KPI, specific=KPITemp)
gen_KPI_KPITraffic: Generalization = Generalization(general=KPI, specific=KPITraffic)
gen_KPI_KPIMoney: Generalization = Generalization(general=KPI, specific=KPIMoney)
gen_Visualisation_Table: Generalization = Generalization(general=Visualisation, specific=Table)
gen_Visualisation_PieChart: Generalization = Generalization(general=Visualisation, specific=PieChart)
gen_Visualisation_StatChart: Generalization = Generalization(general=Visualisation, specific=StatChart)
gen_Visualisation_LineChart: Generalization = Generalization(general=Visualisation, specific=LineChart)
gen_Visualisation_Map: Generalization = Generalization(general=Visualisation, specific=Map)
gen_User_Admin: Generalization = Generalization(general=User, specific=Admin)
gen_User_CityUser: Generalization = Generalization(general=User, specific=CityUser)
gen_User_CityAngel: Generalization = Generalization(general=User, specific=CityAngel)
gen_User_SolutionProvider: Generalization = Generalization(general=User, specific=SolutionProvider)
gen_User_Citizen: Generalization = Generalization(general=User, specific=Citizen)
gen_MapData_GeoJson: Generalization = Generalization(general=MapData, specific=GeoJson)
gen_MapData_WMS: Generalization = Generalization(general=MapData, specific=WMS)
gen_KPI_KPIParticipants: Generalization = Generalization(general=KPI, specific=KPIParticipants)
gen_KPI_KPIWasteAvoided: Generalization = Generalization(general=KPI, specific=KPIWasteAvoided)
gen_KPI_KPICo2Avoided: Generalization = Generalization(general=KPI, specific=KPICo2Avoided)
gen_KPI_KPIWasteSorted: Generalization = Generalization(general=KPI, specific=KPIWasteSorted)
gen_KPI_KPITextileWastePerPerson: Generalization = Generalization(general=KPI, specific=KPITextileWastePerPerson)


# Domain Model
domain: DomainModel = DomainModel(name="Domain Model", types={City, KPI, KPIValue, KPITemp, KPITraffic, KPICollectedWaste, KPISecondHandCustomers, KPIMoney, KPITotalRenewableEnergy, KPINumberHouseholdRenewableEnergy, KPIPeakSolarEnergy, Visualisation, Table, PieChart, StatChart, LineChart, TableColumn, Map, User, Admin, CityUser, CityAngel, SolutionProvider, Citizen, Dashboard, MapData, GeoJson, WMS, KPIParticipants, KPIWasteAvoided, KPICo2Avoided, KPIWasteSorted, KPITextileWastePerPerson}, associations={values, kpis, visualizedBy, has, consistsOf, shows, operatedBy, hasMapData, isDisplayedOnMap}, generalizations={gen_KPI_KPICollectedWaste, gen_KPI_KPISecondHandCustomers, gen_KPI_KPITotalRenewableEnergy, gen_KPI_KPINumberHouseholdRenewableEnergy, gen_KPI_KPIPeakSolarEnergy, gen_KPI_KPITemp, gen_KPI_KPITraffic, gen_KPI_KPIMoney, gen_Visualisation_Table, gen_Visualisation_PieChart, gen_Visualisation_StatChart, gen_Visualisation_LineChart, gen_Visualisation_Map, gen_User_Admin, gen_User_CityUser, gen_User_CityAngel, gen_User_SolutionProvider, gen_User_Citizen, gen_MapData_GeoJson, gen_MapData_WMS, gen_KPI_KPIParticipants, gen_KPI_KPIWasteAvoided, gen_KPI_KPICo2Avoided, gen_KPI_KPIWasteSorted, gen_KPI_KPITextileWastePerPerson})