# KaiwuDB 脚本部署指南

## 前提条件

### 系统要求

- 所有待部署节点的硬件、操作系统和软件依赖满足安装部署要求。
- **网络设置**:
  - 各节点间网络联通。
  - 节点所在机器位于同一机房内。
  - 物理机器间网络延迟不高于 50 ms。
  - 各节点时钟相差不大于 500 ms。
  - 各节点已预留 KaiwuDB 服务所需端口。
- 已获取对应系统版本的 KaiwuDB 裸机或容器安装包。

### 用户权限要求

- 已配置当前节点与集群内其他节点的 SSH 免密登录。
- 安装用户为 `root` 用户或者拥有 `sudo` 权限的普通用户。
- 使用容器安装包部署时，如果安装用户为非 `root` 用户，需要通过 `sudo usermod -aG docker $USER` 命令将用户添加到 `docker` 组。

## 部署步骤

### Step 1: 确认部署模式

首先，确认需要部署的模式：

**询问内容**：
"请选择部署模式：单机部署(single) 或 集群部署(cluster)？"

### Step 1.1: 确认集群副本数 - 仅集群模式需要

如果选择集群部署，我需要进一步确认副本数：

**询问内容**：
"请选择集群部署类型：单副本集群(single-replica) 或 多副本集群(multi-replica)？"

### Step 2: 确认安装包位置

提供安装包的完整路径，包括文件名，例如：
```
/path/to/KaiwuDB-1.0.0.tar.gz
```

### Step 3: 解压安装包

```bash
# 创建安装目录
sudo mkdir -p /opt/kaiwudb

# 解压安装包
tar -xzf "$INSTALL_PACKAGE_PATH" -C /opt/kaiwudb

# 进入安装目录
cd /opt/kaiwudb/$(basename "$INSTALL_PACKAGE_PATH" .tar.gz)
```

### Step 4: 配置 deploy.cfg 文件

我将根据您选择的部署模式，向您逐步询问每一项配置内容，然后根据您的回答来修改 `deploy.cfg` 配置文件。

#### 全局配置 (global) - 所有模式通用

1. **安全模式 (secure_mode)**:
   - 选择安全模式：insecure（非安全模式）、tls（TLS安全模式，默认）、tlcp（TLCP安全模式）

2. **管理用户 (management_user)**:
   - 输入KaiwuDB管理用户名（默认：kaiwudb）

3. **RESTful端口 (rest_port)**:
   - 输入KaiwuDB Web服务端口（默认：8080）

4. **KaiwuDB服务端口 (kaiwudb_port)**:
   - 输入KaiwuDB服务端口（默认：26257）

5. **BRPC端口 (brpc_port)**:
   - 输入KaiwuDB时序引擎通信端口（默认：27257）

6. **数据目录 (data_root)**:
   - 输入KaiwuDB数据存储目录（默认：/var/lib/kaiwudb）

7. **CPU资源占用 (cpu)**:
   - 输入KaiwuDB服务占用CPU资源的比例（0-1，默认无限制）

#### 本地节点配置 (local) - 所有模式通用

8. **本地节点IP地址 (local_node_ip)**:
   - 输入本地节点的IP地址（用于对外提供服务）

#### 集群配置 (cluster) - 仅集群模式需要

9. **集群其他节点IP地址 (cluster_node_ips)**:
   - 输入集群其他节点的IP地址（多个地址用逗号分隔）

10. **SSH端口 (ssh_port)**:
    - 输入远程节点的SSH服务端口（默认：22）

11. **SSH用户名 (ssh_user)**:
    - 输入远程节点的SSH登录用户名

根据您的回答，我会自动生成对应的 `deploy.cfg` 配置文件。单机部署时会自动省略集群配置部分。

### Step 5: 执行安装命令

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

### Step 6: 确认安装信息

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

### Step 7: 初始化并启动集群 - 仅集群模式需要

```bash
./deploy.sh cluster -i
# 或者
./deploy.sh cluster --init
```

### Step 8: 查看状态

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

### Step 9: 配置开机自启动（可选）

```bash
systemctl enable kaiwudb
```

## 状态检查说明

`kw-status` 命令返回的字段说明：

| 字段         | 描述 |
|--------------|------|
| `id`         | 节点 ID |
| `address`    | 节点地址 |
| `sql_address`| SQL 地址 |
| `build`      | KaiwuDB 版本 |
| `started_at` | 启动时间 |
| `updated_at` | 更新时间 |
| `is_available`/`is_live` | 节点状态，均为 `true` 表示正常 |

## 部署模式

### 裸机部署

使用 `KaiwuDB-baremetal-*.tar.gz` 安装包进行部署。

### 容器部署

使用 `KaiwuDB-container-*.tar.gz` 安装包进行部署，需确保 Docker 已安装并配置好。
