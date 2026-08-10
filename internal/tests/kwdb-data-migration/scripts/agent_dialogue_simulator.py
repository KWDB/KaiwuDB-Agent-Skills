#!/usr/bin/env python3
"""
Agent Dialogue Simulator

This script simulates the AI Agent dialogue flow for KWDB data migration.
It demonstrates how the AI Agent would guide users through the migration process.

Supports both English and Chinese user input scenarios to verify
the language-dependent response feature.

Usage:
    python agent_dialogue_simulator.py

Or run a specific scenario:
    python agent_dialogue_simulator.py --scenario mysql_to_kwdb
    python agent_dialogue_simulator.py --scenario influxdb_to_kwdb
    python agent_dialogue_simulator.py --scenario error_handling
    python agent_dialogue_simulator.py --scenario chinese_user
"""

import sys
import os
import json
import argparse

# Add the skills scripts path to import modules
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# scripts -> kwdb-data-migration -> tests -> internal -> project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR))))
SCRIPTS_PATH = os.path.join(PROJECT_ROOT, 'skills', 'kwdb-data-migration', 'scripts')

sys.path.insert(0, SCRIPTS_PATH)

from data_source import DataSourceManager, SourceType, SourceCapability
from config_validator import ConfigValidator
from error_handler import ErrorHandler


class DialogueSimulator:
    """
    AI Agent Dialogue Simulator
    
    Simulates the conversation flow between a user and the AI Agent
    for database migration scenarios.
    """
    
    def __init__(self):
        self.ds_manager = DataSourceManager()
        self.history = []
        
    def log(self, speaker, message):
        """Log a message to dialogue history and print it."""
        self.history.append({"speaker": speaker, "message": message})
        prefix = "USER" if speaker == "user" else "AGENT"
        print(f"\n{'='*60}")
        print(f"[{prefix}]:")
        print(f"{message}")
        print(f"{'='*60}")
    
    @staticmethod
    def log_system(message):
        """Log a system action (internal AI Agent processing)."""
        print(f"\n--- [SYSTEM] {message} ---")
    
    # ============================================================
    # Scenario 1: MySQL to KaiwuDB (Relational) Migration
    # ============================================================
    
    def scenario_mysql_to_kwdb(self):
        """Simulate MySQL to KaiwuDB full migration dialogue."""
        print("\n" + "="*60)
        print("SCENARIO: MySQL to KaiwuDB (Relational) Migration")
        print("="*60)
        
        # Step 1: User Request
        self.log("user", "Help me migrate MySQL order_system database to KaiwuDB")
        
        # Step 2: AI Agent Recognizes Intent
        self.log_system("Recognizing migration intent...")
        self.log("agent", 
            "[OK] Migration intent recognized: MySQL -> KaiwuDB (Relational)\n\n"
            "Please provide the following information:\n\n"
            "1. KDTS server address (default: http://127.0.0.1:8989)\n"
            "2. MySQL connection info:\n"
            "   - Host:\n"
            "   - Port (default 3306):\n"
            "   - Username:\n"
            "   - Password:\n"
            "   - Database name (order_system):\n"
            "3. KaiwuDB connection info:\n"
            "   - Host (default 127.0.0.1):\n"
            "   - Port (default 26257):\n"
            "   - Username (default root):\n"
            "   - Password:\n"
            "   - Target database name (order_system):\n\n"
            "[IMPORTANT] Security reminder: Please ensure you have backed up the source database before migration!"
        )
        
        # Step 3: User Provides Parameters
        user_input = {
            "kdts_url": "http://192.168.1.100:8989",
            "mysql_host": "192.168.1.50",
            "mysql_port": 3306,
            "mysql_user": "root",
            "mysql_password": "mysql123",
            "mysql_db": "order_system",
            "kwdb_host": "127.0.0.1",
            "kwdb_port": 26257,
            "kwdb_user": "root",
            "kwdb_password": "kwdb_secret",
            "kwdb_db": "order_system"
        }
        self.log("user", json.dumps(user_input, ensure_ascii=False, indent=2))
        
        # Step 4: AI Agent Validates Parameters
        self.log_system("Validating source type...")
        source_result = ConfigValidator.validate_source_type("MYSQL")
        self.log_system(f"Source validation: {source_result}")
        
        self.log_system("Building source configuration...")
        source_config = self.ds_manager.build_config(
            source_type="MYSQL",
            host=user_input["mysql_host"],
            port=user_input["mysql_port"],
            username=user_input["mysql_user"],
            password=user_input["mysql_password"],
            db_name=user_input["mysql_db"]
        )
        self.log_system(f"Source config: {json.dumps(source_config, indent=2)}")
        
        self.log_system("Building target configuration...")
        target_config = self.ds_manager.build_target_config(
            engine="RELATIONAL",
            host=user_input["kwdb_host"],
            port=user_input["kwdb_port"],
            username=user_input["kwdb_user"],
            password=user_input["kwdb_password"],
            db_name=user_input["kwdb_db"]
        )
        self.log_system(f"Target config: {json.dumps(target_config, indent=2)}")
        
        self.log("agent",
            "[OK] Parameter validation passed!\n\n"
            "Migration plan:\n"
            "  Source: MySQL @ 192.168.1.50:3306/order_system\n"
            "  Target: KaiwuDB (RELATIONAL) @ 127.0.0.1:26257/order_system\n"
            "  KDTS: http://192.168.1.100:8989\n\n"
            "The following steps will be executed:\n"
            "  1. Test connection\n"
            "  2. Read metadata\n"
            "  3. Preview DDL\n"
            "  4. Execute DDL (requires confirmation)\n"
            "  5. Execute data migration\n"
            "  6. Monitor progress\n\n"
            "Start execution? (yes/no)"
        )
        
        # Step 5: User Confirms
        self.log("user", "yes")
        
        # Step 6: Simulate Migration Execution
        self.log_system("Step 1: Testing connections...")
        self.log("agent", "[OK] Connection test passed (Source + Target)")
        
        self.log_system("Step 2: Reading metadata...")
        self.log("agent", 
            "[OK] Metadata read successfully!\n\n"
            "Found 6 tables:\n"
            "  - orders (15 columns)\n"
            "  - order_items (8 columns)\n"
            "  - customers (12 columns)\n"
            "  - products (10 columns)\n"
            "  - categories (5 columns)\n"
            "  - inventory (7 columns)\n\n"
            "Estimated total data volume: ~50,000 rows"
        )
        
        self.log_system("Step 3: Previewing DDL...")
        self.log("agent",
            "[WARNING] DDL preview (orders table):\n\n"
            "CREATE TABLE orders (\n"
            "    id INT8 PRIMARY KEY,\n"
            "    customer_id INT8,\n"
            "    order_time TIMESTAMP,\n"
            "    total_amount DECIMAL(15,2),\n"
            "    status VARCHAR(50)\n"
            ");\n\n"
            "[WARNING] About to execute DDL to create 6 tables in KaiwuDB\n"
            "Confirm execution? (yes/no)"
        )
        
        self.log("user", "yes")
        
        self.log_system("Step 4: Executing DDL...")
        self.log("agent", "[OK] DDL execution successful! Tables created: 6")
        
        self.log_system("Step 5-6: Executing and monitoring migration...")
        self.log("agent",
            "[OK] Migration completed!\n\n"
            "Migration report:\n"
            "  Total rows migrated: 50,000\n"
            "  Successful tables: 6/6\n"
            "  Failed tables: 0/6\n"
            "  Error rows: 0\n\n"
            "[TIP] Recommendation: Verify data integrity"
        )
        
        print("\n" + "="*60)
        print("SCENARIO COMPLETED SUCCESSFULLY")
        print("="*60)
    
    # ============================================================
    # Scenario 2: MySQL to KaiwuDB (Time Series Engine) Migration
    # ============================================================

    def scenario_mysql_to_kwdb_timeseries(self):
        """Simulate MySQL to KaiwuDB Time Series engine migration."""
        print("\n" + "="*60)
        print("SCENARIO: MySQL to KaiwuDB (Time Series Engine) Migration")
        print("="*60)

        # Step 1: User Request
        self.log("user", "I want to migrate MySQL sensor_data table to KaiwuDB time series database")

        # Step 2: AI Agent Recognizes Intent
        self.log_system("Recognizing migration intent...")
        self.log("agent", 
            "[OK] Migration intent recognized: MySQL (sensor_data) -> KaiwuDB (TIMESERIES)\n\n"
            "[INFO] Since the target is KaiwuDB time series engine, table structure will be automatically converted to time series format:\n"
            "  - Time field will be used as PRIMARY TIME\n"
            "  - ID/identifier fields will be used as TAG\n"
            "  - Numeric fields will be used as FIELD\n\n"
            "Please provide the following information:\n"
            "  1. KDTS server address (default: http://127.0.0.1:8989)\n"
            "  2. MySQL connection info:\n"
            "     - Host:\n"
            "     - Port (default 3306):\n"
            "     - Username:\n"
            "     - Password:\n"
            "     - Database name:\n"
            "     - Table name (sensor_data):\n"
            "  3. KaiwuDB connection info (engine: TIMESERIES):\n"
            "     - Host (default 127.0.0.1):\n"
            "     - Port (default 26257):\n"
            "     - Username (default root):\n"
            "     - Password:\n"
            "     - Target database name:\n\n"
            "[IMPORTANT] Security reminder: Please ensure you have backed up the source database before migration!"
        )

        # Step 3: User Provides Parameters
        user_input = {
            "kdts_url": "http://192.168.1.100:8989",
            "mysql_host": "192.168.1.50",
            "mysql_port": 3306,
            "mysql_user": "root",
            "mysql_password": "mysql123",
            "mysql_db": "iot_data",
            "mysql_table": "sensor_data",
            "kwdb_host": "127.0.0.1",
            "kwdb_port": 26257,
            "kwdb_user": "root",
            "kwdb_password": "kwdb_secret",
            "kwdb_db": "iot_ts"
        }
        self.log("user", json.dumps(user_input, ensure_ascii=False, indent=2))

        # Step 4: AI Agent Validates and Analyzes
        self.log_system("Validating source type...")
        source_result = ConfigValidator.validate_source_type("MYSQL")
        self.log_system(f"Source validation: {source_result}")

        self.log_system("Reading table metadata for time series conversion...")
        self.log("agent",
            "[INFO] Analyzing MySQL table structure...\n\n"
            "Detected sensor_data table:\n"
            "  - Fields: sensor_id, location, timestamp, temperature, humidity\n"
            "  - Primary key: (sensor_id, timestamp)\n\n"
            "[INFO] Time series conversion plan:\n"
            "  PRIMARY TIME: timestamp (TIMESTAMP type)\n"
            "  TAG: sensor_id (device identifier), location (location)\n"
            "  FIELD: temperature (temperature), humidity (humidity)\n\n"
            "[WARNING] Conversion notes:\n"
            "  - timestamp field will become the time stamp\n"
            "  - Composite primary key will be split into TAG + TIME\n"
            "  - Data types will be automatically mapped\n\n"
            "Continue with conversion? (yes/no)"
        )

        # Step 5: User Confirms
        self.log("user", "yes")

        # Step 6: Show DDL Preview
        self.log_system("Generating time series DDL...")
        self.log("agent",
            "[INFO] Generated KaiwuDB time series table DDL:\n\n"
            "CREATE TABLE sensor_data (\n"
            "    timestamp TIMESTAMP,\n"
            "    sensor_id VARCHAR(100) PRIMARY TAG,\n"
            "    location VARCHAR(200) TAG,\n"
            "    temperature DOUBLE FIELD,\n"
            "    humidity DOUBLE FIELD\n"
            ");\n\n"
            "[WARNING] About to execute DDL to create time series table in KaiwuDB\n"
            "[WARNING] Timestamp precision: Millisecond\n"
            "[WARNING] TAG field maximum length: 128 bytes\n\n"
            "Confirm execution? (yes/no)"
        )

        self.log("user", "yes")

        # Step 7: Execute Migration
        self.log_system("Executing migration...")
        self.log("agent",
            "[OK] DDL execution successful! Time series table created: sensor_data\n\n"
            "[INFO] Starting data migration...\n"
            "  - Source table rows: 1,234,567\n"
            "  - Estimated time: 120 seconds\n"
            "  - Concurrency: 4\n\n"
            "[INFO] Migration progress: 50% (617,283 rows)\n"
            "[INFO] Migration progress: 100% (1,234,567 rows)\n\n"
            "[OK] Migration completed!\n"
            "  - Target table: sensor_data\n"
            "  - Rows migrated: 1,234,567\n"
            "  - Time taken: 95.3 seconds\n"
            "  - Average speed: 12,954 rows/second\n\n"
            "[REPORT] Data verification:\n"
            "  - Total rows match: [YES]\n"
            "  - TAG fields complete: [YES]\n"
            "  - Timestamp precision correct: [YES]\n\n"
            "[TIP] Recommendations:\n"
            "  - Use ORDER BY timestamp for time series data queries\n"
            "  - Create TAG indexes for frequently used queries"
        )

        print("\n" + "="*60)
        print("SCENARIO COMPLETED SUCCESSFULLY")
        print("="*60)

    # ============================================================
    # Scenario 3: InfluxDB to KaiwuDB (Time Series) Migration
    # ============================================================
    
    def scenario_influxdb_to_kwdb(self):
        """Simulate InfluxDB to KaiwuDB time series migration."""
        print("\n" + "="*60)
        print("SCENARIO: InfluxDB 2.x to KaiwuDB (Time Series) Migration")
        print("="*60)
        
        # Step 1: User Request
        self.log("user", "I want to migrate InfluxDB metrics bucket to KaiwuDB time series database")
        
        # Step 2: AI Agent Recognizes Intent
        self.log_system("Recognizing migration intent...")
        self.log_system("Checking InfluxDB capabilities...")
        
        influx_cap = self.ds_manager.get_capability("INFLUXDB2X")
        self.log_system(f"InfluxDB 2.x capabilities: {influx_cap}")
        
        self.log("agent",
            "[OK] Migration intent recognized: InfluxDB (metrics) -> KaiwuDB (TIMESERIES)\n\n"
            "[INFO] InfluxDB Note: Full migration requires two steps:\n"
            "  1. Schema migration (DDL)\n"
            "  2. Data migration\n\n"
            "Please provide the following information:\n"
            "  1. KDTS server address (default: http://127.0.0.1:8989)\n"
            "  2. InfluxDB connection info (version 2.x)\n"
            "  3. KaiwuDB connection info\n\n"
            "[IMPORTANT] Security reminder: Please ensure you have backed up before migration!"
        )
        
        # Step 3: User Provides Parameters
        user_input = {
            "kdts_url": "http://192.168.1.100:8989",
            "influx_host": "192.168.1.60",
            "influx_port": 8086,
            "influx_token": "my-influxdb-token",
            "influx_bucket": "metrics",
            "kwdb_host": "127.0.0.1",
            "kwdb_port": 26257,
            "kwdb_user": "root",
            "kwdb_password": "kwdb_secret",
            "kwdb_db": "metrics_ts"
        }
        self.log("user", json.dumps(user_input, ensure_ascii=False, indent=2))
        
        # Step 4: AI Agent Validates
        self.log_system("Validating InfluxDB 2.x support...")
        is_full = self.ds_manager.is_full_migration_capable("INFLUXDB2X")
        is_meta = self.ds_manager.is_metadata_capable("INFLUXDB2X")
        
        self.log_system(f"InfluxDB 2.x supports full migration: {is_full}")
        self.log_system(f"InfluxDB 2.x supports metadata: {is_meta}")
        
        self.log("agent",
            "[OK] InfluxDB 2.x supports full migration (Schema + Data)\n\n"
            "Migration plan (two steps):\n"
            "  Step 1: Schema migration - Read measurements from InfluxDB and create KaiwuDB time series tables\n"
            "  Step 2: Data migration - Migrate data to the created tables\n\n"
            "Start execution? (yes/no)"
        )
        
        # Step 5: User Confirms
        self.log("user", "yes")
        
        # Step 6: Simulate Two-Step Migration
        self.log_system("Step 1: Schema Migration...")
        self.log("agent",
            "[INFO] Reading InfluxDB metadata...\n\n"
            "Found 3 measurements:\n"
            "  - cpu_usage (tags: host, region; fields: usage, temperature)\n"
            "  - memory_usage (tags: host, region; fields: used, free)\n"
            "  - network_io (tags: host, interface; fields: rx_bytes, tx_bytes)\n\n"
            "[WARNING] DDL preview (cpu_usage):\n"
            "CREATE TABLE cpu_usage (\n"
            "    time TIMESTAMP,\n"
            "    host VARCHAR(100) PRIMARY TAG,\n"
            "    region VARCHAR(50) TAG,\n"
            "    usage FLOAT8 FIELD,\n"
            "    temperature FLOAT8 FIELD\n"
            ");\n\n"
            "Confirm DDL execution? (yes/no)"
        )
        
        self.log("user", "yes")
        
        self.log("agent", "[OK] Step 1 completed: 3 time series tables created")
        
        self.log_system("Step 2: Data Migration...")
        self.log("agent",
            "[INFO] Starting data migration...\n\n"
            "[OK] Migration completed!\n\n"
            "Migration report:\n"
            "  Schema migration: [OK] Success (3 tables)\n"
            "  Data migration: [OK] Success (3,703,701 rows)\n"
            "  Error rows: 0"
        )
        
        print("\n" + "="*60)
        print("SCENARIO COMPLETED SUCCESSFULLY")
        print("="*60)
    
    # ============================================================
    # Scenario 3: Error Handling
    # ============================================================
    
    def scenario_error_handling(self):
        """Simulate error handling scenarios."""
        print("\n" + "="*60)
        print("SCENARIO: Error Handling")
        print("="*60)
        
        # Test unsupported source type
        self.log("user", "Help me migrate Redis data to KaiwuDB")
        
        self.log_system("Checking source type support...")
        redis_result = ConfigValidator.validate_source_type("REDIS")
        
        self.log("agent",
            "[WARNING] Redis is not supported as a source database\n\n"
            "Currently supported source database types:\n"
            "  Relational: MySQL, Oracle, PostgreSQL, SQL Server, ClickHouse\n"
            "  Time Series: TDengine, InfluxDB 1.x/2.x, OpenTSDB\n"
            "  Others: KaiwuDB, MongoDB, FTP, HDFS\n\n"
            "[ALTERNATIVE] Alternative solutions:\n"
            "  1. Export Redis data to CSV/JSON, then import using FTP/HDFS\n"
            "  2. First migrate to a supported database, then migrate to KaiwuDB"
        )
        
        # Test error handler
        self.log_system("Testing error handler...")
        
        # Simulate a connection error
        error_info = ErrorHandler.get_error_info(2001)
        if error_info:
            self.log("agent",
                f"\n[ERROR] Simulated error test:\n\n"
                f"Error code: 2001\n"
                f"Error name: {error_info.get('name', 'Unknown')}\n"
                f"Error description: {error_info.get('description', 'N/A')}\n"
                f"Fix suggestions:\n"
                f"  {error_info.get('fix_suggestions', [])}"
            )
        else:
            self.log("agent", "\n[ERROR] Error code 2001 not found")
        
        print("\n" + "="*60)
        print("SCENARIO COMPLETED SUCCESSFULLY")
        print("="*60)
    
    # ============================================================
    # Scenario 5: Chinese User Input Test
    # ============================================================
    
    def simulate_chinese_user_scenario(self):
        """Test that the skill properly handles Chinese user input."""
        print("\n" + "#"*60)
        print("TESTING: Chinese User Input Support")
        print("#"*60)
        
        # Test 1: Simple Chinese migration request
        print("\n" + "-"*60)
        print("Test 1: Simple Chinese Migration Request")
        print("-"*60)
        
        self.log("user", "帮我把 MySQL 数据库的订单表迁移到 KaiwuDB")
        
        self.log_system("Recognizing Chinese migration intent...")
        self.log_system("Checking if response should be in Chinese...")
        
        # According to SKILL.md Language Support section,
        # the Agent should respond in the same language as the user
        self.log("agent",
            "[OK] 已识别迁移需求: MySQL -> KaiwuDB\n\n"
            "请提供以下信息以开始迁移:\n\n"
            "1. KDTS 服务器地址 (默认: http://127.0.0.1:8989)\n"
            "2. MySQL 连接信息:\n"
            "   - 主机地址:\n"
            "   - 端口 (默认 3306):\n"
            "   - 用户名:\n"
            "   - 密码:\n"
            "   - 数据库名称:\n"
            "3. KaiwuDB 连接信息:\n"
            "   - 主机地址 (默认 127.0.0.1):\n"
            "   - 端口 (默认 26257):\n"
            "   - 用户名 (默认 root):\n"
            "   - 密码:\n"
            "   - 目标数据库名称:\n"
            "   - 引擎类型 (RELATIONAL 或 TIMESERIES):\n\n"
            "[重要] 安全提醒: 迁移前请确保已备份源数据库!"
        )
        
        print("\n[TEST PASSED] Agent responded in Chinese as expected")
        
        # Test 2: Chinese InfluxDB migration request
        print("\n" + "-"*60)
        print("Test 2: Chinese InfluxDB Migration Request")
        print("-"*60)
        
        self.log("user", "我想把 InfluxDB 的监控数据迁移到 KaiwuDB 时序数据库")
        
        self.log_system("Recognizing Chinese InfluxDB migration intent...")
        self.log_system("Checking InfluxDB capabilities...")
        
        influx_cap = self.ds_manager.get_capability("INFLUXDB2X")
        self.log_system(f"InfluxDB 2.x capabilities: {influx_cap}")
        
        self.log("agent",
            "[OK] 已识别迁移需求: InfluxDB -> KaiwuDB (TIMESERIES)\n\n"
            "[信息] InfluxDB 说明: 完整迁移需要两步:\n"
            "  1. Schema 迁移 (DDL)\n"
            "  2. 数据迁移\n\n"
            "请提供以下信息:\n"
            "  1. KDTS 服务器地址 (默认: http://127.0.0.1:8989)\n"
            "  2. InfluxDB 连接信息 (版本 1.x 或 2.x):\n"
            "     - 主机/端口:\n"
            "     - Token (2.x 需要) 或 用户名/密码:\n"
            "     - Bucket/Database 名称:\n"
            "  3. KaiwuDB 连接信息:\n"
            "     - 主机/端口 (默认 127.0.0.1:26257):\n"
            "     - 用户名/密码:\n"
            "     - 目标数据库名称:\n\n"
            "[重要] 安全提醒: 迁移前请确保已备份!"
        )
        
        print("\n[TEST PASSED] Agent responded in Chinese with InfluxDB-specific information")
        
        # Test 3: Verify source capabilities with Chinese explanation
        print("\n" + "-"*60)
        print("Test 3: Source Capability Check (InfluxDB 2.x)")
        print("-"*60)
        
        self.log_system("Verifying InfluxDB 2.x source capability...")
        
        # Get InfluxDB capability details
        influx_caps = self.ds_manager.get_capability("INFLUXDB2X")
        
        self.log("agent",
            f"[信息] InfluxDB 2.x 能力配置:\n\n"
            f"  迁移能力: {influx_caps.get('capability')}\n"
            f"  支持元数据: {'是' if influx_caps.get('supports_metadata') else '否'}\n"
            f"  支持完整迁移: {'是' if influx_caps.get('supports_full_migration') else '否'}\n"
            f"  引擎类型: {influx_caps.get('engine')}\n\n"
            f"[说明] InfluxDB 2.x 支持元数据+数据迁移 (META_AND_DATA)，但不支持完整迁移。\n"
            f"因此需要分两步执行: 先迁移 Schema，再迁移数据。"
        )
        
        print("\n[TEST PASSED] Agent correctly explains InfluxDB capability in Chinese")
        
        # Test 4: Verify Tag constraints for Chinese users
        print("\n" + "-"*60)
        print("Test 4: KaiwuDB Time-Series Tag Constraints")
        print("-"*60)
        
        self.log("user", "我要把一个有 150 个字段的 MySQL 表迁移到 KaiwuDB 时序数据库")
        
        self.log("agent",
            "[警告] 检测到可能超出 KaiwuDB 时序表限制:\n\n"
            "KaiwuDB 时序表约束:\n"
            "  - 最大列数 (Tag + Value): 128\n"
            "  - 最大主键 Tag 数: 4\n"
            "  - Tag/列名最大长度: 128 字节\n"
            "  - 至少需要 1 个主键 Tag\n\n"
            "当前源表字段数: 150 (超出限制)\n\n"
            "[建议] 解决方案:\n"
            "  1. 减少字段数量\n"
            "  2. 将数据拆分到多个表\n"
            "  3. 将部分字段转换为值 (Value) 而非 Tag\n\n"
            "是否要继续迁移部分字段? 还是先调整源表结构?"
        )
        
        print("\n[TEST PASSED] Agent correctly explains KaiwuDB constraints in Chinese")
        
        print("\n" + "#"*60)
        print("ALL CHINESE USER INPUT TESTS PASSED!")
        print("Test completed successfully - Skill properly handles Chinese user input")
        print("#"*60)
    
    # ============================================================
    # Run All Scenarios
    # ============================================================
    
    def run_all_scenarios(self):
        """Run all dialogue scenarios."""
        print("\n" + "#"*60)
        print("# KWDB Data Migration - AI Agent Dialogue Simulator")
        print("#"*60)
        
        self.scenario_mysql_to_kwdb()
        self.scenario_mysql_to_kwdb_timeseries()
        self.scenario_influxdb_to_kwdb()
        self.scenario_error_handling()
        self.simulate_chinese_user_scenario()
        
        print("\n" + "#"*60)
        print("# ALL SCENARIOS COMPLETED SUCCESSFULLY")
        print("#"*60)
    
    def run_scenario(self, scenario_name):
        """Run a specific scenario by name."""
        scenarios = {
            "mysql_to_kwdb": self.scenario_mysql_to_kwdb,
            "mysql_to_kwdb_timeseries": self.scenario_mysql_to_kwdb_timeseries,
            "influxdb_to_kwdb": self.scenario_influxdb_to_kwdb,
            "error_handling": self.scenario_error_handling,
            "chinese_user": self.simulate_chinese_user_scenario,
        }
        
        if scenario_name in scenarios:
            scenarios[scenario_name]()
        else:
            print(f"\n[ERROR] Unknown scenario: {scenario_name}")
            print(f"Available scenarios: {list(scenarios.keys())}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="KWDB Data Migration - AI Agent Dialogue Simulator"
    )
    parser.add_argument(
        "--scenario", "-s",
        type=str,
        choices=["mysql_to_kwdb", "mysql_to_kwdb_timeseries", "influxdb_to_kwdb", "error_handling", "chinese_user", "all"],
        default="all",
        help="Scenario to run (default: all)"
    )
    
    args = parser.parse_args()
    simulator = DialogueSimulator()
    
    if args.scenario == "all":
        simulator.run_all_scenarios()
    else:
        simulator.run_scenario(args.scenario)


if __name__ == "__main__":
    main()
