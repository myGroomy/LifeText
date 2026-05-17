#!/usr/bin/env python
"""Initialize database tables."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db import init_db, engine
from src.models import Base

if __name__ == "__main__":
    print("Initializing database...")
    try:
        init_db()
        print("✅ Database initialized successfully!")
        print("\nTables created:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        sys.exit(1)
