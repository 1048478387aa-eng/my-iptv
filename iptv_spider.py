
import requests

def fetch_raw_sources():
    channels = []
    # 使用全网最稳定、必定有港澳台频道的公开接口
    target_urls = [
        "https://githubusercontent.com",
        "https://githubusercontent.com"
    ]
    
    # 筛选包含这些关键词的港澳台和海外大台
    target_keywords = ["香港", "澳门", "台湾", "TVB", "翡翠", "明珠", "凤凰", "东森", "三立", "TVBS", "NOW", "HBO", "BBC", "DISCOVERY", "国家地理", "凤凰卫视"]
    
    for url in target_urls:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                lines = res.text.strip().split('\n')
                current_name = ""
                for line in lines:
                    line = line.strip()
                    if line.startswith("#EXTINF"):
                        if ',' in line:
                            current_name = line.split(',', 1)[1].strip()
                    elif line.startswith("http") and current_name:
                        name_upper = current_name.upper()
                        if any(k in name_upper for k in target_keywords):
                            channels.append({"name": current_name, "url": line})
                        current_name = ""
        except Exception as e:
            print(f"请求失败: {url}, 错误: {e}")
            continue
            
    # 去除重复的链接
    seen = set()
    unique_channels = []
    for ch in channels:
        if ch["url"] not in seen:
            seen.add(ch["url"])
            unique_channels.append(ch)
    return unique_channels

def main():
    print("开始抓取港澳台频道...")
    valid_channels = fetch_raw_sources()
    print(f"共抓取到港澳台频道 {len(valid_channels)} 个，正在直接写入文件...")
    
    m3u_filename = "my_live_list.m3u"
    with open(m3u_filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch in valid_channels:
            f.write(f'#EXTINF:-1 tvg-name="{ch["name"]}" group-title="港澳台海外",{ch["name"]}\n{ch["url"]}\n')
    print("保存完成！")

if __name__ == "__main__":
    main()
