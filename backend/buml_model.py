"""
Complete BUML Model Builder for Climaborough Data Platform
Based on database_structure.plantuml - EXACT MATCH

This creates a complete domain model matching the PlantUML database structure exactly.
"""

from besser.BUML.metamodel.structural import (
    DomainModel, Class, Property, BinaryAssociation, Generalization,
    Multiplicity, Enumeration, EnumerationLiteral,
    StringType, IntegerType, FloatType, BooleanType, DateTimeType
)


def buml_model() -> DomainModel:
    """
    Create the complete Climaborough domain model matching database_structure.plantuml.
    """
    
    print("=" * 70)
    print("CREATING COMPLETE CLIMABOROUGH BUML MODEL")
    print("Based on: plantuml/database_structure.plantuml")
    print("=" * 70)
    print()
    
    model = DomainModel(name="ClimaDataPlatform")
    
    # ========== STEP 1: ENUMERATIONS ==========
    print("Step 1: Creating Enumerations...")
    print("-" * 70)
    
    # Visualization Type (for discriminator)
    viz_type = Enumeration(name="VisualizationType")
    viz_type.add_literal(EnumerationLiteral(name="line", owner=viz_type))
    viz_type.add_literal(EnumerationLiteral(name="bar", owner=viz_type))
    viz_type.add_literal(EnumerationLiteral(name="pie", owner=viz_type))
    viz_type.add_literal(EnumerationLiteral(name="stat", owner=viz_type))
    viz_type.add_literal(EnumerationLiteral(name="table", owner=viz_type))
    viz_type.add_literal(EnumerationLiteral(name="map", owner=viz_type))
    model.add_type(viz_type)
    
    # Map Data Type (for discriminator)
    map_type = Enumeration(name="MapDataType")
    map_type.add_literal(EnumerationLiteral(name="wms", owner=map_type))
    map_type.add_literal(EnumerationLiteral(name="geojson", owner=map_type))
    model.add_type(map_type)
    
    print(f"  ✓ Created {len(list(model.get_enumerations()))} enumerations")
    print()
    
    # ========== STEP 2: CORE ENTITY CLASSES ==========
    print("Step 2: Creating Core Entity Classes...")
    print("-" * 70)
    
    # === CITY ===
    city = Class(name="City")
    city.metadata = {"table_name": "cities"}
    city.add_attribute(Property(name="id", type=IntegerType, owner=city, multiplicity=Multiplicity(1, 1),
                                metadata={"primary_key": True}))
    city.add_attribute(Property(name="name", type=StringType, owner=city, multiplicity=Multiplicity(1, 1),
                                metadata={"length": 100, "unique": True, "index": True}))
    city.add_attribute(Property(name="code", type=StringType, owner=city, multiplicity=Multiplicity(1, 1),
                                metadata={"length": 20, "unique": True, "index": True}))
    city.add_attribute(Property(name="country", type=StringType, owner=city, multiplicity=Multiplicity(1, 1),
                                metadata={"length": 100}))
    city.add_attribute(Property(name="timezone", type=StringType, owner=city, multiplicity=Multiplicity(1, 1),
                                metadata={"length": 50}))
    city.add_attribute(Property(name="created_at", type=DateTimeType, owner=city, multiplicity=Multiplicity(1, 1),
                                metadata={"timestamp": True}))
    city.add_attribute(Property(name="updated_at", type=DateTimeType, owner=city, multiplicity=Multiplicity(1, 1),
                                metadata={"timestamp": True, "onupdate": True}))
    model.add_type(city)
    print("  ✓ City (7 fields)")
    
    # === DASHBOARD ===
    dashboard = Class(name="Dashboard")
    dashboard.metadata = {"table_name": "dashboards"}
    dashboard.add_attribute(Property(name="id", type=IntegerType, owner=dashboard, multiplicity=Multiplicity(1, 1),
                                    metadata={"primary_key": True}))
    dashboard.add_attribute(Property(name="code", type=StringType, owner=dashboard, multiplicity=Multiplicity(1, 1),
                                    metadata={"length": 100, "index": True}))
    dashboard.add_attribute(Property(name="title", type=StringType, owner=dashboard, multiplicity=Multiplicity(1, 1),
                                    metadata={"length": 200}))
    dashboard.add_attribute(Property(name="description", type=StringType, owner=dashboard, multiplicity=Multiplicity(0, 1),
                                    metadata={"length": 2000, "type": "Text"}))
    dashboard.add_attribute(Property(name="is_public", type=BooleanType, owner=dashboard, multiplicity=Multiplicity(1, 1),
                                    metadata={"default": True}))
    dashboard.add_attribute(Property(name="created_at", type=DateTimeType, owner=dashboard, multiplicity=Multiplicity(1, 1),
                                    metadata={"timestamp": True}))
    dashboard.add_attribute(Property(name="updated_at", type=DateTimeType, owner=dashboard, multiplicity=Multiplicity(1, 1),
                                    metadata={"timestamp": True, "onupdate": True}))
    model.add_type(dashboard)
    print("  ✓ Dashboard (7 fields)")
    
    # === DASHBOARD SECTION ===
    section = Class(name="DashboardSection")
    section.metadata = {"table_name": "dashboard_sections"}
    section.add_attribute(Property(name="id", type=IntegerType, owner=section, multiplicity=Multiplicity(1, 1),
                                  metadata={"primary_key": True}))
    section.add_attribute(Property(name="name", type=StringType, owner=section, multiplicity=Multiplicity(1, 1),
                                  metadata={"length": 100}))
    section.add_attribute(Property(name="description", type=StringType, owner=section, multiplicity=Multiplicity(0, 1),
                                  metadata={"length": 2000, "type": "Text"}))
    section.add_attribute(Property(name="order", type=IntegerType, owner=section, multiplicity=Multiplicity(1, 1),
                                  metadata={"default": 0}))
    section.add_attribute(Property(name="is_active", type=BooleanType, owner=section, multiplicity=Multiplicity(1, 1),
                                  metadata={"default": True}))
    section.add_attribute(Property(name="created_at", type=DateTimeType, owner=section, multiplicity=Multiplicity(1, 1),
                                  metadata={"timestamp": True}))
    section.add_attribute(Property(name="updated_at", type=DateTimeType, owner=section, multiplicity=Multiplicity(1, 1),
                                  metadata={"timestamp": True, "onupdate": True}))
    model.add_type(section)
    print("  ✓ DashboardSection (7 fields)")
    print()
    
    # ========== STEP 3: KPI SYSTEM ==========
    print("Step 3: Creating KPI System Classes...")
    print("-" * 70)
    
    # === KPI ===
    kpi = Class(name="KPI")
    kpi.metadata = {"table_name": "kpis"}
    kpi.add_attribute(Property(name="id", type=IntegerType, owner=kpi, multiplicity=Multiplicity(1, 1),
                              metadata={"primary_key": True}))
    kpi.add_attribute(Property(name="id_kpi", type=StringType, owner=kpi, multiplicity=Multiplicity(1, 1),
                              metadata={"length": 100, "unique": True, "index": True}))
    kpi.add_attribute(Property(name="name", type=StringType, owner=kpi, multiplicity=Multiplicity(1, 1),
                              metadata={"length": 200}))
    kpi.add_attribute(Property(name="description", type=StringType, owner=kpi, multiplicity=Multiplicity(0, 1),
                              metadata={"length": 2000, "type": "Text"}))
    kpi.add_attribute(Property(name="category", type=StringType, owner=kpi, multiplicity=Multiplicity(1, 1),
                              metadata={"length": 100, "index": True}))
    kpi.add_attribute(Property(name="unit_text", type=StringType, owner=kpi, multiplicity=Multiplicity(1, 1),
                              metadata={"length": 50}))
    kpi.add_attribute(Property(name="provider", type=StringType, owner=kpi, multiplicity=Multiplicity(0, 1),
                              metadata={"length": 100}))
    kpi.add_attribute(Property(name="calculation_frequency", type=StringType, owner=kpi, multiplicity=Multiplicity(0, 1),
                              metadata={"length": 50}))
    kpi.add_attribute(Property(name="min_threshold", type=FloatType, owner=kpi, multiplicity=Multiplicity(0, 1)))
    kpi.add_attribute(Property(name="max_threshold", type=FloatType, owner=kpi, multiplicity=Multiplicity(0, 1)))
    kpi.add_attribute(Property(name="has_category_label", type=BooleanType, owner=kpi, multiplicity=Multiplicity(1, 1),
                              metadata={"default": False}))
    kpi.add_attribute(Property(name="category_label_dictionary", type=StringType, owner=kpi, multiplicity=Multiplicity(0, 1),
                              metadata={"type": "JSON"}))
    kpi.add_attribute(Property(name="is_active", type=BooleanType, owner=kpi, multiplicity=Multiplicity(1, 1),
                              metadata={"default": True}))
    kpi.add_attribute(Property(name="created_at", type=DateTimeType, owner=kpi, multiplicity=Multiplicity(1, 1),
                              metadata={"timestamp": True}))
    kpi.add_attribute(Property(name="updated_at", type=DateTimeType, owner=kpi, multiplicity=Multiplicity(1, 1),
                              metadata={"timestamp": True, "onupdate": True}))
    model.add_type(kpi)
    print("  ✓ KPI (15 fields)")
    
    # === KPI VALUE ===
    kpi_value = Class(name="KPIValue")
    kpi_value.metadata = {"table_name": "kpi_values"}
    kpi_value.add_attribute(Property(name="id", type=IntegerType, owner=kpi_value, multiplicity=Multiplicity(1, 1),
                                    metadata={"primary_key": True}))
    kpi_value.add_attribute(Property(name="value", type=FloatType, owner=kpi_value, multiplicity=Multiplicity(1, 1)))
    kpi_value.add_attribute(Property(name="timestamp", type=DateTimeType, owner=kpi_value, multiplicity=Multiplicity(1, 1),
                                    metadata={"index": True}))
    kpi_value.add_attribute(Property(name="category_label", type=StringType, owner=kpi_value, multiplicity=Multiplicity(0, 1),
                                    metadata={"length": 100}))
    model.add_type(kpi_value)
    print("  ✓ KPIValue (4 fields)")
    print()
    
    # ========== STEP 4: VISUALIZATION SYSTEM (POLYMORPHIC) ==========
    print("Step 4: Creating Visualization System (Polymorphic)...")
    print("-" * 70)
    
    # === VISUALIZATION (BASE) ===
    visualization = Class(name="Visualization")
    visualization.metadata = {
        "table_name": "visualizations",
        "polymorphic": True,
        "polymorphic_identity": "visualization",
        "inheritance": "joined"
    }
    visualization.add_attribute(Property(name="id", type=IntegerType, owner=visualization, multiplicity=Multiplicity(1, 1),
                                        metadata={"primary_key": True}))
    visualization.add_attribute(Property(name="type", type=StringType, owner=visualization, multiplicity=Multiplicity(1, 1),
                                        metadata={"length": 50, "discriminator": True, "index": True}))
    visualization.add_attribute(Property(name="title", type=StringType, owner=visualization, multiplicity=Multiplicity(1, 1),
                                        metadata={"length": 200}))
    visualization.add_attribute(Property(name="width", type=IntegerType, owner=visualization, multiplicity=Multiplicity(1, 1),
                                        metadata={"default": 4}))
    visualization.add_attribute(Property(name="height", type=IntegerType, owner=visualization, multiplicity=Multiplicity(1, 1),
                                        metadata={"default": 8}))
    visualization.add_attribute(Property(name="x_position", type=IntegerType, owner=visualization, multiplicity=Multiplicity(1, 1),
                                        metadata={"default": 0}))
    visualization.add_attribute(Property(name="y_position", type=IntegerType, owner=visualization, multiplicity=Multiplicity(1, 1),
                                        metadata={"default": 0}))
    visualization.add_attribute(Property(name="i", type=StringType, owner=visualization, multiplicity=Multiplicity(1, 1),
                                        metadata={"length": 100}))
    visualization.add_attribute(Property(name="created_at", type=DateTimeType, owner=visualization, multiplicity=Multiplicity(1, 1),
                                        metadata={"timestamp": True}))
    visualization.add_attribute(Property(name="updated_at", type=DateTimeType, owner=visualization, multiplicity=Multiplicity(1, 1),
                                        metadata={"timestamp": True, "onupdate": True}))
    model.add_type(visualization)
    print("  ✓ Visualization [BASE] (10 fields)")
    
    # === LINE CHART ===
    line_chart = Class(name="LineChart")
    line_chart.metadata = {"table_name": "line_charts", "polymorphic_identity": "linechart", "parent": "Visualization"}
    line_chart.add_attribute(Property(name="x_title", type=StringType, owner=line_chart, multiplicity=Multiplicity(1, 1),
                                     metadata={"length": 100}))
    line_chart.add_attribute(Property(name="y_title", type=StringType, owner=line_chart, multiplicity=Multiplicity(1, 1),
                                     metadata={"length": 100}))
    line_chart.add_attribute(Property(name="color", type=StringType, owner=line_chart, multiplicity=Multiplicity(1, 1),
                                     metadata={"length": 50, "default": "#3498db"}))
    model.add_type(line_chart)
    print("  ✓ LineChart [CHILD] (3 fields)")
    
    # === BAR CHART ===
    bar_chart = Class(name="BarChart")
    bar_chart.metadata = {"table_name": "bar_charts", "polymorphic_identity": "barchart", "parent": "Visualization"}
    bar_chart.add_attribute(Property(name="orientation", type=StringType, owner=bar_chart, multiplicity=Multiplicity(1, 1),
                                    metadata={"length": 20, "default": "vertical"}))
    model.add_type(bar_chart)
    print("  ✓ BarChart [CHILD] (1 field)")
    
    # === PIE CHART ===
    pie_chart = Class(name="PieChart")
    pie_chart.metadata = {"table_name": "pie_charts", "polymorphic_identity": "piechart", "parent": "Visualization"}
    pie_chart.add_attribute(Property(name="show_legend", type=BooleanType, owner=pie_chart, multiplicity=Multiplicity(1, 1),
                                    metadata={"default": True}))
    model.add_type(pie_chart)
    print("  ✓ PieChart [CHILD] (1 field)")
    
    # === STAT CHART ===
    stat_chart = Class(name="StatChart")
    stat_chart.metadata = {"table_name": "stat_charts", "polymorphic_identity": "statchart", "parent": "Visualization"}
    stat_chart.add_attribute(Property(name="unit", type=StringType, owner=stat_chart, multiplicity=Multiplicity(1, 1),
                                     metadata={"length": 50}))
    stat_chart.add_attribute(Property(name="show_trend", type=BooleanType, owner=stat_chart, multiplicity=Multiplicity(1, 1),
                                     metadata={"default": False}))
    model.add_type(stat_chart)
    print("  ✓ StatChart [CHILD] (2 fields)")
    
    # === TABLE ===
    table = Class(name="Table")
    table.metadata = {"table_name": "tables", "polymorphic_identity": "table", "parent": "Visualization"}
    table.add_attribute(Property(name="pagination_enabled", type=BooleanType, owner=table, multiplicity=Multiplicity(1, 1),
                                metadata={"default": True}))
    table.add_attribute(Property(name="page_size", type=IntegerType, owner=table, multiplicity=Multiplicity(1, 1),
                                metadata={"default": 10}))
    model.add_type(table)
    print("  ✓ Table [CHILD] (2 fields)")
    
    # === TABLE COLUMN ===
    table_column = Class(name="TableColumn")
    table_column.metadata = {"table_name": "table_columns"}
    table_column.add_attribute(Property(name="id", type=IntegerType, owner=table_column, multiplicity=Multiplicity(1, 1),
                                       metadata={"primary_key": True}))
    table_column.add_attribute(Property(name="name", type=StringType, owner=table_column, multiplicity=Multiplicity(1, 1),
                                       metadata={"length": 100}))
    table_column.add_attribute(Property(name="header", type=StringType, owner=table_column, multiplicity=Multiplicity(1, 1),
                                       metadata={"length": 100}))
    table_column.add_attribute(Property(name="data_type", type=StringType, owner=table_column, multiplicity=Multiplicity(1, 1),
                                       metadata={"length": 50, "default": "string"}))
    table_column.add_attribute(Property(name="sortable", type=BooleanType, owner=table_column, multiplicity=Multiplicity(1, 1),
                                       metadata={"default": True}))
    table_column.add_attribute(Property(name="filterable", type=BooleanType, owner=table_column, multiplicity=Multiplicity(1, 1),
                                       metadata={"default": False}))
    table_column.add_attribute(Property(name="order", type=IntegerType, owner=table_column, multiplicity=Multiplicity(1, 1),
                                       metadata={"default": 0}))
    model.add_type(table_column)
    print("  ✓ TableColumn (7 fields)")
    
    # === MAP ===
    map_viz = Class(name="Map")
    map_viz.metadata = {"table_name": "maps", "polymorphic_identity": "map", "parent": "Visualization"}
    map_viz.add_attribute(Property(name="default_zoom", type=IntegerType, owner=map_viz, multiplicity=Multiplicity(1, 1),
                                  metadata={"default": 10}))
    map_viz.add_attribute(Property(name="center_lat", type=FloatType, owner=map_viz, multiplicity=Multiplicity(0, 1)))
    map_viz.add_attribute(Property(name="center_lon", type=FloatType, owner=map_viz, multiplicity=Multiplicity(0, 1)))
    model.add_type(map_viz)
    print("  ✓ Map [CHILD] (3 fields)")
    print()
    
    # ========== STEP 5: MAP DATA SYSTEM (POLYMORPHIC) ==========
    print("Step 5: Creating Map Data System (Polymorphic)...")
    print("-" * 70)
    
    # === MAP DATA (BASE) ===
    map_data = Class(name="MapData")
    map_data.metadata = {
        "table_name": "map_data",
        "polymorphic": True,
        "polymorphic_identity": "mapdata",
        "inheritance": "joined"
    }
    map_data.add_attribute(Property(name="id", type=IntegerType, owner=map_data, multiplicity=Multiplicity(1, 1),
                                   metadata={"primary_key": True}))
    map_data.add_attribute(Property(name="type", type=StringType, owner=map_data, multiplicity=Multiplicity(1, 1),
                                   metadata={"length": 50, "discriminator": True, "index": True}))
    map_data.add_attribute(Property(name="title", type=StringType, owner=map_data, multiplicity=Multiplicity(1, 1),
                                   metadata={"length": 200}))
    map_data.add_attribute(Property(name="description", type=StringType, owner=map_data, multiplicity=Multiplicity(0, 1),
                                   metadata={"length": 2000, "type": "Text"}))
    map_data.add_attribute(Property(name="is_active", type=BooleanType, owner=map_data, multiplicity=Multiplicity(1, 1),
                                   metadata={"default": True}))
    map_data.add_attribute(Property(name="created_at", type=DateTimeType, owner=map_data, multiplicity=Multiplicity(1, 1),
                                   metadata={"timestamp": True}))
    map_data.add_attribute(Property(name="updated_at", type=DateTimeType, owner=map_data, multiplicity=Multiplicity(1, 1),
                                   metadata={"timestamp": True, "onupdate": True}))
    model.add_type(map_data)
    print("  ✓ MapData [BASE] (7 fields)")
    
    # === WMS ===
    wms = Class(name="WMS")
    wms.metadata = {"table_name": "wms_layers", "polymorphic_identity": "wms", "parent": "MapData"}
    wms.add_attribute(Property(name="url", type=StringType, owner=wms, multiplicity=Multiplicity(1, 1),
                              metadata={"length": 500}))
    wms.add_attribute(Property(name="layer_name", type=StringType, owner=wms, multiplicity=Multiplicity(1, 1),
                              metadata={"length": 200}))
    wms.add_attribute(Property(name="format", type=StringType, owner=wms, multiplicity=Multiplicity(1, 1),
                              metadata={"length": 50, "default": "image/png"}))
    wms.add_attribute(Property(name="transparent", type=BooleanType, owner=wms, multiplicity=Multiplicity(1, 1),
                              metadata={"default": True}))
    model.add_type(wms)
    print("  ✓ WMS [CHILD] (4 fields)")
    
    # === GEOJSON ===
    geojson = Class(name="GeoJson")
    geojson.metadata = {"table_name": "geojson_data", "polymorphic_identity": "geojson", "parent": "MapData"}
    geojson.add_attribute(Property(name="data", type=StringType, owner=geojson, multiplicity=Multiplicity(1, 1),
                                  metadata={"type": "JSON"}))
    geojson.add_attribute(Property(name="style", type=StringType, owner=geojson, multiplicity=Multiplicity(0, 1),
                                  metadata={"type": "JSON"}))
    model.add_type(geojson)
    print("  ✓ GeoJson [CHILD] (2 fields)")
    print()
    
    # ========== STEP 6: RELATIONSHIPS ==========
    print("Step 6: Creating Relationships...")
    print("-" * 70)
    
    # City <-> Dashboard (1:N)
    city_dashboards = BinaryAssociation(
        name="city_dashboards",
        ends={
            Property(name="city", type=city, owner=dashboard, multiplicity=Multiplicity(1, 1), is_navigable=False),
            Property(name="dashboards", type=dashboard, owner=city, multiplicity=Multiplicity(0, "*"), is_navigable=True)
        }
    )
    model.add_association(city_dashboards)
    print("  ✓ City <-> Dashboard (1:N)")
    
    # City <-> KPI (1:N)
    city_kpis = BinaryAssociation(
        name="city_kpis",
        ends={
            Property(name="city", type=city, owner=kpi, multiplicity=Multiplicity(1, 1), is_navigable=False),
            Property(name="kpis", type=kpi, owner=city, multiplicity=Multiplicity(0, "*"), is_navigable=True)
        }
    )
    model.add_association(city_kpis)
    print("  ✓ City <-> KPI (1:N)")
    
    # City <-> MapData (1:N)
    city_map_data = BinaryAssociation(
        name="city_map_data",
        ends={
            Property(name="city", type=city, owner=map_data, multiplicity=Multiplicity(1, 1), is_navigable=False),
            Property(name="map_data", type=map_data, owner=city, multiplicity=Multiplicity(0, "*"), is_navigable=True)
        }
    )
    model.add_association(city_map_data)
    print("  ✓ City <-> MapData (1:N)")
    
    # Dashboard <-> DashboardSection (1:N)
    dashboard_sections = BinaryAssociation(
        name="dashboard_sections",
        ends={
            Property(name="dashboard", type=dashboard, owner=section, multiplicity=Multiplicity(1, 1), is_navigable=False),
            Property(name="sections", type=section, owner=dashboard, multiplicity=Multiplicity(0, "*"), is_navigable=True)
        }
    )
    model.add_association(dashboard_sections)
    print("  ✓ Dashboard <-> DashboardSection (1:N)")
    
    # Dashboard <-> Visualization (1:N)
    dashboard_viz = BinaryAssociation(
        name="dashboard_visualizations",
        ends={
            Property(name="dashboard", type=dashboard, owner=visualization, multiplicity=Multiplicity(1, 1), is_navigable=False),
            Property(name="visualizations", type=visualization, owner=dashboard, multiplicity=Multiplicity(0, "*"), is_navigable=True)
        }
    )
    model.add_association(dashboard_viz)
    print("  ✓ Dashboard <-> Visualization (1:N)")
    
    # DashboardSection <-> Visualization (1:N)
    section_viz = BinaryAssociation(
        name="section_visualizations",
        ends={
            Property(name="section", type=section, owner=visualization, multiplicity=Multiplicity(1, 1), is_navigable=False),
            Property(name="visualizations", type=visualization, owner=section, multiplicity=Multiplicity(0, "*"), is_navigable=True)
        }
    )
    model.add_association(section_viz)
    print("  ✓ DashboardSection <-> Visualization (1:N)")
    
    # KPI <-> KPIValue (1:N)
    kpi_values = BinaryAssociation(
        name="kpi_values",
        ends={
            Property(name="kpi", type=kpi, owner=kpi_value, multiplicity=Multiplicity(1, 1), is_navigable=False),
            Property(name="values", type=kpi_value, owner=kpi, multiplicity=Multiplicity(0, "*"), is_navigable=True)
        }
    )
    model.add_association(kpi_values)
    print("  ✓ KPI <-> KPIValue (1:N)")
    
    # Visualization <-> KPI (N:1, optional)
    viz_kpi = BinaryAssociation(
        name="visualization_kpi",
        ends={
            Property(name="kpi", type=kpi, owner=visualization, multiplicity=Multiplicity(0, 1), is_navigable=False),
            Property(name="visualizations", type=visualization, owner=kpi, multiplicity=Multiplicity(0, "*"), is_navigable=True)
        }
    )
    model.add_association(viz_kpi)
    print("  ✓ Visualization <-> KPI (N:1)")
    
    # Table <-> TableColumn (1:N)
    table_columns = BinaryAssociation(
        name="table_columns",
        ends={
            Property(name="table", type=table, owner=table_column, multiplicity=Multiplicity(1, 1), is_navigable=False),
            Property(name="columns", type=table_column, owner=table, multiplicity=Multiplicity(0, "*"), is_navigable=True)
        }
    )
    model.add_association(table_columns)
    print("  ✓ Table <-> TableColumn (1:N)")
    
    # Map <-> MapData (1:N, optional)
    map_layers = BinaryAssociation(
        name="map_layers",
        ends={
            Property(name="map", type=map_viz, owner=map_data, multiplicity=Multiplicity(0, 1), is_navigable=False),
            Property(name="layers", type=map_data, owner=map_viz, multiplicity=Multiplicity(0, "*"), is_navigable=True)
        }
    )
    model.add_association(map_layers)
    print("  ✓ Map <-> MapData (1:N)")
    print()
    
    # ========== STEP 7: INHERITANCE (GENERALIZATIONS) ==========
    print("Step 7: Creating Inheritance (Generalizations)...")
    print("-" * 70)
    
    model.add_generalization(Generalization(general=visualization, specific=line_chart))
    print("  ✓ Visualization -> LineChart")
    
    model.add_generalization(Generalization(general=visualization, specific=bar_chart))
    print("  ✓ Visualization -> BarChart")
    
    model.add_generalization(Generalization(general=visualization, specific=pie_chart))
    print("  ✓ Visualization -> PieChart")
    
    model.add_generalization(Generalization(general=visualization, specific=stat_chart))
    print("  ✓ Visualization -> StatChart")
    
    model.add_generalization(Generalization(general=visualization, specific=table))
    print("  ✓ Visualization -> Table")
    
    model.add_generalization(Generalization(general=visualization, specific=map_viz))
    print("  ✓ Visualization -> Map")
    
    model.add_generalization(Generalization(general=map_data, specific=wms))
    print("  ✓ MapData -> WMS")
    
    model.add_generalization(Generalization(general=map_data, specific=geojson))
    print("  ✓ MapData -> GeoJson")
    print()
    
    # ========== SUMMARY ==========
    print("=" * 70)
    print("✅ MODEL CREATION COMPLETE!")
    print("=" * 70)
    
    classes = list(model.types)
    classes = [c for c in classes if hasattr(c, 'attributes')]
    print(f"Classes: {len(classes)}")
    
    enums = [t for t in model.types if hasattr(t, 'literals')]
    print(f"Enumerations: {len(enums)}")
    
    print(f"Associations: {len(list(model.associations))}")
    print(f"Generalizations: {len(list(model.generalizations))}")
    
    total_attrs = sum(len(list(c.attributes)) for c in classes)
    print(f"Total Attributes: {total_attrs}")
    print()
    
    return model


if __name__ == "__main__":
    model = buml_model()
    print("✅ BUML Model created successfully!")
