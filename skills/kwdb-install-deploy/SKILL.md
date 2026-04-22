---
name: kwdb-install-deploy
description: 当用户提问要安装、部署开务数据库 (kwdb,kaiwudb) 时触发，用来帮助用户完成 KaiwuDB 集群的脚本部署。包括配置文件修改、安装命令执行、集群初始化和状态检查等步骤。
---

# KWDB Install (开务数据库安装部署)

## Overview

该技能提供 KaiwuDB 数据库的脚本部署功能，适用于 Linux 环境下的裸机或容器部署。支持单副本和多副本集群部署，并提供完整的部署流程指导。

## Mandatory Rules (强制要求)

**必须严格遵守以下三条规则：**

### 1. 禁止猜测安装参数

**除非用户明确指定，否则不得自行猜测或假设任何安装参数并执行安装。**

- 所有配置参数（端口、IP、数据目录、安全模式等）必须向用户逐一确认
- 即使用户说"使用默认值"，也需要明确列出默认值并等待用户确认
- 安装包路径必须由用户明确提供，不得自行推测

### 2. 安装失败时必须读取日志

**当安装命令执行失败后，必须读取安装脚本同路径下 `log/` 目录中的日志文件，获取详细失败信息。**

日志文件路径：`/opt/kaiwudb/<安装包名>/log/` 或 `kaiwudb_install/log/`

```bash
# 安装失败后，首先读取日志
ls -la log/
cat log/install.log  # 或最新生成的日志文件
```

### 3. 失败汇报后退出，禁止随意重试

**安装失败后，必须：**
1. 向用户清晰展示从日志中获取的错误信息
2. 说明可能的原因
3. 退出安装流程，**不得自行重试**
4. 等待用户指示后再决定下一步操作

**例外**：只有当用户明确要求"重试"时，才可以再次执行安装命令。

## Prerequisites

### System Requirements

- **Hardware**:
  - Memory: At least 8 GB RAM (16 GB recommended)
  - CPU: At least 2 cores (4 cores recommended)
  - Disk: At least 50 GB available space (SSD recommended)
- **Operating System**:
  - CentOS 7/8
  - Ubuntu 18.04/20.04/22.04
- **Network**: All nodes must have network connectivity

### User Permissions

- SSH passwordless login configured between nodes
- User must be `root` or have `sudo` privileges
- For container deployment, non-root users must be in the `docker` group

## Deployment Steps

### Step 1: 确认部署模式

首先，我需要确认您需要部署的模式：

**询问内容**：
"请选择部署模式：单机部署 (single) 或 集群部署 (cluster)？"

### Step 1.1: 确认集群副本数 - 仅集群模式需要

如果选择集群部署，我需要进一步确认副本数：

**询问内容**：
"请选择集群部署类型：单副本集群 (single-replica) 或 多副本集群 (multi-replica)？"

### Step 2: 确认安装包位置

接下来，我需要向您确认 KaiwuDB 安装包的位置。安装包应该是一个以 `KaiwuDB` 为前缀的 `.tar.gz` 文件，例如：`KaiwuDB-1.0.0.tar.gz`。

**询问内容**：
"请提供 KaiwuDB 安装包的完整路径（包含文件名）。安装包应该是一个以 KaiwuDB 为前缀的 tar.gz 文件，例如 /path/to/KaiwuDB-1.0.0.tar.gz。"

**注意**：必须等待用户提供确切路径，不得自行猜测。

### Step 3: 验证安装包

确认安装包位置后，需要验证文件是否存在且格式正确：

```bash
# 检查安装包是否存在
if [ ! -f "$INSTALL_PACKAGE_PATH" ]; then
    echo "错误：安装包不存在，请检查路径是否正确"
    exit 1
fi

# 检查文件名格式
if [[ "$(basename $INSTALL_PACKAGE_PATH)" != KaiwuDB*.tar.gz ]]; then
    echo "错误：安装包文件名不正确。应该以 KaiwuDB 为前缀的 tar.gz 文件"
    exit 1
fi
```

### Step 4: 解压安装包并配置

```bash
# 创建安装目录
sudo mkdir -p /opt/kaiwudb

# 解压安装包
tar -xzf "$INSTALL_PACKAGE_PATH" -C /opt/kaiwudb

# 进入安装目录
cd /opt/kaiwudb/kaiwudb_install
```

### Step 5: 配置 deploy.cfg 文件

我将根据您选择的部署模式，向您逐步询问每一项配置内容，然后根据您的回答来修改 `deploy.cfg` 配置文件。

**强制要求**：除非用户主动说"全部默认"或明确指定了参数值，否则必须逐项确认。即使用户选择默认值，也需要展示默认值并等待确认。

#### 全局配置 (global) - 所有模式通用

1. **安全模式 (secure_mode)**:
   - 询问内容："请选择安全模式：insecure（非安全模式）、tls（TLS 安全模式，默认）、tlcp（TLCP 安全模式）"

2. **管理用户 (management_user)**:
   - 询问内容："请输入 KaiwuDB 管理用户名（默认：kaiwudb）"

3. **RESTful 端口 (rest_port)**:
   - 询问内容："请输入 KaiwuDB Web 服务端口（默认：8080）"

4. **KaiwuDB 服务端口 (kaiwudb_port)**:
   - 询问内容："请输入 KaiwuDB 服务端口（默认：26257）"

5. **BRPC 端口 (brpc_port)**:
   - 询问内容："请输入 KaiwuDB 时序引擎通信端口（默认：27257）"

6. **数据目录 (data_root)**:
   - 询问内容："请输入 KaiwuDB 数据存储目录（默认：/var/lib/kaiwudb）"

7. **CPU 资源占用 (cpu)**:
   - 询问内容："请输入 KaiwuDB 服务占用 CPU 资源的比例（0-1，默认无限制）"

#### 本地节点配置 (local) - 所有模式通用

8. **本地节点 IP 地址 (local_node_ip)**:
   - 询问内容："请输入本地节点的 IP 地址（用于对外提供服务）"
   - **注意**：此参数无默认值，必须由用户提供

#### 集群配置 (cluster) - 仅集群模式需要

9. **集群其他节点 IP 地址 (cluster_node_ips)**:
   - 询问内容："请输入集群其他节点的 IP 地址（多个地址用逗号分隔）"

10. **SSH 端口 (ssh_port)**:
    - 询问内容："请输入远程节点的 SSH 服务端口（默认：22）"

11. **SSH 用户名 (ssh_user)**:
    - 询问内容："请输入远程节点的 SSH 登录用户名"

根据您的回答，我会自动生成对应的 `deploy.cfg` 配置文件。单机部署时会自动省略集群配置部分。

### Step 6: 执行安装命令

根据您的选择，执行相应的安装命令：

**单机部署**：
```bash
./deploy.sh install --single
```

**单副本集群部署**：
```bash
./deploy.sh install --single-replica
```

**多副本集群部署**：
```bash
./deploy.sh install --multi-replica
```

**重要**：执行前必须向用户展示所有配置参数，等待用户确认后方可执行。

### Step 7: 确认安装信息

检查配置无误后输入 `Y` 或 `y`，如需返回修改配置文件，输入 `N` 或 `n`。

```shell
================= KaiwuDB Basic Info =================
Deploy Mode: bare-metal
Management User: kaiwudb
Start Mode: single
RESTful Port: 8080
KaiwuDB Port: 26257
BRPC Port: 27257
Data Root: /var/lib/kaiwudb
Secure Mode: tls
CPU Usage Limit: 1
Local Node Address: 192.168.122.221
=========================================================
Please confirm the installation information above(Y/n):
```

### Step 8: 处理安装失败

**如果安装命令执行失败（返回非零退出码），必须执行以下操作：**

```bash
# 1. 进入日志目录
cd log/

# 2. 列出日志文件
ls -la

# 3. 读取最新的日志文件（通常是 install.log 或带时间戳的文件）
cat install.log
# 或者
tail -100 <最新日志文件>
```

**向用户汇报失败信息：**

1. 清晰展示从日志中提取的错误信息
2. 说明可能的原因（参考 references/troubleshooting.md）
3. **退出安装流程，不得自行重试**
4. 等待用户进一步指示

示例汇报格式：
```
安装失败！

错误信息（来自日志）：
[从 log/install.log 中提取的具体错误内容]

可能原因：
- [根据错误信息分析的可能原因]

请检查上述问题后，告诉我是否需要重试或有其他指示。
```

### Step 9: 初始化并启动集群 - 仅集群模式需要

安装成功后，执行：

```bash
./deploy.sh cluster -i
# 或者
./deploy.sh cluster --init
```

### Step 10: 查看状态

**查看服务状态**：
```bash
systemctl status kaiwudb
```

**查看集群状态（仅集群模式）**：
```bash
./deploy.sh cluster -s
# 或者
./deploy.sh cluster --status
# 或者使用便捷脚本
kw-status
```

### Step 11: 配置开机自启动（可选）

```bash
systemctl enable kaiwudb
```

## Resources

### references/
包含 KaiwuDB 相关文档：

- `installation_guide.md` - 详细的安装指南
- `troubleshooting.md` - 常见问题和解决方案

### assets/
包含 KaiwuDB 配置文件模板和资源：

- `deploy.cfg` - 部署配置文件模板
