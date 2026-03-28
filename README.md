# Agent Paper Weekly Digest

这是一个可直接放到 GitHub 的项目骨架，用于**每天早上 8 点**自动抓取最近一周的「具身智能（Embodied Intelligence）」热点论文，并通过邮件发送到 `510948205@qq.com`。

> 说明：当前环境无法直连 gitee（`https://gitee.com/prepat/agent-paper.git` 返回 403），因此这里提供了一个可运行、可扩展的优化版本实现。

## 功能

- 从 arXiv API 按关键词抓取论文。
- 自动筛选最近 7 天发布的论文。
- 生成邮件摘要（标题、作者、发布时间、链接、摘要）。
- 支持本地定时与 GitHub Actions 定时发送。

## 配置

通过环境变量配置邮件参数：

```env
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USER=你的QQ邮箱
SMTP_PASSWORD=你的SMTP授权码
MAIL_FROM=你的QQ邮箱
MAIL_TO=510948205@qq.com
MAX_PAPERS=20
DIGEST_DAYS=7
```

> QQ 邮箱需开启 SMTP 服务并使用授权码（不是登录密码）。

## 运行

### 1) 先执行一次预览（不发邮件）

```bash
python paper_digest.py --preview --days 7
```

### 2) 执行一次真实发送

```bash
python paper_digest.py --once --days 7
```

### 3) 本地每天 8 点自动运行

```bash
python scheduler.py
```

## GitHub Actions（推荐）

仓库已包含 `.github/workflows/daily_digest.yml`，默认在 **UTC 00:00** 运行（对应北京时间 08:00）。

你只需要在 GitHub 仓库 Settings -> Secrets and variables -> Actions 中配置：

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `MAIL_FROM`
- `MAIL_TO`
- `MAX_PAPERS`（可选）

## 如何创建 GitHub 项目并推送

```bash
git init
git add .
git commit -m "feat: add embodied intelligence weekly paper email digest"
git branch -M main
git remote add origin git@github.com:<your-username>/agent-paper.git
git push -u origin main
```

## 在哪可以获得完整代码

你可以通过以下任一方式拿到完整代码：

1. **GitHub 仓库页面直接下载 ZIP**
   - 打开仓库：`https://github.com/prepat2022/agent-paper`
   - 点击 `Code` -> `Download ZIP`

2. **使用 Git 克隆（推荐）**

```bash
git clone https://github.com/prepat2022/agent-paper.git
cd agent-paper
```

3. **查看单文件源码**
   - 论文抓取与发信主逻辑：`paper_digest.py`
   - 本地定时任务：`scheduler.py`
   - 定时工作流：`.github/workflows/daily_digest.yml`

## 在哪可以 push 到 GitHub

你需要在**有外网访问 GitHub 的机器**上执行 `git push`（本地电脑、云服务器、或 GitHub Codespaces 都可以）。

### 方式 A：HTTPS 推送

```bash
git remote set-url origin https://github.com/prepat2022/agent-paper.git
git push -u origin work:main
```

### 方式 B：SSH 推送

```bash
git remote set-url origin git@github.com:prepat2022/agent-paper.git
git push -u origin work:main
```

### 如果你遇到 `CONNECT tunnel failed, response 403`

- 说明当前环境网络代理限制了 GitHub 访问。
- 解决方式：换到可访问 GitHub 的网络环境再执行 push，或配置正确的代理后再推送。

## 可优化方向

- 增加多数据源（OpenReview、Semantic Scholar）。
- 引入大模型对论文做自动中文总结。
- 按「感知/规划/控制/多模态」自动分组。
- 将发送内容同步到飞书/企业微信。
