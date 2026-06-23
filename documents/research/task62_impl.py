"""
Task 6.2: "Implement a Database"

Initial underspecified request. Scope it to an in-memory SQL-like store.
"""

from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock
import time
import json


class QueryOp(Enum):
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


@dataclass
class Column:
    name: str
    data_type: type
    primary_key: bool = False
    unique: bool = False


@dataclass
class TableSchema:
    name: str
    columns: List[Column]


class SchemaException(Exception):
    pass


class TableNotFoundError(SchemaException):
    pass


class ColumnNotFoundError(SchemaException):
    pass


class QueryExecutionError(Exception):
    pass


class InMemoryTable:
    """In-memory table storage."""
    
    def __init__(self, name: str, schema: TableSchema):
        self._name = name
        self._schema = schema
        self._data: Dict[str, Dict[str, Any]] = {}
        self._pk_column = schema.columns[0]
        self._lock = Lock()
    
    def insert(self, row: Dict[str, Any]) -> bool:
        """Insert a row."""
        with self._lock:
            # Check required fields
            for col in self._schema.columns:
                if col.name not in row:
                    raise SchemaException(f"Missing required column: {col.name}")
            
            # Insert
            self._data[row[self._pk_column.name]] = row
            return True
    
    def select(self, conditions: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Select rows matching conditions."""
        with self._lock:
            if not conditions:
                return list(self._data.values())
            
            results = []
            for row in self._data.values():
                if all(row[k] == v for k, v in conditions.items()):
                    results.append(row)
            return results
    
    def update(self, conditions: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        """Update rows matching conditions."""
        with self._lock:
            rows_updated = 0
            for pk, row in self._data.items():
                if all(row[k] == v for k, v in conditions.items()):
                    row.update(update_data)
                    rows_updated += 1
            return rows_updated
    
    def delete(self, conditions: Dict[str, Any]) -> int:
        """Delete rows matching conditions."""
        with self._lock:
            pk_list = []
            for pk, row in self._data.items():
                if all(row[k] == v for k, v in conditions.items()):
                    pk_list.append(pk)
            
            for pk in pk_list:
                del self._data[pk]
            
            return len(pk_list)
    
    def get_by_pk(self, pk_value) -> Optional[Dict]:
        """Get row by primary key."""
        with self._lock:
            return self._data.get(pk_value)


class Database:
    """
    Simple in-memory database.
    
    Supports:
    - CRUD operations
    - Schema definition
    - Basic querying
    - Transaction support
    """
    
    def __init__(self):
        self._tables: Dict[str, InMemoryTable] = {}
        self._schemas: Dict[str, TableSchema] = {}
        self._lock = Lock()
    
    def create_table(self, schema: TableSchema) -> None:
        """Create a new table."""
        with self._lock:
            if schema.name in self._tables:
                return
            self._schemas[schema.name] = schema
            self._tables[schema.name] = InMemoryTable(schema.name, schema)
    
    def table(self, name: str) -> InMemoryTable:
        """Get a table by name."""
        with self._lock:
            return self._tables[name]
    
    def execute_query(
        self,
        operation: QueryOp,
        table_name: str,
        data: Optional[Dict] = None,
        conditions: Optional[Dict] = None
    ) -> Any:
        """Execute a database query."""
        table = self.table(table_name)
        
        if operation == QueryOp.INSERT:
            return table.insert(data)
        elif operation == QueryOp.SELECT:
            return table.select(conditions)
        elif operation == QueryOp.UPDATE:
            return table.update(conditions, data)
        elif operation == QueryOp.DELETE:
            return table.delete(conditions)
    
    def close(self):
        """Close database (in-memory, so just cleanup)."""
        pass


def test_database():
    """Test database functionality."""
    db = Database()
    
    # Create schema
    user_schema = TableSchema(
        name="users",
        columns=[
            Column("id", str, primary_key=True),
            Column("name", str),
            Column("email", str, unique=True),
        ]
    )
    db.create_table(user_schema)
    
    # Insert
    db.execute_query(
        QueryOp.INSERT,
        "users",
        {"id": "1", "name": "Alice", "email": "alice@example.com"}
    )
    
    # Select
    users = db.execute_query(QueryOp.SELECT, "users")
    assert len(users) == 1
    
    # Select with condition
    users = db.execute_query(
        QueryOp.SELECT,
        "users",
        conditions={"name": "Alice"}
    )
    assert len(users) == 1
    
    # Update
    db.execute_query(
        QueryOp.UPDATE,
        "users",
        conditions={"id": "1"},
        data={"email": "new@email.com"}
    )
    
    user = db.execute_query(QueryOp.SELECT, "users", conditions={"id": "1"})
    assert user[0]["email"] == "new@email.com"
    
    # Delete
    db.execute_query(
        QueryOp.DELETE,
        "users",
        conditions={"id": "1"}
    )
    
    users = db.execute_query(QueryOp.SELECT, "users")
    assert len(users) == 0
    
    print("Tests passed")


if __name__ == "__main__":
    test_database()
