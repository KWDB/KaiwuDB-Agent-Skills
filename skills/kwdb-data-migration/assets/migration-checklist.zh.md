# KDTS 异构数据库迁移检查清单

完整的迁移流程检查清单，确保每个步骤正确执行。

## 语言版本

- **中文版**: 本文件 (`migration-checklist.zh.md`)
- **英文版**: [migration-checklist.md](./migration-checklist.md)

AI Agent 将使用与用户相同的语言进行回复。

---

## 阶段一：迁移准备

### 1.1 环境检查

- [ ] KDTS Server 已启动并可访问
    - 访问 `http://{kdts_host}:{port}/kdts/api/v1/health` 确认状态
    - 默认端口：8989
- [ ] 源数据库可从 KDTS 服务器网络访问
    - 测试连通性：`ping {source_host}` 或 `telnet {source_host} {port}`
- [ ] 目标 KaiwuDB 已安装并启动
    - 测试连接：`mysql -h {kwdb_host} -P {port} -u root -p`
- [ ] Python 3 已安装（KDTS 服务器）
    - 执行：`python3 --version`

### 1.2 账号权限

- [ ] 源数据库账号权限充足
    - MySQL: 对目标库有 SELECT 权限
    - Oracle: SELECT_CATALOG_ROLE 或 DBA
    - PostgreSQL: 对 schema 有 USAGE 权限
    - 其他数据库: 参考对应文档
- [ ] 目标 KaiwuDB 账号权限充足
    - CREATE、DROP、ALTER（用于 DDL）
    - INSERT、SELECT（用于数据迁移）
    - 目标库已创建或允许自动创建
- [ ] 网络防火墙/安全组已开放所需端口

### 1.3 备份提醒

- [ ] 源数据库关键数据已备份
- [ ] 目标数据库现有数据已备份（如有）
- [ ] 迁移失败回滚方案已准备

---

## 阶段二：连接与元数据

### 2.1 连接测试

- [ ] 源数据库连接测试通过

  POST /kdts/api/v1/datasource/validate
  ```json
  {
    "engine": "RELATIONAL",
    "type": "MYSQL",
    "host": "example-host",
    "port": 3306,
    "username": "user",
    "password": "pass",
    "dbName": "example_db",
    "isTarget": false
  }
  ```
    - 预期返回: `{"code": 0, "data": "SUCCEED"}`
- [ ] 目标 KaiwuDB 连接测试通过
    - 设置 `isTarget: true`

### 2.2 源端元数据

- [ ] 列出源数据库

  POST /kdts/api/v1/datasource/databases

  ```json
  {
    "engine": "RELATIONAL",
    "type": "MYSQL",
    "host": "127.0.0.1",
    "port": 3306,
    "username": "user",
    "password": "pass",
    "dbName": null
  }
  ```

- [ ] 读取目标表元数据

  POST /kdts/api/v1/datasource/metadata
  ```json
  {
    "source": {
      "engine": "RELATIONAL",
      "type": "MYSQL",
      "host": "127.0.0.1",
      "port": 3306,
      "username": "user",
      "password": "pass",
      "dbName": "example_db"
    },
    "metadata": {
      "enable": true,
      "autoDdl": false,
      "primaryKey": true,
      "constraint": true,
      "comment": true,
      "index": true,
      "view": false
    }
  }
  ```
- [ ] 确认元数据完整性
    - 表数量正确
    - 列数量和类型正确
    - 主键/约束正确
    - （可选）注释、索引已包含

### 2.3 不支持元数据的源

**如果源不支持元数据（SQL Server 部分版本、TDengine 2.x、InfluxDB 2.x、MongoDB、FTP、HDFS）：**

- [ ] 跳过元数据步骤
- [ ] 手动准备表映射配置
- [ ] 在迁移请求中显式指定 tables 字段

---

## 阶段三：DDL 与结构迁移

### 3.1 DDL 预览

- [ ] 预览目标 DDL

  POST /kdts/api/v1/metadata/preview
  ```json
  {
    "target": {
      "engine": "RELATIONAL",
      "type": "KAIWUDB",
      "host": "127.0.0.1",
      "port": 26257,
      "username": "root",
      "password": "pass",
      "dbName": "target_db",
      "isTarget": true
    },
    "sourceDb": {
      "type": "MYSQL",
      "name": "source_db",
      "encoding": "UTF-8",
      "tableMap": {
        "example_table": {
          "tableName": "example_table",
          "columns": [
            {
              "columnName": "id",
              "columnType": "INT",
              "nullAble": false,
              "finalConvertDataType": "INT",
              "isChecked": true
            }
          ],
          "primaryKey": {
            "tableName": "example_table",
            "columns": [{"columnName": "id", "asc": true}]
          },
          "constraint": [],
          "indexes": []
        }
      },
      "viewMap": {}
    },
    "metadata": {
      "enable": true,
      "autoDdl": false,
      "primaryKey": true,
      "constraint": true,
      "comment": true,
      "index": true,
      "view": false
    },
    "isTimeSeries": false
  }
  ```

  **注意**：`sourceDb` 字段必须是从 `/datasource/metadata` API 返回的完整 `Database` 对象。
  不要传入简化结构，请使用完整的响应对象。
- [ ] 检查生成的 DDL
    - 表名是否匹配
    - 列名和类型是否正确映射
    - 主键/约束是否保留
    - 特殊类型是否正确转换

### 3.2 DDL 执行

- [ ] （如需要）删除目标现有表
    - 确认目标表数据已备份或可丢弃
    - 使用 KaiwuDB DROP TABLE 命令
- [ ] 执行 DDL

  POST /kdts/api/v1/metadata/execute
  ```json
  {
    "target": {
      "engine": "RELATIONAL",
      "type": "KAIWUDB",
      "host": "127.0.0.1",
      "port": 26257,
      "username": "root",
      "password": "pass",
      "dbName": "target_db",
      "isTarget": true
    },
    "ddlScript": {
      "dbName": "SOURCE_DB",
      "createDb": "CREATE DATABASE SOURCE_DB ENGINE=TIMESERIES",
      "table": {
        "example_table": "CREATE TABLE example_table (id INT PRIMARY KEY, name VARCHAR(100))"
      },
      "view": {}
    },
    "autoDdl": false
  }
  ```

  **注意**：`ddlScript` 必须是从 `/metadata/preview` API 返回的完整 `DdlScript` 对象。
  不要传入简单的 SQL 语句数组。
- [ ] 验证 DDL 执行结果
    - 检查是否创建成功
    - 检查列类型是否正确

### 3.3 仅数据迁移场景

**如果目标表已存在且结构匹配：**

- [ ] 跳过 DDL 阶段
- [ ] 确认目标表结构与源端一致
- [ ] 如需清空数据，执行 `TRUNCATE TABLE`

### 3.4 关系源 → 时序目标场景（RELATIONAL → TIMESERIES）

**重要**：KDTS `preview_ddl` 完全支持时序 DDL 生成 —— 请求字段名为 `"isTimeSeries": true`，且 `sourceDb` 列上带有 tag 标记。

- [ ] 引导用户选择主标签（PRIMARY TAGS，1-4 个，必选）
    - 排除浮点类型（FLOAT/DOUBLE/DECIMAL/NUMERIC 等不可作主标签）
    - 建议选择唯一标识列（如 device_id、sensor_id）
- [ ] 引导用户选择普通标签（TAGS，可选）
- [ ] 在 `sourceDb` 列上设置标记（可调用 `mark_time_series_columns()` 辅助函数）：
    - 时间列：`"isTs": true`（KDTS 生成首列 `TIMESTAMPTZ NOT NULL`）
    - 主标签：`"isTag": true` + `"isPrimaryTag": true` + `"nullAble": false`
      （主标签列定义必须非空，否则 KDTS 降级该标签，可能报 3006；辅助函数自动处理）
    - 普通标签：`"isTag": true`
- [ ] 检查所选主标签列源数据无 NULL 值
    ```sql
    SELECT COUNT(*) FROM <table> WHERE <primary_tag_col> IS NULL;
    ```
    （主标签必须非空，源数据含 NULL 会导致迁移失败）
- [ ] 调用 `preview_ddl(target, source_db, metadata, is_time_series=True)` 生成时序 DDL
    - 验证返回 `CREATE TS DATABASE` 与 `TAGS (...)` / `PRIMARY TAGS (...)` 子句
    - 无 tag 标记的表会被 KDTS **跳过**（不生成 DDL），需提醒用户
    - 注意 KDTS 自动降级/转换（浮点/nullable 主标签降级、NVARCHAR→VARCHAR 等）
- [ ] 通过 `execute_ddl` API 执行（createDb 由 KDTS 按目标引擎自动生成）
- [ ] 数据迁移阶段使用显式表映射（`tables` 必填）

---

## 阶段四：数据迁移

### 4.1 配置 DataX 参数（必需）

**重要提示**：包含 `core` 和 `setting` 字段的 DataX 配置对于成功执行数据迁移是必需的！缺少这些字段会导致迁移失败！

**三种配置方式（互斥）：**
- 方式一：固定通道数（简单，推荐用于大多数场景）
- 方式二：按字节限速（精确控制带宽）
- 方式三：按记录数限速（精确控制 QPS）

- [ ] 查看默认 DataX 配置（方式一：固定通道数）

  默认 DataX 配置：
  ```json
  {
    "batchSize": 1000,
    "core": {
      "transport": {
        "channel": {
          "speed": {
            "byte": 1048576,
            "record": 1000
          }
        }
      }
    },
    "enable": true,
    "fetchSize": 1000,
    "setting": {
      "errorLimit": {
        "percentage": 0.02
      },
      "speed": {
        "channel": 4
      }
    }
  }
  ```

- [ ] 确认或自定义 DataX 参数：
  
  **通用参数（所有方式）：**
  - `fetchSize`: 从源数据库每次获取的记录数（默认：1000）
  - `batchSize`: 写入目标数据库的批次记录数（默认：1000）
  - `setting.errorLimit.percentage`: 可接受的错误百分比（默认：0.02 = 2%）
  
  **方式一：固定通道数**
  - `setting.speed.channel`: 并行通道数（默认：4）
  - `core.transport.channel.speed.byte`: 可选的单通道字节限速（默认：1048576 = 1MB/秒）
  - `core.transport.channel.speed.record`: 可选的单通道记录限速（默认：1000 记录/秒）
  
  **方式二：按字节限速**
  - `setting.speed.byte`: 全局字节限速（如：52428800 = 50MB/秒）
  - `core.transport.channel.speed.byte`: 必需的单通道字节限速（如：10485760 = 10MB/秒）
  - 通道数自动计算：全局限速 ÷ 单通道限速
  
  **方式三：按记录数限速**
  - `setting.speed.record`: 全局记录限速（如：40000 = 40000 记录/秒）
  - `core.transport.channel.speed.record`: 必需的单通道记录限速（如：1000 = 1000 记录/秒）
  - 通道数自动计算：全局限速 ÷ 单通道限速

- [ ] 验证配置约束：
  - 方式一与方式二/三**互斥**（不能混用）
  - 使用方式二时，必须配置 `core.transport.channel.speed.byte`
  - 使用方式三时，必须配置 `core.transport.channel.speed.record`
  - 不要在 `core.transport.channel.speed` 中配置 `channel`（只能在 `setting.speed` 中配置）

### 4.2 构建迁移脚本

- [ ] 构建 DataX 迁移脚本

  POST /kdts/api/v1/datax/build
  ```json
  {
    "source": {
      "engine": "RELATIONAL",
      "type": "MYSQL",
      "host": "127.0.0.1",
      "port": 3306,
      "username": "user",
      "password": "pass",
      "dbName": "source_db"
    },
    "target": {
      "engine": "RELATIONAL",
      "type": "KAIWUDB",
      "host": "127.0.0.1",
      "port": 26257,
      "username": "root",
      "password": "pass",
      "dbName": "target_db",
      "isTarget": true
    },
    "tables": [],
    "data": {
      "batchSize": 1000,
      "core": {
        "transport": {
          "channel": {
            "speed": {
              "byte": 1048576,
              "record": 1000
            }
          }
        }
      },
      "enable": true,
      "fetchSize": 1000,
      "setting": {
        "errorLimit": {
          "percentage": 0.02
        },
        "speed": {
          "channel": 4
        }
      }
    }
  }
  ```

  **注意**：
  - 空的 `tables` 数组表示自动发现所有表（仅适用于支持完整迁移的源，且**仅限 RELATIONAL 目标**）。
  - **TIMESERIES 目标必须显式提供表映射**：空 `tables` 会报错 4001
    "No datax contents generated from config"（实测结论）。
  - 对于表级迁移，需要显式指定表列表。
  - **关键提示**：`data` 中的 `core` 和 `setting` 字段对于成功执行 DataX 是必需的。

- [ ] 记录返回的脚本文件名
    - 格式：`{SOURCE}2KAIWUDB_{timestamp}.json`
    - 记录文件名用于后续查询

### 4.3 执行迁移

- [ ] 启动迁移

  POST /kdts/api/v1/datax/execute
  ```json
  ["MYSQL2KAIWUDB_1719290000.json"]
  ```
- [ ] **脚本数 > 10 时使用分批执行**（`execute_migration_batches(script_names, batch_size=10)`）
    - 一次提交过多脚本会触发 HTTP 4003 超时
    - 每批提交 10 个脚本,等待该批全部进入终态后再提交下一批
    - 4003 仅表示响应超时,请求已送达服务端,仍需继续监控该批
- [ ] 记录返回的日志文件路径

### 4.3 监控进度

- [ ] 定期查询任务状态
  ```
  GET /kdts/api/v1/datax/status?scriptName=MYSQL2KAIWUDB_1719290000.json
  ```
- [ ] 状态说明
    - `SUBMITTED`: 已提交，等待执行
    - `RUNNING`: 执行中
    - `SUCCEEDED`: 成功完成
    - `FAILED`: 执行失败
    - `KILLED`: 被终止
- [ ] 如失败，查看详细日志

### 4.4 大规模数据迁移建议

- [ ] 为大表设置 `splitPk` 启用并行
- [ ] 调整 `fetchSize` 和 `batchSize`
- [ ] 设置 `speed.channel` 增加并发
- [ ] 按时间范围分批次执行迁移

---

## 阶段五：迁移验证

### 5.1 数据量核对

- [ ] 逐表核对记录数
  ```sql
  -- 源端
  SELECT COUNT(*) FROM table_name;
  
  -- 目标端
  SELECT COUNT(*) FROM table_name;
  ```
- [ ] 核对结果一致（或符合预期差异）

### 5.2 数据抽样校验

- [ ] 随机抽取记录对比
  ```sql
  -- 比较关键字段
  SELECT * FROM table_name ORDER BY pk LIMIT 100;
  ```
- [ ] 核对特殊值（NULL、空字符串、特殊字符）

### 5.3 业务验证

- [ ] 核心业务场景验证通过
- [ ] 应用功能正常
- [ ] 性能无明显下降

---

## 常见问题排查

### Q1: 连接测试失败

**检查清单：**

- [ ] 数据库服务是否启动
- [ ] host/port 是否正确
- [ ] 网络是否通畅（防火墙）
- [ ] 用户名/密码是否正确
- [ ] 数据库是否存在
- [ ] KDTS 服务器是否有访问权限

### Q2: DDL 预览错误

**检查清单：**

- [ ] 源类型是否支持元数据
- [ ] 是否有不支持的列类型
- [ ] KaiwuDB 版本是否兼容

### Q3: 迁移超时

**检查清单：**

- [ ] 源表是否过大
- [ ] 是否需要分批次迁移
- [ ] 网络带宽是否足够
- [ ] KDTS 服务器资源是否充足

**解决方案：**

- 增加超时时间
- 缩小迁移范围
- 启用并行（splitPk）
- 优化查询（WHERE 条件）

### Q4: 迁移任务 FAILED 但状态查询无详细错误

**检查清单：**

- [ ] 查看 KDTS 服务器日志文件（`/opt/kdts/data/log/`）
- [ ] 时序迁移：主标签列源数据是否含 NULL 值
    - 主标签必须非空，源数据 NULL 会导致写入失败
    - 解决方案：修复源数据 / 更换主标签列 / 降级为普通标签
- [ ] 时序目标是否使用了显式表映射（空 `tables` 会报 4001）

### Q5: 部分数据丢失

**检查清单：**

- [ ] 是否有报错日志
- [ ] 是否有数据被过滤器排除
- [ ] 是否有写入失败

**解决方案：**

- 检查错误日志
- 增加 errorLimit 百分比
- 重试失败的表

---

## 回滚方案

### 场景 1: DDL 执行失败

1. 检查目标表状态
2. 删除已创建的表（如有）
3. 修复源端问题
4. 重新执行 DDL

### 场景 2: 数据迁移失败（未完成）

1. 查询任务状态：`GET /datax/status?scriptName=...`
2. 如可恢复：检查是否支持 resume（有限场景）
3. 如不可恢复：
    - 清空目标表（TRUNCATE）
    - 重新构建并执行迁移

### 场景 3: 迁移完成但数据有问题

1. 评估影响范围
2. 修复问题数据
3. 重新迁移受影响的表（需清空）
4. 或手动修复目标数据

---

## 性能优化建议

### 迁移前

- [ ] 源库：确保统计信息最新（ANALYZE TABLE）
- [ ] 源库：避免高峰时段执行
- [ ] 目标库：创建足够的表空间
- [ ] 目标库：禁用不必要的触发器/约束

### 迁移中

- [ ] 使用 `splitPk` 启用并行读取
- [ ] 调整 `speed.channel` 增加并行写入
- [ ] 合理设置 `fetchSize` 和 `batchSize`
- [ ] 监控系统资源（CPU、内存、磁盘 I/O）

### 迁移后

- [ ] 重建目标库索引（如已禁用）
- [ ] 更新统计信息
- [ ] 验证数据完整性

---

## 成功标准

[OK] 所有表迁移完成  
[OK] 记录数一致  
[OK] 数据抽样无差异  
[OK] 业务功能正常  
[OK] 性能达标

---

**文档版本：** v1.0.0  
**最后更新：** 2026-08-03  
**维护者：** KDTS 开发团队
