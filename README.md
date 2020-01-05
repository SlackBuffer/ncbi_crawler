# A simple ncbi crawler
It's a simple python ncbi crawler that, given the key word, helps to collect information of research articles including title, journal name, impact factor, cited number, abstract, download link and publication date. The result is saved as a `.xlsx` file.
## Getting Started
### Prerequisites
- Python 3.x
- Chrome explorer
- Install Python3 modules
	
    ```bash
    pip3 install selenium bs4 pandas
    ```

- Download [selenium driver](https://selenium-python.readthedocs.io/installation.html#drivers)
### Usage

```bash
python3 ncbi_crawler.py
```

This crawler is single-process. Additionally, after crawling one item, a random sleep time (1-3s) is added to avoid being banned by the ncbi server. So if you crawl for 100 items, an execution time of 4 minutes is to be expected.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<!-- 
- 计算密集型，用进程；取决于网速，用 event loop
- https://chrome.google.com/webstore/detail/chrome-extension-source-v/jifpbeccnghkjeaalbbjmodiffmgedin?utm_source=chrome-ntp-icon
- http://crxdown.com/
- 标题 影响因子 被引次数 发表年月 期刊名 摘要 页面链接 下载链接 
-->