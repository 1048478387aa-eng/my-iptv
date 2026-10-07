
import concurrent.futures
import requests

def fetch_raw_sources():
    channels = []
    # 这里替换为 3 个目前全网最活跃、包含港澳台海外频道的公开源接口
    target_urls = [
        "https://githubusercontent.com",
        "https://githubusercontent.com",
        "https://githubusercontent.com"
    ]
    
    target_keywords = ["香港", "澳门", "台湾", "TVB", "翡翠", "明珠", "凤凰", "东森", "三立", "TVBS", "NOW", "HBO", "BBC", "EARTH", "DISCOVERY", "国家地理", "CHHC", "凤凰卫视"]
    
    for url in target_urls:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                lines = res.text.strip().split('\n')
                
                # 兼容格式1：TXT 格式
                if not any(l.startswith("#EXTM3U") for l in lines[:3]):
                    for line in lines:
                        if ',' in line and not line.startswith("#"):
                            name, url_str = line.split(',', 1)
                            name_upper = name.upper().strip()
                            if any(k in name_upper for k in target_keywords):
                                channels.append({"name": name.strip(), "url": url_str.strip()})
                
                # 兼容格式2：M3U 格式
                else:
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
            print(f"请求源出错: {url}, 错误: {e}")
            continue
            
    seen = set()
    unique_channels = []
    for ch in channels:
        if ch["url"] not in seen:
            seen.add(ch["url"])
            unique_channels.append(ch)
    return unique_channels

def verify_stream(channel):
    name = channel["name"]
    url = channel["url"]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        with requests.get(url, headers=headers, timeout=3, stream=True) as response:
            if response.status_code == 200:
                print(f"[可用港澳台] {name}")
                return channel
    except:
        pass
    return None

def main():
    channels = fetch_raw_sources()
    print(f"共抓取到候选港澳台频道 {len(channels)} 个，开始在线测速...")
    
    valid_channels = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(verify_stream, channels)
        for res in results:
            if res:
                valid_channels.append(res)
                
    m3u_filename = "my_live_list.m3u"
    with open(m3u_filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch in valid_channels:
            f.write(f'#EXTINF:-1 tvg-name="{ch["name"]}" group-title="港澳台海外",{ch["name"]}\n{ch["url"]}\n')
    print(f"同步完成！共保存可用频道 {len(valid_channels)} 个。")

if __name__ == "__main__":
    main()
