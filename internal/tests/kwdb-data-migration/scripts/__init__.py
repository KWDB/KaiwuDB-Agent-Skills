"""
Internal Test Scripts Package for kwdb-data-migration.

This directory contains test helper scripts for the kwdb-data-migration skill.

Files:
- mock_server.py: Mock KDTS server for local testing, simulates all API endpoints
- agent_dialogue_simulator.py: Simulates AI Agent dialogue flow
- test_migration_flow.py: End-to-end migration flow test

Usage:
    # Run dialogue simulator
    python agent_dialogue_simulator.py
    
    # Run migration flow test
    python test_migration_flow.py
    
    # Start mock server
    python mock_server.py
"""

__version__ = "1.0.0"
