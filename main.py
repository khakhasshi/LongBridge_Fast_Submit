import json
import time
import threading
from datetime import datetime, timedelta
from decimal import Decimal
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pynput import keyboard
from longport.openapi import QuoteContext, TradeContext, Config, OrderType, OrderSide, TimeInForceType

# Initialize config and contexts
config = Config(
    app_key=" ",    #此处的APPkey，APPseceret，AccessTOken需要自己去https://open.longportapp.com/zh-CN/account注册领取，领取后填写到相应位置
    app_secret=" ",
    access_token=" "
)
quote_ctx = QuoteContext(config)
trade_ctx = TradeContext(config)
json_file_path = 'quote.json'      #在目录下需要手动创建一个空的json文件用于暂存数据

# Position tracking
position = {'type': None, 'entry_price': None, 'quantity': 25}  # Long or Short  每次做多做空的单位，我这里是25股，根据自己的需求来确定
position_value = []

# JSON encoder
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Fetch quote
def fetch_and_store_quote():
    while True:
        resp = quote_ctx.quote(["NVDA.US"])       #拉取行情数据的标的，我这里选英伟达
        if resp:
            data = resp[0]
            quote = {
                "symbol": data.symbol,
                "last_done": float(data.last_done),
                "timestamp": datetime.utcnow().isoformat()
            }
            with open(json_file_path, 'w') as f:
                json.dump(quote, f, cls=DecimalEncoder)
        time.sleep(0.1)          #拉取行情数据的频率，我这里设定一秒内拉取10次，这是长桥API的最大调用频率

# Order submission
def submit_market_order(symbol, side: OrderSide):
    global position
    try:
        resp = trade_ctx.submit_order(
            symbol=symbol,
            order_type=OrderType.MO,
            side=side,
            submitted_quantity=Decimal(position['quantity']),
            time_in_force=TimeInForceType.Day,
            remark="Triggered by keyboard"
        )
        print(f"{side} order placed: {resp}")
        if side == OrderSide.Buy:
            position['type'] = 'long'
        elif side == OrderSide.Sell:
            position['type'] = 'short'
        position['entry_price'] = get_last_price()
    except Exception as e:
        print(f"Order failed: {e}")

# 获取最新价格
def get_last_price():
    with open(json_file_path, 'r') as f:
        quote = json.load(f)
        return float(quote['last_done'])

# 键盘监听
def on_press(key):
    try:
        if key.char.lower() == 'n':                         #此处用于确定买单（做多）按键，这里我设定为N
            submit_market_order("NVDA.US", OrderSide.Buy)   #做多标的
        elif key.char.lower() == 'm':                       #此处用于确定卖单（做空）按键，这里我设定为N
            submit_market_order("NVDA.US", OrderSide.Sell)  #做空标的
        elif key.char.lower() == 'q':                       #用于结束程序
            print("Exiting...")
            return False
    except AttributeError:
        pass

def start_keyboard_listener():
    print("Press N to Buy (long), M to Sell (short), Q to Quit.")
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

# 动画更新函数
def animate(i, xs_all, ys_all, xs_5min, ys_5min, xs_60s, ys_60s, ax_all, ax_5min, ax_60s, ax_pos):
    try:
        with open(json_file_path, 'r') as f:
            quote = json.load(f)
            timestamp = datetime.fromisoformat(quote["timestamp"])
            price = quote["last_done"]

            # 更新主图数据
            if not xs_all or timestamp > xs_all[-1]:
                xs_all.append(timestamp)
                ys_all.append(price)

            # 保持子图数据在指定时间范围内
            def trim(xs, ys, delta_seconds):
                while xs and (timestamp - xs[0]).total_seconds() > delta_seconds:
                    xs.pop(0)
                    ys.pop(0)
                xs.append(timestamp)
                ys.append(price)

            trim(xs_5min, ys_5min, 300) #过去五分钟的滚动子图
            trim(xs_60s, ys_60s, 60)    #过去一分钟的滚动子图

            # 更新持仓价值
            if position['type'] and position['entry_price'] is not None:
                multiplier = 1 if position['type'] == 'long' else -1
                profit = (price - position['entry_price']) * position['quantity'] * multiplier
                value_str = f"{position['type'].capitalize()} Position\nEntry: {position['entry_price']:.2f}\nNow: {price:.2f}\nPnL: {profit:.2f} USD"
            else:
                value_str = "No active position"

            # 绘图 - 左上 全程图
            ax_all.clear()
            ax_all.plot(xs_all, ys_all, color='lime')
            ax_all.set_title('All Prices', color='lime')
            ax_all.tick_params(colors='lime')

            # 右上 5min
            ax_5min.clear()
            ax_5min.plot(xs_5min, ys_5min, color='lime')
            ax_5min.set_title('Last 5 Minutes', color='lime')
            ax_5min.tick_params(colors='lime')

            # 左下 60s
            ax_60s.clear()
            ax_60s.plot(xs_60s, ys_60s, color='lime')
            ax_60s.set_title('Last 60 Seconds', color='lime')
            ax_60s.tick_params(colors='lime')

            # 右下持仓信息
            ax_pos.clear()
            ax_pos.axis('off')
            ax_pos.text(0.5, 0.5, value_str, color='lime', fontsize=14,
                        ha='center', va='center', fontweight='lime')

    except Exception as e:
        print(f"Error in animate: {e}")

# 主函数
def main():
    plt.style.use('dark_background')
    fig, axs = plt.subplots(2, 2, figsize=(14, 8))
    ax_all, ax_5min = axs[0]
    ax_60s, ax_pos = axs[1]

    xs_all, ys_all = [], []
    xs_5min, ys_5min = [], []
    xs_60s, ys_60s = [], []

    fetch_thread = threading.Thread(target=fetch_and_store_quote, daemon=True)
    fetch_thread.start()
    start_keyboard_listener()

    ani = animation.FuncAnimation(
        fig, animate,
        fargs=(xs_all, ys_all, xs_5min, ys_5min, xs_60s, ys_60s, ax_all, ax_5min, ax_60s, ax_pos),
        interval=100         #行情动画更新的频率，我这里选择间隔100MS更新一次，与数据拉取频率相同
    )
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
