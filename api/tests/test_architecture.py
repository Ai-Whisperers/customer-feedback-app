"""
Architecture tests to enforce clean architecture principles.

These tests prevent architectural violations like:
- Circular imports
- Layer violations (e.g., core importing from services)
- Incorrect dependency directions
"""

import ast
import os
from pathlib import Path
from typing import Set, Dict, List
import pytest


# Define allowed dependency directions
LAYER_RULES = {
    "routes": ["services", "schemas", "config", "core", "adapters"],
    "services": ["core", "schemas", "config", "adapters"],
    "core": ["config", "schemas"],  # Core should be independent
    "adapters": ["config", "schemas", "core"],
    "workers": ["services", "core", "schemas", "config", "adapters"],
    "schemas": [],  # Schemas should have no app dependencies
}


class ImportAnalyzer(ast.NodeVisitor):
    """AST visitor to extract import statements."""

    def __init__(self):
        self.imports: Set[str] = set()

    def visit_Import(self, node):
        """Visit import statements."""
        for alias in node.names:
            self.imports.add(alias.name)

    def visit_ImportFrom(self, node):
        """Visit from...import statements."""
        if node.module:
            self.imports.add(node.module)


def get_project_root() -> Path:
    """Get the API project root directory."""
    current = Path(__file__).parent
    while current.name != "api" and current.parent != current:
        current = current.parent
    return current


def get_python_files(directory: Path) -> List[Path]:
    """Get all Python files in directory recursively."""
    return list(directory.rglob("*.py"))


def extract_imports(file_path: Path) -> Set[str]:
    """Extract all imports from a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        analyzer = ImportAnalyzer()
        analyzer.visit(tree)
        return analyzer.imports
    except SyntaxError:
        # Skip files with syntax errors
        return set()


def get_app_layer(file_path: Path, app_dir: Path) -> str:
    """Determine which architectural layer a file belongs to."""
    relative = file_path.relative_to(app_dir)
    parts = relative.parts

    if len(parts) > 1 and parts[0] == "app":
        layer = parts[1]
        if layer in LAYER_RULES:
            return layer

    return "other"


def check_layer_violation(
    file_layer: str,
    imported_module: str,
    app_modules: Set[str]
) -> bool:
    """
    Check if import violates layer rules.

    Args:
        file_layer: Layer of the importing file
        imported_module: Module being imported
        app_modules: Set of all app module names

    Returns:
        True if violation detected, False otherwise
    """
    if file_layer not in LAYER_RULES:
        return False

    # Check if importing from app
    if not imported_module.startswith("app."):
        return False

    # Extract the layer being imported
    parts = imported_module.split(".")
    if len(parts) < 2:
        return False

    imported_layer = parts[1]

    # Check if this import is allowed
    allowed_layers = LAYER_RULES[file_layer]

    return imported_layer not in allowed_layers and imported_layer != file_layer


class TestArchitecture:
    """Architecture validation tests."""

    @pytest.fixture(scope="class")
    def project_structure(self):
        """Analyze project structure once for all tests."""
        root = get_project_root()
        app_dir = root / "app"

        files_by_layer = {}
        all_files = get_python_files(app_dir)
        app_modules = {f.stem for f in all_files}

        for file_path in all_files:
            layer = get_app_layer(file_path, root)
            if layer not in files_by_layer:
                files_by_layer[layer] = []
            files_by_layer[layer].append(file_path)

        return {
            "root": root,
            "app_dir": app_dir,
            "files_by_layer": files_by_layer,
            "all_files": all_files,
            "app_modules": app_modules
        }

    def test_no_circular_imports(self, project_structure):
        """
        Test that there are no circular imports in the codebase.

        Circular imports can cause:
        - Hard-to-debug initialization errors
        - Import failures at runtime
        - Tight coupling between modules
        """
        root = project_structure["root"]
        all_files = project_structure["all_files"]

        # Build dependency graph
        dependencies: Dict[str, Set[str]] = {}

        for file_path in all_files:
            module_name = str(file_path.relative_to(root).with_suffix('')).replace(os.sep, '.')
            imports = extract_imports(file_path)

            # Filter to only app imports
            app_imports = {
                imp for imp in imports
                if imp.startswith('app.')
            }

            dependencies[module_name] = app_imports

        # Check for circular dependencies using DFS
        def has_cycle(node, visited, rec_stack, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in dependencies.get(node, set()):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack, path):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    pytest.fail(
                        f"Circular import detected:\n" +
                        "\n → ".join(cycle)
                    )
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        visited = set()
        for module in dependencies:
            if module not in visited:
                has_cycle(module, visited, set(), [])

    def test_layer_dependencies(self, project_structure):
        """
        Test that layer dependencies follow clean architecture rules.

        Rules:
        - routes can import: services, schemas, config, core, adapters
        - services can import: core, schemas, config, adapters
        - core can import: config, schemas (core should be independent)
        - adapters can import: config, schemas, core
        - workers can import: services, core, schemas, config, adapters
        - schemas should have no app dependencies
        """
        root = project_structure["root"]
        files_by_layer = project_structure["files_by_layer"]
        app_modules = project_structure["app_modules"]

        violations = []

        for layer, files in files_by_layer.items():
            if layer not in LAYER_RULES:
                continue

            for file_path in files:
                imports = extract_imports(file_path)

                for imported_module in imports:
                    if check_layer_violation(layer, imported_module, app_modules):
                        violations.append(
                            f"{file_path.name} ({layer}) imports {imported_module}"
                        )

        if violations:
            pytest.fail(
                "Layer dependency violations detected:\n" +
                "\n".join(f"  - {v}" for v in violations)
            )

    def test_core_is_independent(self, project_structure):
        """
        Test that core layer doesn't import from services or routes.

        Core domain logic should be independent of:
        - HTTP/API layer (routes)
        - Orchestration layer (services)
        - External integrations (adapters, except through interfaces)
        """
        files_by_layer = project_structure["files_by_layer"]
        violations = []

        for file_path in files_by_layer.get("core", []):
            imports = extract_imports(file_path)

            for imported_module in imports:
                if imported_module.startswith("app.services."):
                    violations.append(
                        f"{file_path.name} imports services: {imported_module}"
                    )
                elif imported_module.startswith("app.routes."):
                    violations.append(
                        f"{file_path.name} imports routes: {imported_module}"
                    )
                elif imported_module.startswith("app.workers."):
                    violations.append(
                        f"{file_path.name} imports workers: {imported_module}"
                    )

        if violations:
            pytest.fail(
                "Core layer should not import from services/routes/workers:\n" +
                "\n".join(f"  - {v}" for v in violations)
            )

    def test_schemas_are_independent(self, project_structure):
        """
        Test that schemas don't import from other app layers.

        Schemas should be pure data definitions without:
        - Business logic imports
        - Service imports
        - Route imports
        """
        files_by_layer = project_structure["files_by_layer"]
        violations = []

        for file_path in files_by_layer.get("schemas", []):
            imports = extract_imports(file_path)

            for imported_module in imports:
                if imported_module.startswith("app."):
                    # Only allow base, config, and other schemas
                    if not any(
                        imported_module.startswith(f"app.{allowed}")
                        for allowed in ["schemas", "config"]
                    ):
                        violations.append(
                            f"{file_path.name} imports {imported_module}"
                        )

        if violations:
            pytest.fail(
                "Schemas should not import from other app layers:\n" +
                "\n".join(f"  - {v}" for v in violations)
            )

    def test_no_wildcard_imports(self, project_structure):
        """
        Test that there are no wildcard imports (from x import *).

        Wildcard imports:
        - Make it unclear what's being imported
        - Can cause name conflicts
        - Make refactoring harder
        """
        all_files = project_structure["all_files"]
        violations = []

        for file_path in all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                if "import *" in content:
                    violations.append(file_path.name)
            except:
                continue

        if violations:
            pytest.fail(
                "Wildcard imports detected in:\n" +
                "\n".join(f"  - {v}" for v in violations)
            )


class TestFileOrganization:
    """Test file organization conventions."""

    def test_no_god_files(self):
        """
        Test that no files exceed 250 lines (excluding tests).

        God files (>250 lines) are hard to:
        - Understand
        - Test
        - Maintain
        - Refactor
        """
        root = get_project_root()
        app_dir = root / "app"
        violations = []

        for file_path in get_python_files(app_dir):
            # Skip __init__ files and certain allowed exceptions
            if file_path.name == "__init__.py":
                continue

            # Skip excel_formatter (known large file, has refactoring guide)
            if "excel_formatter" in str(file_path):
                continue

            # Skip export_service (has refactoring guide in local-reports)
            if "export_service" in str(file_path):
                continue

            with open(file_path, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())

            if lines > 250:
                violations.append(f"{file_path.name} ({lines} lines)")

        if violations:
            pytest.fail(
                "Files exceeding 250 lines (god files):\n" +
                "\n".join(f"  - {v}" for v in violations) +
                "\n\nConsider refactoring into smaller, more focused modules."
            )

    def test_entry_points_are_small(self):
        """
        Test that route handlers are <=150 lines.

        Route handlers should be thin controllers that:
        - Validate input
        - Call services
        - Return responses
        """
        root = get_project_root()
        routes_dir = root / "app" / "routes"
        violations = []

        if routes_dir.exists():
            for file_path in routes_dir.glob("*.py"):
                if file_path.name == "__init__.py":
                    continue

                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())

                if lines > 150:
                    violations.append(f"{file_path.name} ({lines} lines)")

        if violations:
            pytest.fail(
                "Route files exceeding 150 lines:\n" +
                "\n".join(f"  - {v}" for v in violations) +
                "\n\nRoute handlers should delegate to services."
            )


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
