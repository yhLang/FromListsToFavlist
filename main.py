#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站合集视频转收藏夹工具
将指定合集中的所有视频添加到指定收藏夹
"""

import json

from FromListsToFavlist import FromListsToFavlist

def test_cookies():
    """
    单独测试cookies是否有效
    """
    print("=" * 60)
    print("B站Cookies测试工具")
    print("=" * 60)
    
    print("\n🔧 获取cookies方法:")
    print("1. 登录B站 (https://www.bilibili.com)")
    print("2. 按F12打开开发者工具")
    print("3. 点击Console(控制台)标签")
    print("4. 输入: document.cookie")
    print("5. 复制返回的整个字符串")
    print("6. 如果缺失SESSDATA, 浏览器开发者工具 → Application/存储 → Cookies")
    
    cookies = input("\n请输入你的B站cookies: ").strip()
    if not cookies:
        print("错误: cookies不能为空")
        return
    
    # 检查cookies格式
    print("\n🔍 检查cookies格式...")
    if not check_cookies_format(cookies):
        return
    
    print("\n正在测试cookies...")
    transfer = FromListsToFavlist(cookies)
    
    if transfer.verify_login():
        print("\n🎉 Cookies有效！你可以使用主程序进行转移操作了。")
    else:
        print("\n❌ Cookies无效，请重新获取。")
        print("\n💡 常见问题解决:")
        print("1. 确保已经登录B站")
        print("2. 复制完整的cookie字符串（通常很长）")
        print("3. 不要复制多余的引号")
        print("4. cookies可能已过期，请重新登录后获取")


def check_cookies_format(cookies):
    """
    检查cookies格式是否正确
    """
    if not cookies or len(cookies) < 50:
        print("❌ Cookies太短，可能不完整")
        return False
    
    # 检查必要的cookies
    required_cookies = ['SESSDATA', 'DedeUserID', 'bili_jct']
    missing_cookies = []
    
    for cookie in required_cookies:
        if cookie not in cookies:
            missing_cookies.append(cookie)
    
    if missing_cookies:
        print(f"❌ 缺少必要的cookies: {', '.join(missing_cookies)}")
        print("请确保复制了完整的cookie字符串")
        return False
    
    print("✅ Cookies格式检查通过")
    return True


def main():
    """
    主程序入口
    """
    print("=" * 60)
    print("B站合集转收藏夹工具")
    print("=" * 60)
    
    print("\n请选择功能:")
    print("1. 测试cookies是否有效")
    print("2. 执行合集转收藏夹")
    
    choice = input("\n请输入选择 (1或2): ").strip()
    
    if choice == '1':
        test_cookies()
        return
    elif choice != '2':
        print("无效选择，程序退出")
        return
    
    # 获取用户输入
    print("\n请按照提示输入相关信息:")
    print("注意：需要先登录B站并获取cookies")
    
    cookies = input("\n1. 请输入你的B站cookies: ").strip()
    if not cookies:
        print("错误: cookies不能为空")
        return
    
    collection_url = input("\n2. 请输入合集URL: ").strip()
    if not collection_url:
        print("错误: 合集URL不能为空")
        return
    
    fav_url = input("\n3. 请输入收藏夹URL: ").strip()
    if not fav_url:
        print("错误: 收藏夹URL不能为空")
        return
    
    # 确认操作
    print(f"\n即将执行操作:")
    print(f"源合集: {collection_url}")
    print(f"目标收藏夹: {fav_url}")
    
    confirm = input("\n确认执行吗? (y/N): ").strip().lower()
    if confirm != 'y':
        print("操作已取消")
        return
    
    print("\n" + "=" * 60)
    
    # 执行转移
    transfer = FromListsToFavlist.py(cookies)
    success_count, failed_count = transfer.transfer_collection_to_favorites(collection_url, fav_url)
    
    print("=" * 60)
    print("操作完成!")
    if success_count > 0:
        print(f"成功转移 {success_count} 个视频到收藏夹")
    if failed_count > 0:
        print(f"有 {failed_count} 个视频转移失败")


if __name__ == "__main__":
    main()