"""
导航到 Google Docs 并截图
"""
from playwright.sync_api import sync_playwright
import time

def navigate_and_screenshot():
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        try:
            print("正在导航到 https://docs.google.com ...")
            
            # 导航到 Google Docs
            response = page.goto('https://docs.google.com', wait_until='networkidle', timeout=30000)
            
            # 等待页面加载
            time.sleep(3)
            
            # 获取最终 URL（可能有重定向）
            final_url = page.url
            
            # 截图
            screenshot_path = 'c:\\ADHD_agent\\google_docs_screenshot.png'
            page.screenshot(path=screenshot_path, full_page=False)
            
            # 获取页面标题
            title = page.title()
            
            # 检查是否有错误消息
            error_messages = []
            
            # 检查常见的错误元素
            error_selectors = [
                'text="Error"',
                'text="404"',
                'text="Page not found"',
                '[role="alert"]',
                '.error-message'
            ]
            
            for selector in error_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        error_text = page.locator(selector).first.text_content()
                        if error_text:
                            error_messages.append(error_text)
                except:
                    pass
            
            # 获取页面主要内容
            body_text = page.locator('body').text_content()[:500] if page.locator('body').count() > 0 else ""
            
            # 检查是否是登录页面
            is_login_page = any([
                'sign in' in body_text.lower(),
                'login' in body_text.lower(),
                'email' in body_text.lower() and 'password' in body_text.lower()
            ])
            
            # 输出结果
            print("\n" + "="*80)
            print("导航结果报告")
            print("="*80)
            print(f"1. 页面加载状态: {'成功' if response and response.ok else '失败'}")
            if response:
                print(f"   HTTP 状态码: {response.status}")
            
            print(f"\n2. 页面类型:")
            if is_login_page:
                print("   - 登录页面（需要 Google 账号登录）")
            elif error_messages:
                print("   - 错误页面")
            else:
                print("   - 正常页面")
            
            print(f"\n3. 页面标题: {title}")
            
            print(f"\n4. 最终 URL: {final_url}")
            
            if error_messages:
                print(f"\n5. 错误消息:")
                for msg in error_messages:
                    print(f"   - {msg}")
            else:
                print(f"\n5. 错误消息: 无")
            
            print(f"\n6. 截图已保存到: {screenshot_path}")
            
            print(f"\n7. 页面内容预览（前500字符）:")
            print(f"   {body_text[:500]}")
            
            print("="*80)
            
        except Exception as e:
            print(f"发生错误: {str(e)}")
            print(f"错误类型: {type(e).__name__}")
            
        finally:
            # 等待一下让用户看到浏览器
            time.sleep(2)
            browser.close()

if __name__ == '__main__':
    navigate_and_screenshot()
