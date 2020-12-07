# VersionStatistic

(1)列出github开源软件的当前版本及历史版本
(2)列出dockerhub开源镜像的当前版本及历史版本

## Build Setup

```bash
# install dependencies
npm install

# serve with hot reload at localhost:8080
npm run dev

# build for production with minification
npm run build

# build for production and view the bundle analyzer report
npm run build --report

```

## 生成数据

# 使用脚本生成数据

python3 scripts/check.py

# 更新软件/镜像列表
- `scripts/source.json` 记录要搜集版本的开源软件/镜像列表
- `static/data/data.json` 存放搜集到的数据


