"""
scripts package for KWDB data migration.

This package contains all necessary scripts for performing heterogeneous
database migration to KaiwuDB via KDTS REST API.

Modules:
- api_client.py: KDTS REST API client
- data_source.py: Data source configuration management
- migration_task.py: Migration workflow orchestration
- config_validator.py: Configuration validation
- error_handler.py: Error code handling
- config.py: Multi-layer configuration management
"""

from .api_client import KDTSClient, build_source_config, build_table_mapping
from .data_source import (
    DataSourceManager,
    Engine,
    SourceType,
    SourceCapability,
    build_source_config as ds_build_source_config,
    build_target_config as ds_build_target_config,
)
from .migration_task import (
    MigrationWorkflowManager,
    MigrationWorkflow,
    MigrationStep,
    MigrationStatus,
    create_workflow_manager,
)
from .config_validator import ConfigValidator
from .error_handler import ErrorHandler
from .config import (
    KDTSConfig,
    resolve_base_url,
    get_environment_info,
)

__all__ = [
    # api_client
    "KDTSClient",
    "build_source_config",
    "build_table_mapping",
    # data_source
    "DataSourceManager",
    "Engine",
    "SourceType",
    "SourceCapability",
    "ds_build_source_config",
    "ds_build_target_config",
    # migration_task
    "MigrationWorkflowManager",
    "MigrationWorkflow",
    "MigrationStep",
    "MigrationStatus",
    "create_workflow_manager",
    # config_validator
    "ConfigValidator",
    # error_handler
    "ErrorHandler",
    # config
    "KDTSConfig",
    "resolve_base_url",
    "get_environment_info",
]

__version__ = "2.0.0"
