# 🎯 Real-Time NVDA Trading Monitor & Order Executor

该项目是一个基于 Longbridge API 实时拉取 **NVDA（英伟达）美股数据**，并通过 **键盘控制下单** 的 Python 程序，集成了可视化图表、持仓追踪和订单提交功能，适合用于交易策略测试与人工盯盘辅助操作。

## 📦 功能说明

- ⏱ 实时行情获取（NVDA.US，每秒最多10次）
- 📉 三种视图：
  - 所有价格历史
  - 过去5分钟价格走势
  - 过去1分钟价格走势
- 💼 持仓追踪：
  - 显示做多/做空持仓信息、进场价格、当前价格、实时盈亏（仅供参考，实际测试有不显示的BUG，看手机上的成交价格和盈亏，大佬可以来改bug）
- ⌨️ 键盘下单：
  - `N` 键做多（Buy）
  - `M` 键做空（Sell）
  - `Q` 键退出程序
- 🎮 实时交互 + 图表动态更新

## 🧱 项目结构

```bash
.
├── main.py             # 主程序
├── quote.json          # 用于缓存实时行情的临时文件（需提前创建）
├── README.md           # 使用说明
```

## 🚀 安装步骤

1. **安装依赖包**

```bash
pip install longport-openapi matplotlib pynput
```

2. **注册 Longbridge API**

前往 [https://open.longportapp.com/zh-CN/account](https://open.longportapp.com/zh-CN/account) 注册开发者账号，获取以下信息：

- `APP Key`
- `APP Secret`
- `Access Token`

将它们填入代码中的 `config = Config(...)` 中。

3. **创建缓存文件**

在项目目录下创建一个空的 `quote.json` 文件：

```bash
touch quote.json
```

## 🎯 使用方法

运行程序后将出现图表窗口，同时在控制台中会提示：

```
Press N to Buy (long), M to Sell (short), Q to Quit.
```

- 按 `N` 键：提交**做多**市价单（25股）
- 按 `M` 键：提交**做空**市价单（25股）
- 按 `Q` 键：退出程序

## 📊 可视化界面说明

图表共有四个区域：

- 📈 左上角：全程价格历史
- ⏱ 右上角：过去 5 分钟内的价格走势
- ⏱ 左下角：过去 60 秒内的价格走势
- 💼 右下角：当前持仓信息（方向、进场价、当前价、盈亏）

## ⚙️ 参数说明

在 `position` 中可以修改交易单位：

```python
position = {
    'type': None,
    'entry_price': None,
    'quantity': 25  # 每次买入/卖出股数
}
```

行情拉取与图像刷新频率设为每 0.1 秒：

```python
time.sleep(0.1)          # 拉取频率
interval=100             # 动画刷新频率 (ms)
```

## 🛑 注意事项

- 请确保网络连接稳定，避免 API 请求失败。
- 避免在真实账户下频繁下单，建议先在模拟账户测试。
- 持仓信息不记录历史，只追踪当前一次下单情况。

## 📌 未来可拓展方向

- 添加止盈/止损逻辑
- 增加自动交易策略
- 多标的支持（可自定义）
- 持仓记录保存与分析

---

如需协助或有任何建议，欢迎提 issue 或联系项目开发者。

Happy Trading! 📈💻
