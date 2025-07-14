from classes import *

tempValue1 = KPIValue(kpiValue = "22", timestamp = "2025-07-07 10:00:00", currentStanding = "Good")

moneyValue1 = KPIValue(kpiValue = "1200", timestamp = "2025-07-07 10:00:00", currentStanding = "Good")

kpiTrafficCongestion_Sofia = KPI(id_kpi = "traffic001", name = "Traffic Congestion Level", category = "Transport", description = "Measures the level of traffic congestion", provider = "TransportDepartment", calculationFrequency = "Hourly", unitText = "Number of Cars", minThreshold = "10", maxThreshold = "50")

kpiTotalRenewableEnergy_Differdange = KPI(id_kpi = "energy001", name = "Percentage of renewable energy in Differdange", category = "Energy", description = "Percentage of renewable energy in Differdange based on total amount of energy", provider = "Solution Provider", calculationFrequency = "Monthly", unitText = "Percentage", minThreshold = "15", maxThreshold = "25")

kpiNumberHouseholdRenewableEnergy_Differdange = KPI(id_kpi = "energy002", name = "Household with renewable energy", category = "Energy", description = "Number of households producing any kind of renewable energy", provider = "Citizens", calculationFrequency = "Monthly", unitText = "Number", minThreshold = "300", maxThreshold = "700")

kpiPeakSolarEnergy_Differdange = KPI(id_kpi = "energy003", name = "Peak solar energy", category = "Energy", description = "Peak solar energy in Differdange", provider = "Differdange", calculationFrequency = "Monthly", unitText = "KW peak", minThreshold = "800", maxThreshold = "1200")

kpiCollectedWaste_Cascais = KPI(id_kpi = "waste001", name = "Collected Textile Waste in Ton", category = "Waste", description = "Total textile waste collected in Cascais", provider = "WasteDepartment", calculationFrequency = "Weekly", unitText = "Tons", minThreshold = "5", maxThreshold = "15")

kpiCSecondHandCustomers_Cascais = KPI(id_kpi = "waste002", name = "Customers in second hand shops", category = "Waste", description = "Daily number of customers in second hand shops", provider = "Shops", calculationFrequency = "Daily", unitText = "Number of people", minThreshold = "500", maxThreshold = "1500")

kpiCollectedClothes = KPI(id_kpi = "waste_011", name = "Amount of collected textile clothes", category = "Waste", description = "Amount of collected textile clothes", provider = "City of Torino", calculationFrequency = "Monthly", unitText = "Kg", minThreshold = "5500", maxThreshold = "6500")

kpiCollectedTextileWaste = KPI(id_kpi = "waste_012", name = "Amount of other types of textiles collected", category = "Waste", description = "Amount of other types of textiles collected", provider = "City of Torino", calculationFrequency = "Monthly", unitText = "Kg", minThreshold = "4500", maxThreshold = "5500")

kpiCollectedTextileWasteEcoIsole = KPI(id_kpi = "waste_014", name = "Amount of textile left in the indifferentiated waste (Eco-Isole)", category = "Waste", description = "Amount of textile left in the indifferentiated waste (Eco-Isole)", provider = "City of Torino", calculationFrequency = "Monthly", unitText = "Kg", minThreshold = "2800", maxThreshold = "3200")

kpiInformedCitizens = KPI(id_kpi = "participants_001", name = "Citizens informed through Re4Circular", category = "Waste", description = "Citizens informed through Re4Circular", provider = "Re4Circular", calculationFrequency = "Monthly", unitText = "Number of people", minThreshold = "800", maxThreshold = "1200")

kpiDiscardedWaste = KPI(id_kpi = "waste_013", name = "Amount of textile waste discarded from the differentiated share", category = "Waste", description = "Amount of textile waste discarded from the differentiated share", provider = "City of Torino", calculationFrequency = "Monthly", unitText = "Kg", minThreshold = "40", maxThreshold = "60")

kpiInvolvedCitizens = KPI(id_kpi = "participants_002", name = "Citizens active on Re4Circular", category = "Waste", description = "Citizens active on Re4Circular", provider = "Re4Circular", calculationFrequency = "Monthly", unitText = "Number of people", minThreshold = "400", maxThreshold = "600")

kpiInformedBusinesses = KPI(id_kpi = "participants_003", name = "Businesses informed through Re4Circular", category = "Waste", description = "Businesses informed through Re4Circular", provider = "Re4Circular", calculationFrequency = "Monthly", unitText = "Number of businesses", minThreshold = "40", maxThreshold = "60")

kpiInvolvedBusinesses = KPI(id_kpi = "participants_004", name = "Businesses active on Re4Circular", category = "Waste", description = "Businesses active on Re4Circular", provider = "Re4Circular", calculationFrequency = "Monthly", unitText = "Number of businesses", minThreshold = "15", maxThreshold = "25")

kpiReuseBusinesses = KPI(id_kpi = "participants_005", name = "Businesses re-using textiles through Re4Circular", category = "Waste", description = "Businesses re-using textiles through Re4Circular", provider = "Re4Circular", calculationFrequency = "Monthly", unitText = "Number of businesses", minThreshold = "8", maxThreshold = "12")

kpiWasteAvoided = KPI(id_kpi = "waste_001", name = "Waste avoided through Re4Circular", category = "Waste", description = "Waste avoided through Re4Circular (collecting material before it becomes waste)", provider = "Re4Circular", calculationFrequency = "Monthly", unitText = "Tons", minThreshold = "8", maxThreshold = "12")

kpiCo2Avoided = KPI(id_kpi = "co2_001", name = "Co2 avoided through collection of waste through Re4Circular", category = "Waste", description = "Co2 avoided through collection of waste through Re4Circular", provider = "DKSR", calculationFrequency = "Monthly", unitText = "Tons", minThreshold = "8", maxThreshold = "2")

kpiWasteSorted = KPI(id_kpi = "waste_006", name = "Amount of correctly sorted waste in bins using ReLearn sensors", category = "Waste", description = "Amount of correctly sorted waste in bins using ReLearn sensors", provider = "ReLearn", calculationFrequency = "Monthly", unitText = "Kg", minThreshold = "800", maxThreshold = "1200")

kpiCollectedWaste = KPI(id_kpi = "waste_007", name = "Amount of collected textile waste", category = "Waste", description = "Amount of collected textile waste", provider = "ReLearn", calculationFrequency = "Monthly", unitText = "Kg", minThreshold = "5000", maxThreshold = "7000")

kpiTextileWastePerPerson = KPI(id_kpi = "waste_010", name = "Amount of yearly textile waste per person", category = "Waste", description = "Amount of yearly textile waste per person", provider = "City", calculationFrequency = "Yearly", unitText = "Kg", minThreshold = "10", maxThreshold = "30")

kpiHouseholdInvolvedThreeBagCollection = KPI(id_kpi = "participants_006", name = "Households participating in the three bags collection", category = "Waste", description = "Households participating in the three bags collection", provider = "Torino", calculationFrequency = "Monthly", unitText = "Households", minThreshold = "80", maxThreshold = "120")

kpiCollectedClothes2 = KPI(id_kpi = "waste_015", name = "Amount of collected textile clothes", category = "Waste", description = "Amount of collected textile clothes", provider = "City of Torino", calculationFrequency = "Monthly", unitText = "Kg", minThreshold = "90", maxThreshold = "110")

kpiTemp_Differdange = KPI(id_kpi = "temp001", name = "Average Temperature", category = "Environment", description = "Measures the average temperature of the city", provider = "WeatherService", calculationFrequency = "Daily", unitText = "Celsius", minThreshold = "15", maxThreshold = "35", tempValue1)

kpiMoney_Differdange = KPI(id_kpi = "money001", name = "Money Invested", category = "Environment", description = "Measures the money invested in green stuff", provider = "BankService", calculationFrequency = "Weekly", unitText = "Euros", minThreshold = "500", maxThreshold = "2000", moneyValue1)

sofia = City(name = "Sofia", kpiTrafficCongestion_Sofia)

cascais = City(name = "Cascais", kpiCollectedWaste_Cascais, kpiCSecondHandCustomers_Cascais)

torino = City(name = "Torino", kpiCollectedClothes, kpiCollectedTextileWaste, kpiCollectedTextileWasteEcoIsole, kpiInformedCitizens, kpiDiscardedWaste, kpiInvolvedCitizens, kpiInformedBusinesses, kpiInvolvedBusinesses, kpiReuseBusinesses, kpiWasteAvoided, kpiCo2Avoided, kpiWasteSorted, kpiCollectedWaste, kpiTextileWastePerPerson, kpiHouseholdInvolvedThreeBagCollection, kpiCollectedClothes2)

differdange = City(name = "Differdange", kpiTemp_Differdange, kpiMoney_Differdange, kpiTotalRenewableEnergy_Differdange, kpiNumberHouseholdRenewableEnergy_Differdange, kpiPeakSolarEnergy_Differdange)

athens = City(name = "Athens")

grenoble = City(name = "Grenoble-Alpes")

maribor = City(name = "Maribor")

ioannina = City(name = "Ioannina")
