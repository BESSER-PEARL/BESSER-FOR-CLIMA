from besser.BUML.metamodel.structural import *  

# Primitive Data Types
int_type = PrimitiveDataType("int")
str_type = PrimitiveDataType("str")
datetime_type = PrimitiveDataType("datetime")

# Classes
City: Class = Class(name="City")
KPI: Class = Class(name="KPI", is_abstract=True)
KPIValue: Class = Class(name="KPIValue")
KPITemp: Class = Class(name="KPITemp")
KPITraffic: Class = Class(name="KPITraffic")
KPICollectedWaste: Class = Class(name="KPICollectedWaste")
KPISecondHandCustomers: Class = Class(name="KPISecondHandCustomers")
KPIMoney: Class = Class(name="KPIMoney")
KPITotalRenewableEnergy: Class = Class(name="KPITotalRenewableEnergy")
KPINumberHouseholdRenewableEnergy: Class = Class(name="KPINumberHouseholdRenewableEnergy")
KPIPeakSolarEnergy: Class = Class(name="KPIPeakSolarEnergy")
Visualisation: Class = Class(name="Visualisation", is_abstract=True)
Table: Class = Class(name="Table")
PieChart: Class = Class(name="PieChart")
StatChart: Class = Class(name="StatChart")
LineChart: Class = Class(name="LineChart")
TableColumn: Class = Class(name="TableColumn")
Map: Class = Class(name="Map")
User: Class = Class(name="User", is_abstract=True)
Admin: Class = Class(name="Admin")
CityUser: Class = Class(name="CityUser")
CityAngel: Class = Class(name="CityAngel")
SolutionProvider: Class = Class(name="SolutionProvider")
Citizen: Class = Class(name="Citizen")
Dashboard: Class = Class(name="Dashboard")
MapData: Class = Class(name="MapData", is_abstract=True)
GeoJson: Class = Class(name="GeoJson")
WMS: Class = Class(name="WMS")
KPIParticipants: Class = Class(name="KPIParticipants")
KPIWasteAvoided: Class = Class(name="KPIWasteAvoided")
KPICo2Avoided: Class = Class(name="KPICo2Avoided")
KPIWasteSorted: Class = Class(name="KPIWasteSorted")
KPITextileWastePerPerson: Class = Class(name="KPITextileWastePerPerson")

# City class attributes and methods
City_name: Property = Property(name="name", type=str_type)
City.attributes={City_name}

# KPI class attributes and methods
KPI_id_kpi: Property = Property(name="id_kpi", type=str_type)
KPI_name: Property = Property(name="name", type=str_type)
KPI_category: Property = Property(name="category", type=str_type)
KPI_description: Property = Property(name="description", type=str_type)
KPI_provider: Property = Property(name="provider", type=str_type)
KPI_calculationFrequency: Property = Property(name="calculationFrequency", type=str_type)
KPI_unitText: Property = Property(name="unitText", type=str_type)
KPI.attributes={KPI_id_kpi, KPI_name, KPI_category, KPI_description, KPI_provider, KPI_calculationFrequency, KPI_unitText}

# KPIValue class attributes and methods
KPIValue_kpiValue: Property = Property(name="kpiValue", type=int_type)
KPIValue_timestamp: Property = Property(name="timestamp", type=datetime_type)
KPIValue_currentStanding: Property = Property(name="currentStanding", type=str_type)
KPIValue.attributes={KPIValue_kpiValue, KPIValue_timestamp, KPIValue_currentStanding}

# KPITemp class attributes and methods
KPITemp_threshold: Property = Property(name="threshold", type=int_type)
KPITemp.attributes={KPITemp_threshold}

# KPITraffic class attributes and methods
KPITraffic_target: Property = Property(name="target", type=int_type)
KPITraffic.attributes={KPITraffic_target}

# KPICollectedWaste class attributes and methods
KPICollectedWaste_target: Property = Property(name="target", type=int_type)
KPICollectedWaste.attributes={KPICollectedWaste_target}

# KPISecondHandCustomers class attributes and methods
KPISecondHandCustomers_target: Property = Property(name="target", type=int_type)
KPISecondHandCustomers.attributes={KPISecondHandCustomers_target}

# KPIMoney class attributes and methods
KPIMoney_target: Property = Property(name="target", type=int_type)
KPIMoney.attributes={KPIMoney_target}

# KPITotalRenewableEnergy class attributes and methods
KPITotalRenewableEnergy_target: Property = Property(name="target", type=int_type)
KPITotalRenewableEnergy.attributes={KPITotalRenewableEnergy_target}

# KPINumberHouseholdRenewableEnergy class attributes and methods
KPINumberHouseholdRenewableEnergy_target: Property = Property(name="target", type=int_type)
KPINumberHouseholdRenewableEnergy.attributes={KPINumberHouseholdRenewableEnergy_target}

# KPIPeakSolarEnergy class attributes and methods
KPIPeakSolarEnergy_target: Property = Property(name="target", type=int_type)
KPIPeakSolarEnergy.attributes={KPIPeakSolarEnergy_target}

# Visualisation class attributes and methods
Visualisation_xposition: Property = Property(name="xposition", type=int_type)
Visualisation_yposition: Property = Property(name="yposition", type=int_type)
Visualisation_width: Property = Property(name="width", type=int_type)
Visualisation_height: Property = Property(name="height", type=int_type)
Visualisation_chartType: Property = Property(name="chartType", type=str_type)
Visualisation_title: Property = Property(name="title", type=str_type)
Visualisation_i: Property = Property(name="i", type=str_type)
Visualisation_section: Property = Property(name="section", type=str_type)
Visualisation.attributes={Visualisation_xposition, Visualisation_yposition, Visualisation_width, Visualisation_height, Visualisation_chartType, Visualisation_title, Visualisation_i, Visualisation_section}

# Table class attributes and methods

# PieChart class attributes and methods

# StatChart class attributes and methods
StatChart_unit: Property = Property(name="unit", type=str_type)
StatChart_target: Property = Property(name="target", type=int_type)
StatChart.attributes={StatChart_unit, StatChart_target}

# LineChart class attributes and methods
LineChart_xtitle: Property = Property(name="xtitle", type=str_type)
LineChart_ytitle: Property = Property(name="ytitle", type=str_type)
LineChart_color: Property = Property(name="color", type=str_type)
LineChart_target: Property = Property(name="target", type=int_type)
LineChart.attributes={LineChart_xtitle, LineChart_ytitle, LineChart_color, LineChart_target}

# TableColumn class attributes and methods
TableColumn_name: Property = Property(name="name", type=str_type)
TableColumn.attributes={TableColumn_name}

# Map class attributes and methods

# User class attributes and methods
User_password: Property = Property(name="password", type=str_type)
User_email: Property = Property(name="email", type=str_type)
User_firstName: Property = Property(name="firstName", type=str_type)
User_lastName: Property = Property(name="lastName", type=str_type)
User.attributes={User_password, User_email, User_firstName, User_lastName}

# Admin class attributes and methods

# CityUser class attributes and methods

# CityAngel class attributes and methods

# SolutionProvider class attributes and methods

# Citizen class attributes and methods

# Dashboard class attributes and methods
Dashboard_code: Property = Property(name="code", type=str_type)
Dashboard.attributes={Dashboard_code}

# MapData class attributes and methods
MapData_title: Property = Property(name="title", type=str_type)
MapData.attributes={MapData_title}

# GeoJson class attributes and methods
GeoJson_data: Property = Property(name="data", type=str_type)
GeoJson.attributes={GeoJson_data}

# WMS class attributes and methods
WMS_url: Property = Property(name="url", type=str_type)
WMS_name: Property = Property(name="name", type=str_type)
WMS.attributes={WMS_url, WMS_name}

# KPIParticipants class attributes and methods
KPIParticipants_target: Property = Property(name="target", type=int_type)
KPIParticipants.attributes={KPIParticipants_target}

# KPIWasteAvoided class attributes and methods
KPIWasteAvoided_target: Property = Property(name="target", type=int_type)
KPIWasteAvoided.attributes={KPIWasteAvoided_target}

# KPICo2Avoided class attributes and methods
KPICo2Avoided_target: Property = Property(name="target", type=int_type)
KPICo2Avoided.attributes={KPICo2Avoided_target}

# KPIWasteSorted class attributes and methods
KPIWasteSorted_target: Property = Property(name="target", type=int_type)
KPIWasteSorted.attributes={KPIWasteSorted_target}

# KPITextileWastePerPerson class attributes and methods

# Relationships
values: BinaryAssociation = BinaryAssociation(name="values", ends={
        Property(name="values", type=KPI, multiplicity=Multiplicity(1, 1), is_navigable=False),
        Property(name="values", type=KPIValue, multiplicity=Multiplicity(0, "*"), is_navigable=True)})
kpis: BinaryAssociation = BinaryAssociation(name="kpis", ends={
        Property(name="kpis", type=City, multiplicity=Multiplicity(1, 1), is_navigable=False),
        Property(name="kpis", type=KPI, multiplicity=Multiplicity(0, "*"), is_navigable=True)})
visualizedBy: BinaryAssociation = BinaryAssociation(name="visualizedBy", ends={
        Property(name="visualizedBy", type=Visualisation, multiplicity=Multiplicity(0, "*"), is_navigable=True),
        Property(name="visualizedBy", type=KPI, multiplicity=Multiplicity(1, 1), is_navigable=False)})
has: BinaryAssociation = BinaryAssociation(name="has", ends={
        Property(name="has", type=City, multiplicity=Multiplicity(1, 1), is_navigable=False),
        Property(name="has", type=Dashboard, multiplicity=Multiplicity(0, "*"), is_navigable=True)})
consistsOf: BinaryAssociation = BinaryAssociation(name="consistsOf", ends={
        Property(name="consistsOf", type=Dashboard, multiplicity=Multiplicity(1, 1), is_navigable=False),
        Property(name="consistsOf", type=Visualisation, multiplicity=Multiplicity(0, "*"), is_navigable=True)})
shows: BinaryAssociation = BinaryAssociation(name="shows", ends={
        Property(name="shows", type=Table, multiplicity=Multiplicity(1, 1), is_navigable=False),
        Property(name="shows", type=TableColumn, multiplicity=Multiplicity(0, "*"), is_navigable=True)})
operatedBy: BinaryAssociation = BinaryAssociation(name="operatedBy", ends={
        Property(name="operatedBy", type=City, multiplicity=Multiplicity(1, 1), is_navigable=False),
        Property(name="operatedBy", type=User, multiplicity=Multiplicity(0, "*"), is_navigable=True)})
hasMapData: BinaryAssociation = BinaryAssociation(name="hasMapData", ends={
        Property(name="hasMapData", type=City, multiplicity=Multiplicity(1, 1), is_navigable=False),
        Property(name="hasMapData", type=MapData, multiplicity=Multiplicity(0, "*"), is_navigable=True)})
isDisplayedOnMap: BinaryAssociation = BinaryAssociation(name="isDisplayedOnMap", ends={
        Property(name="isDisplayedOnMap", type=Map, multiplicity=Multiplicity(0, "*"), is_navigable=True),
        Property(name="isDisplayedOnMap", type=MapData, multiplicity=Multiplicity(1, 1), is_navigable=False)})

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
domain: DomainModel = DomainModel(
				name="Domain Model",
				types={City, KPI, KPIValue, KPITemp, KPITraffic, KPICollectedWaste, KPISecondHandCustomers, KPIMoney, KPITotalRenewableEnergy, KPINumberHouseholdRenewableEnergy, KPIPeakSolarEnergy, Visualisation, Table, PieChart, StatChart, LineChart, TableColumn, Map, User, Admin, CityUser, CityAngel, SolutionProvider, Citizen, Dashboard, MapData, GeoJson, WMS, KPIParticipants, KPIWasteAvoided, KPICo2Avoided, KPIWasteSorted, KPITextileWastePerPerson},
				associations={values, kpis, visualizedBy, has, consistsOf, shows, operatedBy, hasMapData, isDisplayedOnMap},
				generalizations={gen_KPI_KPICollectedWaste, gen_KPI_KPISecondHandCustomers, gen_KPI_KPITotalRenewableEnergy, gen_KPI_KPINumberHouseholdRenewableEnergy, gen_KPI_KPIPeakSolarEnergy, gen_KPI_KPITemp, gen_KPI_KPITraffic, gen_KPI_KPIMoney, gen_Visualisation_Table, gen_Visualisation_PieChart, gen_Visualisation_StatChart, gen_Visualisation_LineChart, gen_Visualisation_Map, gen_User_Admin, gen_User_CityUser, gen_User_CityAngel, gen_User_SolutionProvider, gen_User_Citizen, gen_MapData_GeoJson, gen_MapData_WMS, gen_KPI_KPIParticipants, gen_KPI_KPIWasteAvoided, gen_KPI_KPICo2Avoided, gen_KPI_KPIWasteSorted, gen_KPI_KPITextileWastePerPerson},
				enumerations=set()
				)
