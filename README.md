# 微信小程序与公众号后台服务

这是一个为微信小程序和公众号提供后台服务的项目，基于FastAPI框架开发。

## 项目结构

```
penxxy-server/
├── app/                    # 应用程序主目录
│   ├── api/                # API路由层
│   │   ├── v1/             # API版本1
│   │   │   ├── endpoints/  # 各个API端点
│   │   │   └── router.py   # API路由注册
│   │   └── deps.py         # API依赖项
│   ├── core/               # 核心配置
│   │   ├── config.py       # 配置管理
│   │   ├── security.py     # 安全相关
│   │   └── events.py       # 应用事件处理
│   ├── db/                 # 数据库相关
│   │   ├── base.py         # 数据库基础设置
│   │   └── session.py      # 数据库会话
│   ├── models/             # 数据库模型
│   ├── schemas/            # 数据验证/响应模型
│   ├── services/           # 业务逻辑层
│   ├── utils/              # 通用工具函数
│   │   └── wechat/         # 微信相关工具
│   └── main.py             # 应用入口
├── alembic/                # 数据库迁移
├── static/                 # 静态文件
├── templates/              # 模板文件
├── tests/                  # 测试用例
├── .env                    # 环境变量
├── .gitignore              # Git忽略规则
├── requirements.txt        # 项目依赖
└── README.md               # 项目说明
```

## 功能模块

1. 用户认证与管理
2. 微信小程序API
3. 微信公众号API
4. 微信支付集成
5. 数据统计与分析
6. 后台管理功能

## 如何启动

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 设置环境变量
```bash
# 复制.env.example为.env并修改相应配置
cp .env.example .env
```

3. 运行服务
```bash
uvicorn app.main:app --reload
```

4. 访问API文档
```
http://127.0.0.1:8000/docs
```

## 开发指南

- 遵循RESTful API设计规范
- 使用Pydantic进行数据验证
- 使用SQLAlchemy进行ORM操作
- 利用FastAPI依赖注入系统管理服务和依赖 