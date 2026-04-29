---
name: kwdb-data-migration
description: |
  Assist with full-lifecycle KaiwuDB data migration tasks, including source configuration,
  data type mapping, migration policy setup, parameter validation, Headless command generation,
  connection checks, time-series slicing, and troubleshooting.
  Trigger keywords: migration, KDTS, KaiwuDB, data migration, type mapping,
  time-series, relational, Headless, split interval, where filter, DDL, DML.
  NOT for: installation, deployment, cluster management, SQL tuning, backup, restore.
version: 1.0.0
---

<!-- 
辅助完成KaiwuDB全生命周期数据迁移任务，包括数据源配置、数据类型映射、迁移策略设定、参数校验、Headless命令生成、连通性检查、时序分片及故障排查。  
触发关键词：迁移、KDTS、KaiwuDB、数据迁移、类型映射、时序、关系、Headless、切分间隔、where过滤、DDL、DML。  
不适用场景：安装、部署、集群管理、SQL调优、备份、恢复。  
-->

## EXTREMELY IMPORTANT

ALWAYS invoke this skill via the Skill tool before performing any KaiwuDB migration.

1. This applies even when:
    - Reference file contents appear in conversation context
    - Session was restored from a compacted conversation
    - You believe you already know the KaiwuDB migration rules
2. Reading reference files directly is not equivalent to Skill invocation.
3. The Skill tool triggers the complete standard workflow and ensures guardrails are followed.
4. Skip this step equals skipping the standard migration workflow and validation.

<!-- 
极度重要说明：执行任何KaiwuDB迁移操作前，必须通过Skill工具调用本技能  
1. 即使出现以下情况，也必须触发本技能：  
    - 参考文件内容已出现在对话上下文中  
    - 会话从压缩对话中恢复  
    - 你认为自己已经掌握了KaiwuDB迁移规则  
2. 分层参考架构：明确不同层级的参考文件和配置重点  
3. Skill工具会触发完整的标准工作流，并确保遵循所有防护规则  
4. 跳过此步骤等同于跳过标准迁移流程和校验
-->

## Tiered Reference Architecture

**Tier 1 (Always Read)** - Core rules and workflow

- `references/key-rules.md` - Core migration constraints and business rules
- `references/path-discovery.md` - Standard migration process and step definition
- `references/triage-playbook.md` - Migration fault diagnosis and handling manual
- `references/data-type-mapping.md` - Standard data type mapping rules

<!-- 
第一层（必须阅读）- 核心规则和工作流  
- 迁移核心约束和业务规则  
- 标准迁移流程和步骤定义  
- 迁移故障诊断和处理手册  
- 标准数据类型映射规则  
-->

**Tier 2 (Mandatory Parameters)** - High-frequency configuration items

- Time-series: time_column, start_time, end_time
- Relational: split key, where filter
- Write modes: INSERT / UPSERT

<!-- 
第二层（必填参数）- 高频配置项  
- 时序迁移必填参数：时间列、开始时间、结束时间  
- 关系迁移相关：切分主键、where过滤条件  
- 写入模式：插入（默认）、更新插入
-->

**Tier 3 (Execution & Tuning)** - Execution and optimization items

- Headless command generation
- Channel count & flow control
- JVM tuning & batch size

<!-- 
第三层（执行与调优）- 执行和优化相关项  
- Headless命令生成  
- 并发通道数和流量控制  
- JVM调优和批次大小设置
-->

## When to Activate

### Should trigger

- Migrate business data to KaiwuDB
- Use KaiwuDB official migration tool
- Configure migration task parameters and policy
- Generate Headless running command for migration
- Diagnose and resolve migration task errors (including type mismatch)
- Verify migration task configuration validity
- Slice migration tasks by time interval
- Check data type mapping between source and KaiwuDB

<!-- 
- 将业务数据迁移到KaiwuDB  
- 使用KaiwuDB官方迁移工具  
- 配置迁移任务参数和策略  
- 生成迁移用的Headless运行命令  
- 诊断并解决迁移任务报错（含类型不匹配）  
- 校验迁移任务配置的合法性  
- 按时间间隔对迁移任务进行分片  
- 核查数据源与KaiwuDB之间的数据类型映射
-->

### Should NOT trigger

- KaiwuDB installation, deployment and cluster initialization
- Cluster node management and status query
- Conventional SQL query writing and performance tuning
- Database backup, restore and permission management
- Daily DDL operation without migration background

<!--
- KaiwuDB的安装、部署和集群初始化  
- 集群节点管理和状态查询  
- 常规SQL编写和性能调优  
- 数据库备份、恢复和权限管理  
- 无迁移背景的日常DDL操作  
-->

## Supported Migration Scope

| Category           | Supported Content                                                                                  |
|--------------------|----------------------------------------------------------------------------------------------------|
| Data Sources       | MySQL, PostgreSQL, Oracle, TDengine, InfluxDB, OpenTSDB, FTP, HDFS, MongoDB, SQLServer, ClickHouse |
| Target Engines     | Relational Engine, Time-Series Engine                                                              |
| Migration Modes    | Schema-only, Data-only, Schema & Data full migration                                               |
| Migration Policies | WHERE filter condition, time range filter, split key, split interval, custom SQL                   |
| Write Modes        | INSERT, UPSERT                                                                                     |
| Execution Modes    | Graphical GUI mode, Headless command line mode                                                     |

## Workflow

### Step 1: Distinguish Engine Type

Classify the target into Relational Engine / Time-Series Engine / Mixed scenario.
If unclear, actively ask user, do not assume arbitrarily.

<!-- 
步骤1：区分引擎类型  
将目标引擎归类为关系引擎、时序引擎或混合场景；信息不明确时主动询问，禁止自行臆断  
-->

### Step 2: Confirm Migration Basic Information

Confirm data source type, migration mode, target business scenario.

<!-- 
步骤2：确认迁移基础信息  
确认数据源类型、迁移模式、目标业务场景  
-->

### Step 3: Verify Mandatory Parameters & Data Type Mapping

- Time-series migration: Check time_column, start_time, end_time + data type mapping compliance.
- Relational migration: Check split key, custom SQL mutual exclusion rules + data type mapping compliance.

<!-- 
步骤3：校验必填参数及数据类型映射  
时序迁移需校验时间列、开始时间、结束时间及数据类型映射合规性；关系迁移需校验切分主键、自定义SQL互斥规则及数据类型映射合规性  
-->

### Step 4: Configure Migration Policy

Set filter conditions, split interval, batch size and concurrency channel.

<!-- 
步骤4：配置迁移策略  
设置过滤条件、切分间隔、批次大小和并发通道  
-->

### Step 5: Generate Executable Configuration and Command

Output standard Headless command and task configuration template.

<!-- 
步骤5：生成可执行配置与命令  
输出标准Headless命令和任务配置模板  
-->

### Step 6: Verify and Troubleshoot

Check running logs, count data rows; locate fault (including type mismatch) according to playbook when abnormal.

<!-- 
步骤6：校验与故障排查  
查看运行日志、统计数据行数；异常时（含类型不匹配）依据排查手册定位问题  
-->

## Output Format

```markdown
## Intent

[Brief description of this migration task scenario]

## Source & Target

- Data Source:
- Target Engine:
- Migration Mode:

## Mandatory Configuration Parameters

## Data Type Mapping Verification

(Refer to references/data-type-mapping.md)

## Migration Policy & Filter Rules

## Recommended Headless Execution Command

{{headless_command}}

## Post-Migration Verification & Matters Needing Attention

```

## Guardrails

1. Must distinguish relational engine and time-series engine first before any configuration.
2. Must verify mandatory parameters for time-series migration completely.
3. Must follow parameter mutual exclusion rules: custom SQL cannot be used with WHERE and time filter.
4. Must verify data type mapping compliance before configuration submission.
5. Do not generate execution command before configuration validation passed.
6. Production environment prefer Headless command line mode to run migration tasks.
7. Must remind user to verify data row count consistency after migration completed.

<!--
1. 任何配置前，必须先区分关系引擎与时序引擎  
2. 必须完整校验时序迁移的所有必填参数  
3. 严格遵循参数互斥规则：自定义SQL不可与WHERE、时间过滤同时使用  
4. 配置提交前，必须校验数据类型映射合规性  
5. 配置校验不通过，禁止生成执行命令  
6. 生产环境优先使用Headless命令行运行迁移任务  
7. 迁移完成后，必须提醒用户校验数据行数一致性  
-->

## Error Handling

- Incomplete parameters: put forward clear supplementary requirements to user.
- Connection abnormal: check network, port, account password and IP whitelist.
- Time format error: unify standard format as yyyy-MM-dd HH:mm:ss.
- Task timeout and OOM: suggest adjusting split interval and JVM memory parameters.
- Data loss and inconsistency: check filter conditions and switch to UPSERT write mode.
- Type mismatch error: check data type mapping (refer to references/data-type-mapping.md) and adjust field types.

<!--
- 参数缺失：向用户明确提出补充要求  
- 连接异常：检查网络、端口、账号密码及IP白名单  
- 时间格式错误：统一为标准格式yyyy-MM-dd HH:mm:ss  
- 任务超时/内存溢出：建议调整分片间隔及JVM内存参数  
- 数据丢失/不一致：核查过滤条件，切换为UPSERT写入模式  
- 类型不匹配报错：核查数据类型映射（参考官方文件），调整字段类型
-->
