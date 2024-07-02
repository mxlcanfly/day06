import requests
import re

def get_old_view_count(video_url):
    for i in range(5):
        try:
            res = requests.get(
                url=video_url,
                headers={
                    'user-agent':'Mozilla / 5.0(WindowsNT10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 126.0.0.0Safari / 537.36Edg / 126.0.0.0',
                    'referer':'https://w.yangshipin.cn/'
                }
            )
            match_object = re.findall(r'"subtitle":"(.+)次观看",',res.text)
            if not match_object:
                return True,0
            return True, match_object[0]
        except Exception as e:
            pass
    return False, 0
if __name__ == '__main__':
    count = get_old_view_count("https://w.yangshipin.cn/video?type=0&vid=y000088hru8")
    print(count)