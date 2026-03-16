"""
大麦 App 抢票引擎 - 基于 uiautomator2

直接通过 ADB 控制安卓设备上的大麦 App，
比 Appium 轻量，不需要 Node.js / Appium Server。

使用 text 匹配定位元素，适配大麦 App 各版本。
"""

import re
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import uiautomator2 as u2


class DamaiAppSniper:

    DAMAI_PACKAGE = "cn.damai"

    def __init__(self, config: dict):
        self.config = config
        self.d: Optional[u2.Device] = None
        self._attempt = 0
        self._success = False

    # ==================================================================
    # 主流程
    # ==================================================================

    def run(self):
        self._connect_device()
        self._open_damai()
        self._navigate_to_show()
        self._wait_for_start_time()
        self._snipe_loop()

    # ==================================================================
    # 连接设备
    # ==================================================================

    def _connect_device(self):
        addr = self.config.get("device_addr", "")
        if addr:
            self._log(f"连接设备: {addr}")
            subprocess.run(["adb", "connect", addr], capture_output=True)
            time.sleep(1)
            self.d = u2.connect(addr)
        else:
            self._log("自动检测 USB 设备...")
            self.d = u2.connect()

        info = self.d.info
        self._log(f"设备已连接: {info.get('productName', 'unknown')} "
                  f"(Android {self.d.device_info.get('version', '?')})")
        self._log(f"屏幕: {self.d.window_size()}")

    # ==================================================================
    # 打开大麦
    # ==================================================================

    def _open_damai(self):
        self._log("启动大麦 App...")
        self.d.app_start(self.DAMAI_PACKAGE)
        time.sleep(3)

        # 处理可能的弹窗（广告、权限等）
        self._dismiss_popups()

    def _dismiss_popups(self):
        """关闭常见弹窗"""
        dismiss_texts = ["我知道了", "同意", "允许", "关闭", "跳过", "取消", "暂不升级", "以后再说"]
        for _ in range(5):
            dismissed = False
            for text in dismiss_texts:
                el = self.d(text=text)
                if el.exists(timeout=0.5):
                    el.click()
                    self._log(f"  关闭弹窗: {text}")
                    time.sleep(0.5)
                    dismissed = True
                    break
            if not dismissed:
                break

    # ==================================================================
    # 导航到演出页
    # ==================================================================

    def _navigate_to_show(self):
        share_url = self.config.get("share_url", "")
        if not share_url:
            self._log("未配置 share_url，请手动在 App 中打开演出页面")
            self._log("等待 30 秒...")
            time.sleep(30)
            return

        item_id = self._extract_item_id(share_url)
        if item_id:
            # 通过 deeplink 直接跳转到演出详情页
            deeplink = f"https://m.damai.cn/shows/item.html?itemId={item_id}"
            self._log(f"通过链接跳转到演出页 (itemId={item_id})...")
            self.d.open_url(deeplink)
            time.sleep(3)
            self._dismiss_popups()
        else:
            self._log("无法解析 itemId，请手动打开演出页面")
            time.sleep(15)

    @staticmethod
    def _extract_item_id(url: str) -> str:
        m = re.search(r"itemId=(\d+)", url)
        return m.group(1) if m else ""

    # ==================================================================
    # 定时等待
    # ==================================================================

    def _wait_for_start_time(self):
        start_str = self.config.get("start_time", "")
        if not start_str:
            return

        target = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
        now = time.time()

        if now >= target.timestamp():
            self._log("抢购时间已过，立即开始")
            return

        self._log(f"等待抢购时间: {target}")
        while time.time() < target.timestamp() - 5:
            remaining = target.timestamp() - time.time()
            if remaining > 60:
                self._log(f"  还有 {remaining / 60:.1f} 分钟")
                time.sleep(30)
            else:
                self._log(f"  还有 {remaining:.0f}s")
                time.sleep(min(5, remaining - 5))

        # 最后几秒刷新页面
        self._log("即将开售，刷新页面...")
        share_url = self.config.get("share_url", "")
        item_id = self._extract_item_id(share_url)
        if item_id:
            self.d.open_url(f"https://m.damai.cn/shows/item.html?itemId={item_id}")
            time.sleep(1)

        while time.time() < target.timestamp():
            time.sleep(0.01)

        self._log("时间到！开始抢票！")

    # ==================================================================
    # 核心抢票循环
    # ==================================================================

    def _snipe_loop(self):
        behavior = self.config.get("behavior", {})
        interval = behavior.get("interval_ms", 300) / 1000
        max_attempts = behavior.get("max_attempts", 0)
        wanted = self.config.get("wanted_tickets", [])
        ticket_count = self.config.get("ticket_count", 1)

        self._log(f"抢票循环启动（间隔 {interval * 1000:.0f}ms）")

        while True:
            self._attempt += 1
            if max_attempts and self._attempt > max_attempts:
                self._log(f"已达最大 {max_attempts} 次，停止")
                break

            if self._attempt % 50 == 0:
                self._log(f"  第 {self._attempt} 次尝试...")

            try:
                # Step 1: 选票档
                if not self._select_ticket(wanted):
                    if self._attempt % 10 == 0:
                        self._refresh_page()
                    time.sleep(interval)
                    continue

                # Step 2: 调整数量
                if ticket_count > 1:
                    self._set_count(ticket_count)

                # Step 3: 点击购买
                if not self._click_buy():
                    time.sleep(interval)
                    continue

                self._log(f"第 {self._attempt} 次 - 点击购买成功！")
                time.sleep(1.5)

                # Step 4: 处理弹窗/确认
                self._dismiss_popups()

                # Step 5: 选择购票人
                self._select_buyers()

                # Step 6: 提交订单
                self._submit_order()

                self._success = True
                self._log("=" * 50)
                self._log(f"抢票流程完成！共尝试 {self._attempt} 次")
                self._log("请在手机上完成支付！")
                self._log("=" * 50)

                if behavior.get("screenshot_on_success", True):
                    self._screenshot("success")
                return

            except Exception as e:
                if self._attempt % 50 == 0:
                    self._log(f"  异常: {e}")

            time.sleep(interval)

        if not self._success:
            self._log("未能成功抢到票")

    # ==================================================================
    # Step 1: 选择票档
    # ==================================================================

    def _select_ticket(self, wanted: list) -> bool:
        # 尝试按关键词匹配票档
        if wanted and wanted[0]:
            for keyword in wanted:
                el = self.d(textContains=keyword, clickable=True)
                if el.exists(timeout=0.3):
                    el.click()
                    self._log(f"  选中票档: {keyword}")
                    time.sleep(0.2)
                    return True

        # 没有指定或没匹配到 → 尝试点击价格区域
        # 大麦 App 票档通常包含 "¥" 或纯数字价格
        price_el = self.d(textMatches=r".*[¥￥]\d+.*", clickable=True)
        if price_el.exists(timeout=0.3):
            price_el.click()
            time.sleep(0.2)
            return True

        return False

    # ==================================================================
    # Step 2: 调整数量
    # ==================================================================

    def _set_count(self, count: int):
        for _ in range(count - 1):
            # 大麦 App 中数量 "+" 按钮
            plus = self.d(description="增加")
            if not plus.exists(timeout=0.3):
                plus = self.d(text="+")
            if not plus.exists(timeout=0.3):
                plus = self.d(resourceIdMatches=r".*add.*|.*plus.*|.*increase.*")
            if plus.exists(timeout=0.3):
                plus.click()
                time.sleep(0.1)

    # ==================================================================
    # Step 3: 点击购买按钮
    # ==================================================================

    def _click_buy(self) -> bool:
        buy_texts = ["立即购买", "立即预订", "立即预定", "选座购买", "立即抢购"]
        for text in buy_texts:
            el = self.d(textContains=text)
            if el.exists(timeout=0.3):
                el.click()
                return True

        # 也尝试 resource-id 匹配
        el = self.d(resourceIdMatches=r".*buy.*|.*purchase.*")
        if el.exists(timeout=0.3):
            el.click()
            return True

        return False

    # ==================================================================
    # Step 5: 选择购票人
    # ==================================================================

    def _select_buyers(self):
        buyers = self.config.get("buyers", [])
        if buyers and buyers[0]:
            for name in buyers:
                el = self.d(textContains=name)
                if el.exists(timeout=1):
                    el.click()
                    self._log(f"  选中购票人: {name}")
                    time.sleep(0.2)
        else:
            # 尝试点击第一个未选中的购票人
            # 大麦 App 中未选中的购票人旁边有空心圆
            time.sleep(0.5)

    # ==================================================================
    # Step 6: 提交订单
    # ==================================================================

    def _submit_order(self):
        time.sleep(0.5)
        submit_texts = ["提交订单", "确认订单", "立即支付", "去支付"]
        for text in submit_texts:
            el = self.d(textContains=text)
            if el.exists(timeout=1.5):
                el.click()
                self._log(f"  已点击「{text}」")
                time.sleep(1)
                return

    # ==================================================================
    # 工具方法
    # ==================================================================

    def _refresh_page(self):
        """下拉刷新"""
        w, h = self.d.window_size()
        self.d.swipe(w // 2, h // 4, w // 2, h * 3 // 4, duration=0.3)
        time.sleep(1)

    def _screenshot(self, name: str):
        try:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = Path(f"screenshots/{name}_{ts}.png")
            path.parent.mkdir(parents=True, exist_ok=True)
            self.d.screenshot(str(path))
            self._log(f"截图: {path}")
        except Exception:
            pass

    @staticmethod
    def _log(msg: str):
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{ts}] {msg}")
