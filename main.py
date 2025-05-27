#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站合集视频转收藏夹工具
将指定合集中的所有视频添加到指定收藏夹
"""

import os
import json
from FromListsToFavlist import FromListsToFavlist

# cookies文件路径
COOKIES_FILE = "bilibili_cookies.txt"

def create_cookies_file():
    """
    创建cookies文件并提示用户填入内容
    """
    print("=" * 60)
    print("创建Cookies文件")
    print("=" * 60)
    
    print(f"\n将创建文件: {COOKIES_FILE}")
    print("\n🔧 获取cookies方法:")
    print("1. 登录B站 (https://www.bilibili.com)")
    print("2. 按F12打开开发者工具")
    print("3. 点击Console(控制台)标签")
    print("4. 输入: document.cookie")
    print("5. 复制返回的整个字符串")
    print("6. 如果缺失SESSDATA, 浏览器开发者工具 → Application/存储 → Cookies")
    
    # 创建空的cookies文件模板
    template_content = """# B站Cookies配置文件
# 请将你的完整cookies粘贴到下面这行，替换这个注释
# 格式示例: SESSDATA=abc123; DedeUserID=12345; bili_jct=xyz789; DedeUserID__ckMd5=abcdef

"""
    
    try:
        with open(COOKIES_FILE, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        print(f"\n✅ 已创建文件: {COOKIES_FILE}")
        print("\n📝 请按以下步骤操作:")
        print(f"1. 用文本编辑器打开 {COOKIES_FILE}")
        print("2. 按照上面的方法获取你的B站cookies")
        print("3. 将cookies粘贴到文件中（替换注释内容）")
        print("4. 保存文件")
        print("5. 重新运行程序")
        
        # 询问是否要直接输入cookies
        choice = input("\n是否现在就输入cookies? (y/N): ").strip().lower()
        if choice == 'y':
            cookies = input("\n请粘贴你的cookies: ").strip()
            if cookies and len(cookies) > 50:
                # 验证cookies格式
                if check_cookies_format(cookies):
                    # 写入文件
                    with open(COOKIES_FILE, 'w', encoding='utf-8') as f:
                        f.write("# B站Cookies配置文件\n")
                        f.write("# 自动生成于程序运行时\n\n")
                        f.write(cookies)
                    
                    print(f"\n✅ Cookies已保存到 {COOKIES_FILE}")
                    return True
                else:
                    print("\n❌ Cookies格式验证失败，请检查后重新输入")
            else:
                print("\n❌ Cookies为空或太短，请重新输入")
        
        return False
        
    except Exception as e:
        print(f"\n❌ 创建文件失败: {str(e)}")
        return False

def read_cookies_from_file():
    """
    从文件读取cookies
    """
    try:
        if not os.path.exists(COOKIES_FILE):
            return None
            
        with open(COOKIES_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # 过滤掉注释行和空行
        lines = []
        for line in content.split('\n'):
            line = line.strip()
            if not line.startswith('#') and line:
                lines.append(line)
        
        if not lines:
            return None
            
        # 取第一个非注释行作为cookies
        cookies = lines[0].strip()
        
        if len(cookies) < 50:  # cookies太短
            return None
            
        return cookies
        
    except Exception as e:
        print(f"❌ 读取cookies文件失败: {str(e)}")
        return None

def update_cookies_file():
    """
    更新cookies文件
    """
    print("=" * 60)
    print("更新Cookies文件")
    print("=" * 60)
    
    print(f"\n当前cookies文件: {COOKIES_FILE}")
    
    if os.path.exists(COOKIES_FILE):
        print("✅ 文件存在")
        
        # 显示当前cookies信息（部分）
        current_cookies = read_cookies_from_file()
        if current_cookies:
            print(f"当前cookies预览: {current_cookies[:100]}...")
        else:
            print("⚠️  文件存在但cookies无效")
    else:
        print("❌ 文件不存在")
    
    choice = input("\n是否要更新cookies? (y/N): ").strip().lower()
    if choice != 'y':
        return False
    
    print("\n🔧 获取新cookies方法:")
    print("1. 登录B站 (https://www.bilibili.com)")
    print("2. 按F12打开开发者工具")
    print("3. 点击Console(控制台)标签")
    print("4. 输入: document.cookie")
    print("5. 复制返回的整个字符串")
    
    cookies = input("\n请粘贴新的cookies: ").strip()
    if not cookies:
        print("❌ Cookies为空")
        return False
    
    # 验证cookies格式
    if not check_cookies_format(cookies):
        return False
    
    try:
        # 备份旧文件
        if os.path.exists(COOKIES_FILE):
            backup_file = f"{COOKIES_FILE}.backup"
            os.rename(COOKIES_FILE, backup_file)
            print(f"✅ 已备份旧文件为: {backup_file}")
        
        # 写入新cookies
        with open(COOKIES_FILE, 'w', encoding='utf-8') as f:
            f.write("# B站Cookies配置文件\n")
            f.write("# 更新时间: " + str(__import__('datetime').datetime.now()) + "\n\n")
            f.write(cookies)
        
        print(f"✅ 新cookies已保存到 {COOKIES_FILE}")
        return True
        
    except Exception as e:
        print(f"❌ 更新文件失败: {str(e)}")
        return False

def test_cookies():
    """
    测试cookies是否有效
    """
    print("=" * 60)
    print("B站Cookies测试工具")
    print("=" * 60)
    
    # 尝试从文件读取cookies
    cookies = read_cookies_from_file()
    
    if not cookies:
        print(f"❌ 无法从 {COOKIES_FILE} 读取有效cookies")
        
        if not os.path.exists(COOKIES_FILE):
            print(f"文件 {COOKIES_FILE} 不存在")
            choice = input("\n是否创建cookies文件? (y/N): ").strip().lower()
            if choice == 'y':
                if create_cookies_file():
                    # 重新尝试读取
                    cookies = read_cookies_from_file()
                    if not cookies:
                        print("❌ 仍然无法读取cookies，请检查文件内容")
                        return
                else:
                    return
            else:
                return
        else:
            print("请检查文件内容是否正确")
            choice = input("\n是否更新cookies文件? (y/N): ").strip().lower()
            if choice == 'y':
                if update_cookies_file():
                    cookies = read_cookies_from_file()
                    if not cookies:
                        print("❌ 仍然无法读取cookies")
                        return
                else:
                    return
            else:
                return
    
    print(f"✅ 从 {COOKIES_FILE} 读取到cookies")
    print(f"Cookies预览: {cookies[:100]}...")
    
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
        choice = input("\n是否更新cookies文件? (y/N): ").strip().lower()
        if choice == 'y':
            update_cookies_file()

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
    print("3. 创建/更新cookies文件")
    print("4. 查看cookies文件状态")
    
    choice = input("\n请输入选择 (1-4): ").strip()
    
    if choice == '1':
        test_cookies()
        return
    elif choice == '3':
        if os.path.exists(COOKIES_FILE):
            update_cookies_file()
        else:
            create_cookies_file()
        return
    elif choice == '4':
        show_cookies_status()
        return
    elif choice != '2':
        print("无效选择，程序退出")
        return
    
    # 选择2：执行合集转收藏夹
    print("\n" + "=" * 60)
    print("执行合集转收藏夹")
    print("=" * 60)
    
    # 读取cookies
    cookies = read_cookies_from_file()
    if not cookies:
        print(f"❌ 无法从 {COOKIES_FILE} 读取cookies")
        print("请先运行选项3创建cookies文件")
        return
    
    print(f"✅ 已从 {COOKIES_FILE} 读取cookies")
    
    # 获取用户输入
    collection_url = input("\n1. 请输入合集URL: ").strip()
    if not collection_url:
        print("错误: 合集URL不能为空")
        return
    
    fav_url = input("\n2. 请输入收藏夹URL: ").strip()
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
    transfer = FromListsToFavlist(cookies)
    success_count, failed_count = transfer.transfer_collection_to_favorites(collection_url, fav_url)
    
    print("=" * 60)
    print("操作完成!")
    if success_count > 0:
        print(f"成功转移 {success_count} 个视频到收藏夹")
    if failed_count > 0:
        print(f"有 {failed_count} 个视频转移失败")

def show_cookies_status():
    """
    显示cookies文件状态
    """
    print("=" * 60)
    print("Cookies文件状态")
    print("=" * 60)
    
    print(f"\n文件路径: {os.path.abspath(COOKIES_FILE)}")
    
    if os.path.exists(COOKIES_FILE):
        print("✅ 文件存在")
        
        try:
            # 获取文件信息
            stat = os.stat(COOKIES_FILE)
            size = stat.st_size
            mtime = __import__('datetime').datetime.fromtimestamp(stat.st_mtime)
            
            print(f"文件大小: {size} 字节")
            print(f"修改时间: {mtime}")
            
            # 尝试读取cookies
            cookies = read_cookies_from_file()
            if cookies:
                print("✅ Cookies读取成功")
                print(f"Cookies长度: {len(cookies)} 字符")
                print(f"Cookies预览: {cookies[:100]}...")
                
                # 检查关键字段
                key_fields = ['SESSDATA', 'DedeUserID', 'bili_jct', 'DedeUserID__ckMd5']
                print("\n关键字段检查:")
                for field in key_fields:
                    if field in cookies:
                        print(f"  ✅ {field}")
                    else:
                        print(f"  ❌ {field}")
            else:
                print("❌ Cookies读取失败或为空")
                
        except Exception as e:
            print(f"❌ 读取文件信息失败: {str(e)}")
    else:
        print("❌ 文件不存在")
        print("\n💡 使用选项3创建cookies文件")

if __name__ == "__main__":
    main()