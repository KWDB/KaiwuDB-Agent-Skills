# KaiwuDB 常见问题与解决方案

## 安装问题

### 1. 环境检查失败

**问题**：脚本提示环境检查失败

**解决方案**：
- 检查系统要求是否满足（内存、磁盘空间）
- 确保运行脚本的用户有足够权限
- 检查网络连接是否正常

### 2. 依赖安装失败

**问题**：依赖安装过程中出现错误

**解决方案**：
- 检查系统包管理器是否正常（yum/apt）
- 尝试手动更新包管理器：
  - CentOS: `sudo yum update -y`
  - Ubuntu: `sudo apt-get update -y`
- 如果网络慢，考虑使用国内镜像源

### 3. 下载安装包失败

**问题**：无法下载 KaiwuDB 安装包

**解决方案**：
- 检查网络连接
- 尝试手动下载安装包并放在 scripts/ 目录下
- 联系技术支持获取下载链接

## 运行问题

### 1. 数据库无法启动

**问题**：执行启动命令后没有响应

**解决方案**：
- 检查数据目录权限：`ls -ld /var/lib/kwdb`
- 查看日志文件：`cat /var/log/kwdb/kwdb.log`
- 检查配置文件是否正确

### 2. 无法连接数据库

**问题**：使用 psql 命令无法连接到数据库

**解决方案**：
- 检查 kwdb 进程是否正在运行：`ps aux | grep kwdb`
- 检查防火墙是否允许端口 5432 访问
- 检查 listen_addresses 配置是否为 '*'
- 检查 pg_hba.conf 文件是否允许连接

### 3. 数据库运行缓慢

**问题**：查询响应时间长

**解决方案**：
- 检查系统资源使用情况：`top`
- 查看慢查询日志：`/var/log/kwdb/slow_query.log`
- 优化查询语句
- 调整配置文件参数

## 性能问题

### 1. 内存使用过高

**问题**：数据库进程占用过多内存

**解决方案**：
- 调整 shared_buffers 参数
- 检查是否有内存泄漏
- 增加系统内存

### 2. 磁盘I/O过高

**问题**：磁盘写入速度慢

**解决方案**：
- 检查磁盘空间是否充足
- 考虑使用 SSD 磁盘
- 调整 checkpoint 相关参数
- 优化查询减少磁盘I/O

## 备份和恢复

### 1. 备份数据库

```bash
/opt/kwdb/current/bin/pg_dump -h localhost -p 5432 -U $USER -d kwdb_db > backup.sql
```

### 2. 恢复数据库

```bash
/opt/kwdb/current/bin/psql -h localhost -p 5432 -U $USER -d kwdb_db < backup.sql
```

## 联系支持

如果您遇到无法解决的问题，请联系技术支持：
- 邮箱：support@kaiwudb.com
- 电话：400-xxx-xxxx