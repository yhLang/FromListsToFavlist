import requests


import re
import time
from urllib.parse import parse_qs, urlparse


class FromListsToFavlist:
    def __init__(self, cookies):
        """
        初始化
        :param cookies: B站登录后的cookies字符串
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com',
        })

        # 解析cookies字符串并设置到session
        if cookies:
            cookie_dict = {}
            for item in cookies.split(';'):
                if '=' in item:
                    key, value = item.strip().split('=', 1)
                    cookie_dict[key] = value
            self.session.cookies.update(cookie_dict)

    def extract_season_info(self, collection_url):
        """
        从合集URL中提取用户ID和合集ID
        """
        # 解析URL: https://space.bilibili.com/627432065/lists/3836754?type=season
        # 或: https://space.bilibili.com/627432065/channel/seriesdetail?sid=3836754

        # 方法1: lists格式
        pattern1 = r'space\.bilibili\.com/(\d+)/lists/(\d+)'
        match1 = re.search(pattern1, collection_url)
        if match1:
            uid = match1.group(1)
            season_id = match1.group(2)
            return uid, season_id

        # 方法2: channel/seriesdetail格式
        pattern2 = r'space\.bilibili\.com/(\d+)/channel/seriesdetail.*?sid=(\d+)'
        match2 = re.search(pattern2, collection_url)
        if match2:
            uid = match2.group(1)
            season_id = match2.group(2)
            return uid, season_id

        # 方法3: 从URL参数中提取
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(collection_url)
        if 'space.bilibili.com' in parsed.netloc:
            # 提取用户ID
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) >= 1 and path_parts[0].isdigit():
                uid = path_parts[0]

                # 提取合集ID
                if len(path_parts) >= 3 and path_parts[1] == 'lists' and path_parts[2].isdigit():
                    season_id = path_parts[2]
                    return uid, season_id

                # 从查询参数中提取
                query_params = parse_qs(parsed.query)
                if 'sid' in query_params:
                    season_id = query_params['sid'][0]
                    return uid, season_id

        raise ValueError("无法解析合集URL，请检查URL格式。支持格式：\n"
                        "1. https://space.bilibili.com/用户ID/lists/合集ID?type=season\n"
                        "2. https://space.bilibili.com/用户ID/channel/seriesdetail?sid=合集ID")

    def extract_fav_info(self, fav_url):
        """
        从收藏夹URL中提取收藏夹ID
        """
        # 解析URL: https://space.bilibili.com/309874814/favlist?fid=3125287314&ftype=create
        parsed = urlparse(fav_url)
        query_params = parse_qs(parsed.query)
        if 'fid' in query_params:
            return query_params['fid'][0]
        else:
            raise ValueError("无法解析收藏夹URL，请检查URL格式")

    def get_season_videos(self, uid, season_id):
        """
        获取合集中的所有视频
        """
        videos = []
        page = 1
        page_size = 30

        print(f"正在获取合集 {season_id} 中的视频...")

        while True:
            # 使用新的API端点
            url = "https://api.bilibili.com/x/polymer/web-space/seasons_archives_list"
            params = {
                'mid': uid,
                'season_id': season_id,
                'sort_reverse': False,
                'page_num': page,
                'page_size': page_size
            }

            # 添加必要的headers
            headers = {
                'Referer': f'https://space.bilibili.com/{uid}/channel/seriesdetail?sid={season_id}',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            try:
                response = self.session.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()

                if data['code'] != 0:
                    print(f"获取合集视频失败: {data.get('message', '未知错误')}")
                    # 如果新API失败，尝试备用方法
                    return self.get_season_videos_backup(uid, season_id)

                # 检查数据结构
                if 'data' not in data or 'archives' not in data['data']:
                    print("返回数据格式异常，尝试备用方法...")
                    return self.get_season_videos_backup(uid, season_id)

                archives = data['data']['archives']
                if not archives:
                    break

                for video in archives:
                    videos.append({
                        'bvid': video['bvid'],
                        'aid': video['aid'],
                        'title': video['title'],
                        'pic': video['pic'],
                        'duration': video['duration']
                    })
                    print(f"找到视频: {video['title']} (BV{video['bvid']})")

                # 如果返回的视频数量少于请求的数量，说明已经到最后一页
                if len(archives) < page_size:
                    break

                page += 1
                time.sleep(0.5)  # 避免请求过快

            except Exception as e:
                print(f"获取第{page}页视频时出错: {str(e)}")
                if page == 1:  # 如果第一页就失败，尝试备用方法
                    print("尝试备用方法...")
                    return self.get_season_videos_backup(uid, season_id)
                break

        print(f"总共找到 {len(videos)} 个视频")
        return videos

    def get_season_videos_backup(self, uid, season_id):
        """
        备用的获取合集视频方法
        """
        videos = []
        print(f"使用备用方法获取合集 {season_id} 中的视频...")

        try:
            # 尝试通过个人空间页面获取合集信息
            url = "https://api.bilibili.com/x/polymer/web-space/home/seasons_series"
            params = {
                'mid': uid,
                'page_num': 1,
                'page_size': 10
            }

            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data['code'] == 0 and 'data' in data:
                # 寻找目标合集
                items_lists = data['data'].get('items_lists', {})
                seasons_list = items_lists.get('seasons_list', [])

                target_season = None
                for season in seasons_list:
                    if str(season.get('meta', {}).get('season_id', '')) == str(season_id):
                        target_season = season
                        break

                if target_season:
                    archives = target_season.get('archives', [])
                    for video in archives:
                        videos.append({
                            'bvid': video['bvid'],
                            'aid': video['aid'],
                            'title': video['title'],
                            'pic': video['pic'],
                            'duration': video['duration']
                        })
                        print(f"找到视频: {video['title']} (BV{video['bvid']})")

        except Exception as e:
            print(f"备用方法也失败了: {str(e)}")

    def get_series_videos(self, uid, series_id):
        """
        获取视频列表(series)中的所有视频
        """
        videos = []
        print(f"尝试作为视频列表获取 {series_id} 中的视频...")

        try:
            url = "https://api.bilibili.com/x/series/archives"
            params = {
                'mid': uid,
                'series_id': series_id,
                'only_normal': True,
                'sort': 'desc',
                'pn': 1,
                'ps': 30
            }

            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data['code'] == 0 and 'data' in data:
                archives = data['data'].get('archives', [])
                for video in archives:
                    videos.append({
                        'bvid': video['bvid'],
                        'aid': video['aid'],
                        'title': video['title'],
                        'pic': video['pic'],
                        'duration': video['duration']
                    })
                    print(f"找到视频: {video['title']} (BV{video['bvid']})")

        except Exception as e:
            print(f"获取视频列表失败: {str(e)}")

        print(f"视频列表方法找到 {len(videos)} 个视频")
        return videos

    def add_to_favorites(self, fav_id, videos):
        """
        将视频添加到收藏夹
        """
        success_count = 0
        failed_count = 0

        print(f"开始将视频添加到收藏夹 {fav_id}...")

        for i, video in enumerate(videos, 1):
            try:
                url = "https://api.bilibili.com/x/v3/fav/resource/deal"
                data = {
                    'rid': video['aid'],
                    'type': 2,  # 视频类型
                    'add_media_ids': fav_id,
                    'del_media_ids': '',
                    'csrf': self.get_csrf_token()
                }

                response = self.session.post(url, data=data)
                response.raise_for_status()
                result = response.json()

                if result['code'] == 0:
                    print(f"[{i}/{len(videos)}] 成功添加: {video['title']}")
                    success_count += 1
                else:
                    print(f"[{i}/{len(videos)}] 添加失败: {video['title']} - {result['message']}")
                    failed_count += 1

                # 添加延时避免请求过快
                time.sleep(1)

            except Exception as e:
                print(f"[{i}/{len(videos)}] 添加失败: {video['title']} - {str(e)}")
                failed_count += 1

        print(f"\n转移完成! 成功: {success_count}, 失败: {failed_count}")
        return success_count, failed_count

    def get_csrf_token(self):
        """
        从cookies中获取csrf token
        """
        return self.session.cookies.get('bili_jct', '')

    def verify_login(self):
        """
        验证登录状态
        """
        try:
            url = "https://api.bilibili.com/x/web-interface/nav"
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()

            print(f"API响应码: {data.get('code', 'unknown')}")
            print(f"API消息: {data.get('message', 'unknown')}")

            if data['code'] == 0 and data['data']['isLogin']:
                user_info = data['data']
                print(f"✅ 登录验证成功!")
                print(f"用户名: {user_info.get('uname', '未知')}")
                print(f"UID: {user_info.get('mid', '未知')}")
                return True
            else:
                print("❌ 登录验证失败")
                print("调试信息:")
                print(f"  - 登录状态: {data.get('data', {}).get('isLogin', 'unknown')}")
                print(f"  - 用户信息: {data.get('data', {})}")

                # 检查关键cookies
                key_cookies = ['SESSDATA', 'DedeUserID', 'bili_jct', 'DedeUserID__ckMd5']
                print("\n关键cookies检查:")
                for cookie_name in key_cookies:
                    cookie_value = self.session.cookies.get(cookie_name, '')
                    if cookie_value:
                        print(f"  ✅ {cookie_name}: {cookie_value[:20]}...")
                    else:
                        print(f"  ❌ {cookie_name}: 缺失")

                return False

        except Exception as e:
            print(f"❌ 验证登录状态时出错: {str(e)}")
            print("这可能是网络问题或cookies格式错误")
            return False

    def transfer_collection_to_favorites(self, collection_url, fav_url):
        """
        主函数：将合集转移到收藏夹
        """
        try:
            # 首先验证登录状态
            print("正在验证登录状态...")
            if not self.verify_login():
                return 0, 0

            print("-" * 50)

            # 解析URL
            uid, season_id = self.extract_season_info(collection_url)
            fav_id = self.extract_fav_info(fav_url)

            print(f"合集信息: 用户ID={uid}, 合集ID={season_id}")
            print(f"收藏夹ID: {fav_id}")
            print("-" * 50)

            # 获取合集中的视频
            videos = self.get_season_videos(uid, season_id)

            # 如果合集API获取失败，尝试作为视频列表获取
            if not videos:
                print("合集API获取失败，尝试作为视频列表获取...")
                videos = self.get_series_videos(uid, season_id)

            if not videos:
                print("未找到任何视频，请检查合集URL是否正确")
                return 0, 0

            print("-" * 50)

            # 添加到收藏夹
            success_count, failed_count = self.add_to_favorites(fav_id, videos)

            return success_count, failed_count

        except Exception as e:
            print(f"转移过程中出错: {str(e)}")
            return 0, 0