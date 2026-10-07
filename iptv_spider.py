import subprocess
import concurrent.futures
import requests

def fetch_raw_sources():
    channels = []
    target_urls = [
        "https://githubusercontent.com",
        "https://githubusercontent.com",
        "https://githubusercontent.com"
    ]
    for url in target_urls:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                for line in res.text.strip().split('\n'):
                    if ',' in line and not line.startswith("#"):
                        name, url_str = line.split(',', 1)
                        name_upper = name.upper().strip()
                        target_keywords = ["香港", "澳门", "台湾", "TVB", "翡翠", "明珠", "凤凰", "东森", "三立", "TVBS", "NOW", "HBO", "BBC", "EARTH", "DISCOVERY", "国家地理"]
                        if any(k in name_upper for k in target_keywords):
                            channels.append({"name": name.strip(), "url": url_str.strip()})
        except:
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
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', '-timeout', '3000000', url]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=4)
        if result.returncode == 0:
            print(f"[可用港澳台] {name}")
            return channel
    except:
        pass
    return None

def main():
    channels = fetch_raw_sources()
    valid_channels = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(verify_stream, channels)
        for res in results:
            if res:
                valid_channels.append(res)
    m3u_filename = "my_live_list.m3u"
    with open(m3u_filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch in valid_channels:
            f.write(f'#EXTINF:-1 tvg-name="{ch["name"]}" group-title="港澳台海外",{ch["name"]}\n{ch["url"]}\n')

if __name__ == "__main__":
    main()
