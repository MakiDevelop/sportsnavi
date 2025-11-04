# 🔌 端口配置說明

## 📋 端口映射

為了避免與 **reas** 專案的端口衝突，Sportsnavi 使用不同的端口：

### 當前配置

| 服務 | 容器內部端口 | 主機端口 | 用途 |
|------|------------|---------|------|
| **PostgreSQL** | 5432 | **5433** | 資料庫連接 |
| **Web API** | 8000 | **8001** | FastAPI 服務 |

### 對比 reas 專案

| 專案 | PostgreSQL | Web API |
|------|-----------|---------|
| **reas** | 5432 | 8000 |
| **sportsnavi** | **5433** | **8001** |

---

## 🔗 連接方式

### 1. **從容器內部連接資料庫**（例如：爬蟲、API）

容器內部使用 Docker 網絡，使用**容器名稱**和**內部端口**：

```python
# 正確 ✅
DATABASE_URL = "postgresql://user:password@db:5432/sportsnavidb"
```

**說明**：
- `db` 是容器名稱（在 docker-compose.yml 中定義）
- `5432` 是容器內部的 PostgreSQL 端口

---

### 2. **從主機連接資料庫**（例如：DBeaver、psql）

從主機連接使用 **localhost** 和**映射後的端口**：

```bash
# 使用 psql 連接
psql -h localhost -p 5433 -U user -d sportsnavidb

# 使用 DBeaver 或其他 GUI 工具
Host: localhost
Port: 5433
Database: sportsnavidb
User: user
Password: sportsnavi_password_2024
```

---

### 3. **訪問 Web UI**

```bash
# Sportsnavi
http://localhost:8001

# reas（參考）
http://localhost:8000
```

---

## ⚙️ 如何修改端口

如果需要更改端口，只需修改 `docker-compose.yml`：

```yaml
services:
  db:
    ports:
      - "新端口:5432"  # 例如：5434:5432

  web:
    ports:
      - "新端口:8000"  # 例如：8002:8000
```

**注意**：
- 冒號**左邊**是主機端口（外部訪問）
- 冒號**右邊**是容器內部端口（不要修改）

---

## 🧪 測試連接

### 測試資料庫連接

```bash
# 從主機測試
docker exec -it sportsnavi-db psql -U user -d sportsnavidb -c "SELECT version();"

# 或使用端口 5433
psql -h localhost -p 5433 -U user -d sportsnavidb -c "SELECT version();"
```

### 測試 Web API

```bash
# 測試 API 是否運行
curl http://localhost:8001/

# 或在瀏覽器打開
http://localhost:8001/docs  # FastAPI 自動文檔
```

---

## 🔧 常見問題

### Q1: 為什麼容器內部仍然使用 5432？

**答**：Docker 容器內部有自己的網絡空間，不受主機端口影響。`5432` 是 PostgreSQL 的標準端口，保持不變可以確保：
- 標準工具無需額外配置
- 容器間通信使用標準端口
- 遷移和部署更簡單

### Q2: 如果我忘記端口是多少怎麼辦？

**答**：使用以下指令查看：

```bash
docker ps

# 輸出範例：
# CONTAINER ID   PORTS                    NAMES
# abc123         0.0.0.0:5433->5432/tcp   sportsnavi-db
# def456         0.0.0.0:8001->8000/tcp   sportsnavi-web
```

### Q3: 可以同時運行 reas 和 sportsnavi 嗎？

**答**：可以！因為使用了不同的端口：
- reas: 5432, 8000
- sportsnavi: 5433, 8001

兩個專案可以同時運行，互不干擾。

---

## 📝 快速參考

```bash
# Sportsnavi
資料庫（主機）: localhost:5433
Web UI:        localhost:8001
容器名稱:       sportsnavi-db, sportsnavi-web

# reas（參考）
資料庫（主機）: localhost:5432
Web UI:        localhost:8000
```

---

**✅ 端口配置完成！現在可以同時運行兩個專案了。**
