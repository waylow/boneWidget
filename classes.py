from .props import ImportColorSet


class BoneWidgetImportData:
    """
    Tracks import status for BoneWidgets, including successes, failures, and duplicates.
    """

    def __init__(self):
        self.new_imported_items: int = 0  # Count of new successfully imported items
        self.total_num_imports: int = 0  # Total number of attempted imports
        self.failed_imports: list[Widget | ColorSet] = []
        self.skipped_imports: list[Widget | ColorSet] = []
        self.imported_items: list[Widget | ColorSet] = []
        self.duplicate_imports: list[Widget | ColorSet] = []
        self.import_type: str | None = None  # Type of import operation (None if undefined)
        self.json_import_error: bool = False  # Flag for JSON parsing errors

    def imported(self) -> int:
        """Returns the number of newly imported items or total imported items."""
        return self.new_imported_items or len(self.imported_items)

    def skipped(self) -> int:
        """Returns the number of skipped imports."""
        return len(self.skipped_imports)

    def failed(self) -> int:
        """Returns the number of failed imports."""
        return len(self.failed_imports)

    def total(self) -> int:
        """Returns the total number of attempted imports."""
        return self.total_num_imports

    def reset_imports(self) -> None:
        """Resets import tracking data, clearing skipped, imported, and duplicate items."""
        self.skipped_imports = []
        self.imported_items = {}
        self.duplicate_imports = {}


class Widget:
    def __init__(self, name: str, widget_dict: dict):
        self._name: str = name if name else "Unnamed Widget"
        self._vertices: list[list[float]] = widget_dict.get("vertices", [[]])  # Ensure list structure
        self._edges: list[list[int]] = widget_dict.get("edges", [[]])
        self._faces: list[list[int]] = widget_dict.get("faces", [[]])
        self._image: str = widget_dict.get("image", "") or "user_defined.png"

    @property
    def name(self) -> str:
        """Returns the widget name."""
        return self._name
    
    @name.setter
    def name(self, new_name: str) -> None:
        self._name = new_name

    @property
    def vertices(self) -> list[list[float]]:
        """Returns the list of vertices."""
        return self._vertices

    @property
    def edges(self) -> list[list[int]]:
        """Returns the list of edges."""
        return self._edges

    @property
    def faces(self) -> list[list[int]]:
        """Returns the list of faces."""
        return self._faces

    @property
    def image(self) -> str:
        """Returns the image filename."""
        return self._image

    def __repr__(self):
        return f"Widget({self.name})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Widget):
            return False
        return (
            self.vertices == other.vertices and
            self.edges == other.edges and
            self.faces == other.faces and
            self.image == other.image
        )
    
    def to_dict(self) -> dict[str, dict[str, list | str]]:
        """
        Returns a dictionary with the widget's name as the key,
        and its attributes as the value. Matches the structure of the
        original widgets collection.
        """
        return {
            self.name: {
                "vertices": self.vertices,
                "edges": self.edges,
                "faces": self.faces,
                "image": self.image
            }
        }


class ColorSet:
    def __init__(self, color_dict: dict[str, list[float]]):
        self._name: str = color_dict.get("name", "Unnamed ColorSet")
        self._normal: list[float] = color_dict.get("normal", [])
        self._select: list[float] = color_dict.get("select", [])
        self._active: list[float] = color_dict.get("active", [])

    @property
    def name(self) -> str:
        """Returns the color set name."""
        return self._name
    
    @name.setter
    def name(self, new_name: str) -> None:
        """Sets a new color set name."""
        self._name = new_name

    @property
    def normal(self) -> list[float]:
        """Returns the normal color values."""
        return self._normal

    @property
    def select(self) -> list[float]:
        """Returns the select color values."""
        return self._select

    @property
    def active(self) -> list[float]:
        """Returns the active color values."""
        return self._active

    def __repr__(self) -> str:
        return f"ColorSet({self.name})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ColorSet):
            return False
        return (
            self.normal == other.normal and
            self.select == other.select and
            self.active == other.active
        )
    
    @classmethod
    def from_pg(cls, pg: ImportColorSet) -> "ColorSet":
        """
        Creates a ColorSet instance from a Blender PropertyGroup -> ImportColorSet.

        Args:
            pg (ImportColorSet): The PropertyGroup holding color data.

        Returns:
            ColorSet: A new instance based on the property group.
        """
        return cls({
            "name": pg.name,
            "normal": list(pg.normal),
            "select": list(pg.select),
            "active": list(pg.active)
        })
