# 非官方 TikTok Python API

这是一个针对 TikTok.com 的非官方 Python API 封装。使用此 API，你可以获取热门内容、抓取特定用户信息等更多数据。

[![DOI](https://zenodo.org/badge/188710490.svg)](https://zenodo.org/badge/latestdoi/188710490) [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/davidteather/) [![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/c/DavidTeather) [![Discord](https://img.shields.io/discord/736724457258745936?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/Xpc6xG4)

本 API 旨在从 TikTok 上“获取数据”。它不能用于代表用户在 TikTok 上“发布或上传”内容。它不支持任何需要用户身份验证的路由；如果你无法在“未登录状态”下通过浏览器完成的操作，这个库也无法完成。

## 赞助商

以下赞助商为展示位付费，或为我个人的联盟推广链接（可能会获得佣金）。除此之外，我与他们没有任何其他关联。TikTokAPI 包将始终保持免费、开源。

<div align="center">
    <a href="https://tikapi.io/?ref=davidteather" target="_blank">
        <img src="https://raw.githubusercontent.com/davidteather/TikTok-Api/main/imgs/tikapi.png" width="100" alt="TikApi">
        <div>
            <b>TikAPI</b> 是一项付费的 TikTok API 服务，提供开箱即用的完整解决方案，让开发更轻松——已被 500+ 公司信任。
        </div>
    </a>
    <br>
    <a href="https://www.ensembledata.com/?utm_source=github&utm_medium=githubpage&utm_campaign=david_thea_github&utm_id=david_thea_github" target="_blank">
        <img src="https://raw.githubusercontent.com/davidteather/TikTok-Api/main/imgs/EnsembleData.png" width="100" alt="Ensemble Data">
        <b></b>
        <div>
         <b>EnsembleData</b> 是领先的 API 提供商，支持抓取 TikTok、Instagram、YouTube 等平台。<br> 被主流的网红营销与社交媒体监测平台所信任。
        </div>
    </a>
    <br>
    <a href="https://tikhub.io/?utm_source=github&utm_medium=readme&utm_campaign=tiktok_api&ref=github_davidteather_tiktokapi" target="_blank">
        <img src="https://raw.githubusercontent.com/davidteather/TikTok-Api/main/imgs/tikhub.png" width="100" alt="TikHub API">
        <b></b>
        <div>
         <b>TikHub API</b> 提供 700+ 个端点，覆盖 14+ 个社交平台的数据抓取与分析，<br>包括视频、用户、评论、店铺、商品与趋势等——一站式搞定。
        </div>
    </a>
    <br>
    <a href="https://www.webshare.io/?referral_code=3x5812idzzzp" target="_blank">
        <img src="https://raw.githubusercontent.com/davidteather/TikTok-Api/main/imgs/webshare.png" width="100" alt="Webshare Proxies">
        <b></b>
        <div>
         <b>高性价比、可靠的代理：</b> 用快速稳定的代理为你的爬虫加速。立即试用 10 个免费数据中心代理！
        </div>
    </a>
</div>

## 目录

- [文档](#documentation)
- [快速开始](#getting-started)
  - [如何支持本项目](#how-to-support-the-project)
  - [安装](#installing)
  - [常见问题](#common-issues)
- [快速上手示例](#quick-start-guide)
  - [示例代码库](https://github.com/davidteather/TikTok-Api/tree/main/examples)

<a name="documentation"></a>
## 文档

完整文档见：[文档站点](https://davidteather.github.io/TikTok-Api)

<a name="getting-started"></a>
## 快速开始

按照以下步骤开始使用本 API。

注意：如果你想系统学习网页爬虫，请查看我开源免费的课程：[Everything Web Scraping](https://github.com/davidteather/everything-web-scraping)

<a name="how-to-support-the-project"></a>
### 如何支持本项目

- 给仓库点个 Star 😎
- 考虑在 GitHub 上[赞助](https://github.com/sponsors/davidteather)我
- 给我发邮件，或在 [LinkedIn](https://www.linkedin.com/in/davidteather/) 上告诉我你在用这个 API 做什么——我很乐意听到你的故事
- 为 issue 提交 PR :)

<a name="installing"></a>
### 安装

注意：需要 Python 3.9 及以上版本

如果遇到问题，请先查看仓库里的已关闭 issue；如果你发现久远的 issue 与现在的问题相同，也可以新开一个 issue。该代码库会受到 TikTok 更新的影响，有时需要一些时间来适配。

```sh
pip install TikTokApi
python -m playwright install
```

如果你更喜欢视频讲解，关于安装与设置可以看这段 [YouTube 视频](https://www.youtube.com/watch?v=-uCt1x8kINQ)（版本可能略旧，但安装步骤相同）。

如果你想快速了解如何在 Python 中监听 [TikTok Live](https://www.youtube.com/watch?v=307ijmA3_lc) 事件，也可以看这段短视频。

#### Docker 安装

将本仓库克隆到本地（或只拷贝 Dockerfile，因为它会从 pip 安装 TikTokApi），然后运行以下命令：

```sh
docker pull mcr.microsoft.com/playwright:focal
docker build . -t tiktokapi:latest
docker run -v TikTokApi --rm tiktokapi:latest python3 your_script.py
```

注意：以上示例假设你的脚本名为 your_script.py，且位于仓库根目录。

<a name="common-issues"></a>
### 常见问题

- 空响应异常（EmptyResponseException）——表示 TikTok 拦截了请求并检测到你是机器人。这可能来自你的环境设置或库本身
  - 你可能需要代理才能稳定抓取 TikTok。我做了一节[代理课程](https://github.com/davidteather/everything-web-scraping/tree/main/002-proxies)，讲解住宅代理与数据中心代理的区别等内容

- “Browser has no attribute …”——请确认已执行 `python3 -m playwright install`。若问题仍在，请参考 [playwright-python](https://github.com/microsoft/playwright-python) 的快速上手指南

- “API 方法返回协程（Coroutine）”——库中很多方法是异步的，请确保在你的程序中使用 `await` 正确调用

<a name="quick-start-guide"></a>
## 快速上手示例

下面是一个示例，用于获取 TikTok 上最新的热门视频。更多示例见 [examples](https://github.com/davidteather/TikTok-Api/tree/main/examples) 目录。

注意：如果你想学习通过逆向工程进行网页抓取，请查看我开源免费的课程：[Web Scraping with Reverse Engineering](https://github.com/davidteather/web-scraping-with-reverse-engineering)

```py
from TikTokApi import TikTokApi
import asyncio
import os

ms_token = os.environ.get("ms_token", None) # 从 tiktok.com 的浏览器 Cookie 中获取你的 ms_token

async def trending_videos():
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"))
        async for video in api.trending.videos(count=30):
            print(video)
            print(video.as_dict)

if __name__ == "__main__":
    asyncio.run(trending_videos())
```

在仓库根目录下，使用 `-m` 方式可直接运行示例脚本：

```sh
python -m examples.trending_example
```

你可以通过 `.as_dict` 访问对象创建时的完整数据字典。对于视频对象，可能类似于[这个示例](https://gist.github.com/davidteather/7c30780bbc30772ba11ec9e0b909e99d)。由于 TikTok 会不定期调整数据结构，建议在使用时先了解字典结构。
