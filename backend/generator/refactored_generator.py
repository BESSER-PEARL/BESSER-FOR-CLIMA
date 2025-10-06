"""
Generator for creating refactored backend architecture from BUML models.
This generator creates SQLAlchemy models, Pydantic schemas, and FastAPI routers.
"""
import os
from datetime import datetime
from typing import List, Set, Optional
from besser.BUML.metamodel.structural import (
    DomainModel, Class, Property, Multiplicity, 
    Association, Generalization, Enumeration,
    PrimitiveDataType
)
# Import primitive types separately
try:
    from besser.BUML.metamodel.structural import (
        StringType, IntegerType, FloatType, BooleanType, 
        DateTimeType, DateType
    )
except ImportError:
    # Fallback if types are not directly available
    StringType = type(None)
    IntegerType = type(None)
    FloatType = type(None)
    BooleanType = type(None)
    DateTimeType = type(None)
    DateType = type(None)
from jinja2 import Environment, FileSystemLoader


class RefactoredBackendGenerator:
    """Generator for creating a complete refactored backend from BUML models."""
    
    # Type mappings for SQLAlchemy
    SQLALCHEMY_TYPE_MAP = {
        'str': 'String(255)',
        'int': 'Integer',
        'float': 'Float',
        'bool': 'Boolean',
        'datetime': 'DateTime',
        'date': 'Date',
        'dict': 'JSON',
        'list': 'JSON'
    }
    
    # Type mappings for Python/Pydantic
    PYTHON_TYPE_MAP = {
        'str': 'str',
        'int': 'int',
        'float': 'float',
        'bool': 'bool',
        'datetime': 'datetime',
        'date': 'date',
        'dict': 'Dict[str, Any]',
        'list': 'List[Any]'
    }
    
    def __init__(self, model: DomainModel, output_dir: str):
        """
        Initialize the generator.
        
        Args:
            model: The BUML DomainModel to generate from
            output_dir: Directory where files will be generated
        """
        self.model = model
        self.output_dir = output_dir
        self.env = Environment(
            loader=FileSystemLoader('generator/templates'),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Register custom filters and functions
        self._register_filters()
    
    def _register_filters(self):
        """Register custom Jinja2 filters and functions."""
        # Register as globals (accessible in templates without filter syntax)
        self.env.globals['get_python_type'] = self.get_python_type
        self.env.globals['get_sqlalchemy_type'] = self.get_sqlalchemy_type
        self.env.globals['get_pydantic_type'] = self.get_pydantic_type
        self.env.globals['has_timestamps'] = self.has_timestamps
        self.env.globals['is_polymorphic_base'] = self.is_polymorphic_base
        self.env.globals['has_polymorphic_parent'] = self.has_polymorphic_parent
        self.env.globals['get_association_ends'] = self.get_association_ends
        self.env.globals['get_foreign_key_associations'] = self.get_foreign_key_associations
        self.env.globals['get_navigable_associations'] = self.get_navigable_associations
        self.env.globals['get_back_populates'] = self.get_back_populates
        self.env.globals['is_unique'] = self.is_unique
        self.env.globals['should_index'] = self.should_index
        self.env.globals['has_order_attribute'] = self.has_order_attribute
        self.env.globals['get_table_constraints'] = self.get_table_constraints
        self.env.globals['get_repr_fields'] = self.get_repr_fields
        self.env.globals['is_timestamp_field'] = self.is_timestamp_field
        self.env.globals['get_table_name'] = self.get_table_name
        self.env.globals['uses_joined_inheritance'] = self.uses_joined_inheritance
        self.env.globals['get_string_length'] = self.get_string_length
    
    def get_python_type(self, type_obj, optional: bool = False) -> str:
        """Get Python type string for a BUML type."""
        if isinstance(type_obj, Class):
            type_str = type_obj.name
        elif isinstance(type_obj, Enumeration):
            type_str = type_obj.name
        elif hasattr(type_obj, '__class__') and type_obj.__class__.__name__ == 'StringType':
            type_str = 'str'
        elif hasattr(type_obj, '__class__') and type_obj.__class__.__name__ == 'IntegerType':
            type_str = 'int'
        elif hasattr(type_obj, '__class__') and type_obj.__class__.__name__ == 'FloatType':
            type_str = 'float'
        elif hasattr(type_obj, '__class__') and type_obj.__class__.__name__ == 'BooleanType':
            type_str = 'bool'
        elif hasattr(type_obj, '__class__') and type_obj.__class__.__name__ == 'DateTimeType':
            type_str = 'datetime'
        elif hasattr(type_obj, '__class__') and type_obj.__class__.__name__ == 'DateType':
            type_str = 'date'
        elif hasattr(type_obj, 'name'):
            type_str = self.PYTHON_TYPE_MAP.get(type_obj.name, 'Any')
        else:
            type_str = 'Any'
        
        return type_str
    
    def get_sqlalchemy_type(self, type_obj) -> str:
        """Get SQLAlchemy column type for a BUML type."""
        if hasattr(type_obj, 'name'):
            return self.SQLALCHEMY_TYPE_MAP.get(type_obj.name, 'String(255)')
        return 'String(255)'
    
    def get_pydantic_type(self, type_obj) -> str:
        """Get Pydantic type string for a BUML type."""
        if isinstance(type_obj, Class):
            return type_obj.name
        elif isinstance(type_obj, Enumeration):
            return type_obj.name
        elif hasattr(type_obj, 'name'):
            return self.PYTHON_TYPE_MAP.get(type_obj.name, 'Any')
        return 'Any'
    
    def has_timestamps(self, class_obj: Class) -> bool:
        """Check if a class should have timestamp fields."""
        # Classes with these names typically have timestamps
        timestamp_classes = {'City', 'Dashboard', 'KPI', 'Visualization', 'MapData', 'DashboardSection'}
        return class_obj.name in timestamp_classes or any(
            attr.name in ['created_at', 'updated_at'] for attr in class_obj.attributes
        )
    
    def is_polymorphic_base(self, class_obj: Class) -> bool:
        """Check if a class is a polymorphic base (has subclasses)."""
        return len(class_obj.specializations()) > 0
    
    def has_polymorphic_parent(self, class_obj: Class) -> bool:
        """Check if a class has a polymorphic parent."""
        return len(class_obj.parents()) > 0
    
    def get_association_ends(self, class_obj: Class) -> List[Property]:
        """Get all association ends for a class."""
        return list(class_obj.association_ends())
    
    def get_foreign_key_associations(self, class_obj: Class) -> List[Property]:
        """Get association ends that represent foreign keys (many-to-one)."""
        fk_ends = []
        for end in class_obj.association_ends():
            # It's a FK if it points to another class and is navigable
            if end.multiplicity.max == 1 and end.is_navigable:
                opposite = end.opposite_end()
                if opposite and opposite.multiplicity.max > 1:
                    fk_ends.append(end)
        return fk_ends
    
    def get_navigable_associations(self, class_obj: Class) -> List[Property]:
        """Get all navigable association ends for a class."""
        return [end for end in class_obj.association_ends() if end.is_navigable]
    
    def get_back_populates(self, property_obj: Property) -> Optional[str]:
        """Get the back_populates name for a relationship."""
        opposite = property_obj.opposite_end()
        return opposite.name if opposite and opposite.is_navigable else None
    
    def is_unique(self, property_obj: Property) -> bool:
        """Check if a property should be unique."""
        # Check metadata first
        if hasattr(property_obj, 'metadata') and property_obj.metadata and 'unique' in property_obj.metadata:
            return property_obj.metadata['unique']
        
        # Properties like 'code', 'name' on root entities are often unique
        return property_obj.name in ['code', 'id_kpi'] or (
            property_obj.name == 'name' and not property_obj.owner.parents()
        )
    
    def should_index(self, property_obj: Property) -> bool:
        """Check if a property should be indexed."""
        # Check metadata first
        if hasattr(property_obj, 'metadata') and property_obj.metadata and 'index' in property_obj.metadata:
            return property_obj.metadata['index']
        
        # Common fields to index
        indexed_fields = {'name', 'code', 'category', 'timestamp', 'id_kpi'}
        return property_obj.name in indexed_fields
    
    def has_order_attribute(self, class_obj: Class) -> bool:
        """Check if a class has an 'order' attribute."""
        return any(attr.name == 'order' for attr in class_obj.attributes)
    
    def get_table_constraints(self, class_obj: Class) -> List[str]:
        """Get table-level constraints for a class."""
        constraints = []
        
        # Check for composite unique constraints
        if class_obj.name == 'Dashboard':
            constraints.append(
                'UniqueConstraint("code", "city_id", name="unique_dashboard_code_per_city")'
            )
            constraints.append(
                'Index("idx_dashboard_city_code", "city_id", "code")'
            )
        elif class_obj.name == 'DashboardSection':
            constraints.append(
                'UniqueConstraint("name", "dashboard_id", name="unique_section_name_per_dashboard")'
            )
            constraints.append(
                'Index("idx_section_dashboard_order", "dashboard_id", "order")'
            )
        elif class_obj.name == 'KPI':
            constraints.append('Index("idx_kpi_city_category", "city_id", "category")')
            constraints.append('Index("idx_kpi_active", "is_active")')
        elif class_obj.name == 'KPIValue':
            constraints.append('Index("idx_kpivalue_kpi_timestamp", "kpi_id", "timestamp")')
            constraints.append('Index("idx_kpivalue_timestamp_desc", "timestamp", postgresql_using="btree")')
        elif class_obj.name == 'Visualization':
            constraints.append('Index("idx_visualization_dashboard", "dashboard_id")')
            constraints.append('Index("idx_visualization_section", "section_id")')
            constraints.append('Index("idx_visualization_type", "type")')
        
        return constraints
    
    def get_repr_fields(self, class_obj: Class) -> str:
        """Get fields to include in __repr__ method."""
        fields = []
        for attr in class_obj.attributes:
            if attr.name in ['name', 'code', 'title']:
                fields.append(f"{attr.name}='{{self.{attr.name}}}'")
        return ', '.join(fields)
    
    def is_timestamp_field(self, field_name: str) -> bool:
        """Check if a field is a timestamp field."""
        return field_name in ['created_at', 'updated_at']
    
    def get_table_name(self, class_obj: Class) -> str:
        """
        Get the table name for a class.
        Checks metadata first, then uses simple pluralization.
        """
        # Check if table name is specified in metadata
        if hasattr(class_obj, 'metadata') and class_obj.metadata and 'table_name' in class_obj.metadata:
            return class_obj.metadata['table_name']
        
        # Simple pluralization fallback
        name = class_obj.name.lower()
        
        # Handle common irregular plurals
        if name.endswith('y'):
            return name[:-1] + 'ies'
        elif name.endswith('s'):
            return name + 'es'
        else:
            return name + 's'
    
    def uses_joined_inheritance(self, class_obj: Class) -> bool:
        """
        Check if a class uses joined table inheritance.
        Returns True if metadata specifies joined inheritance.
        """
        if hasattr(class_obj, 'metadata') and class_obj.metadata:
            return class_obj.metadata.get('polymorphic') == 'joined'
        return False
    
    def get_string_length(self, prop: Property) -> int:
        """
        Get the appropriate string length for a property.
        Uses metadata if available, otherwise applies sensible defaults.
        """
        # Check metadata first
        if hasattr(prop, 'metadata') and prop.metadata and 'length' in prop.metadata:
            return prop.metadata['length']
        
        # Apply sensible defaults based on field name
        field_name = prop.name.lower()
        
        if field_name in ['code', 'id_kpi']:
            return 20
        elif field_name in ['name', 'title']:
            return 100
        elif field_name in ['email', 'url', 'wms_url']:
            return 255
        elif field_name in ['description', 'notes']:
            return 500
        elif field_name in ['config', 'layout_config', 'style_config', 'geojson_data', 'formula']:
            return 2000
        else:
            return 255  # Default
    
    def _create_directory_structure(self, base_dir: str):
        """Create the complete directory structure for the app."""
        directories = [
            base_dir,
            os.path.join(base_dir, 'core'),
            os.path.join(base_dir, 'models'),
            os.path.join(base_dir, 'schemas'),
            os.path.join(base_dir, 'repositories'),
            os.path.join(base_dir, 'services'),
            os.path.join(base_dir, 'api'),
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def generate(self):
        """Generate complete backend application structure."""
        print("🚀 Starting complete backend generation...")
        
        # Create app directory structure
        app_dir = os.path.join(self.output_dir, 'app')
        self._create_directory_structure(app_dir)
        
        # Get sorted classes and enumerations
        classes = self.model.classes_sorted_by_inheritance()
        enumerations = list(self.model.get_enumerations())
        
        context = {
            'classes': classes,
            'enumerations': enumerations,
            'model': self.model,
            'timestamp': datetime.now().isoformat()
        }
        
        # Generate core files
        print("\n📦 Generating core infrastructure...")
        self._generate_file('core/__init__.py.j2', os.path.join(app_dir, 'core', '__init__.py'), context)
        self._generate_file('core/config.py.j2', os.path.join(app_dir, 'core', 'config.py'), context)
        self._generate_file('core/database.py.j2', os.path.join(app_dir, 'core', 'database.py'), context)
        
        # Generate models
        print("📦 Generating SQLAlchemy models...")
        self._generate_file('models/__init__.py.j2', os.path.join(app_dir, 'models', '__init__.py'), context)
        
        # Generate schemas
        print("📋 Generating Pydantic schemas...")
        self._generate_file('schemas/__init__.py.j2', os.path.join(app_dir, 'schemas', '__init__.py'), context)
        
        # Generate repositories
        print("🗄️  Generating repositories...")
        self._generate_file('repositories/__init__.py.j2', os.path.join(app_dir, 'repositories', '__init__.py'), context)
        self._generate_file('repositories/base.py.j2', os.path.join(app_dir, 'repositories', 'base.py'), context)
        
        # Generate services
        print("⚙️  Generating services...")
        self._generate_file('services/__init__.py.j2', os.path.join(app_dir, 'services', '__init__.py'), context)
        self._generate_file('services/auth.py.j2', os.path.join(app_dir, 'services', 'auth.py'), context)
        
        # Generate API routers
        print("🛣️  Generating API routers...")
        self._generate_file('api/__init__.py.j2', os.path.join(app_dir, 'api', '__init__.py'), context)
        self._generate_file('api/auth.py.j2', os.path.join(app_dir, 'api', 'auth.py'), context)
        
        # Generate individual entity routers
        for cls in classes:
            if not self.has_polymorphic_parent(cls):  # Only generate for base classes
                entity_name = cls.name.lower()
                self._generate_file(
                    'api/entity_router.py.j2',
                    os.path.join(app_dir, 'api', f'{entity_name}s.py'),
                    {**context, 'entity': cls}
                )
        
        # Generate main application
        print("🚀 Generating main application...")
        self._generate_file('main.py.j2', os.path.join(app_dir, 'main.py'), context)
        self._generate_file('__init__.py.j2', os.path.join(app_dir, '__init__.py'), context)
        
        print(f"\n✅ Generation complete! App created in: {app_dir}")
        print(f"   - Generated {len(classes)} model classes")
        print(f"   - Generated {len(enumerations)} enumerations")
        print(f"   - Generated {len([c for c in classes if not self.has_polymorphic_parent(c)])} API routers")
        print(f"   - Complete app structure with core, models, schemas, repositories, services, and API")
    
    def _generate_file(self, template_name: str, output_filename: str, context: dict):
        """Generate a single file from a template."""
        try:
            template = self.env.get_template(template_name)
            rendered = template.render(**context)
            
            # output_filename is already the full path, don't add output_dir again
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(rendered)
            
            # Print relative path for readability
            rel_path = os.path.relpath(output_filename, self.output_dir)
            print(f"   ✓ Created {rel_path}")
        except Exception as e:
            rel_path = os.path.relpath(output_filename, self.output_dir)
            print(f"   ✗ Error generating {rel_path}: {str(e)}")
            raise


def generate_refactored_backend(model: DomainModel, output_dir: str = "refactored/generated"):
    """
    Convenience function to generate refactored backend.
    
    Args:
        model: The BUML DomainModel
        output_dir: Output directory for generated files
    """
    generator = RefactoredBackendGenerator(model, output_dir)
    generator.generate()
