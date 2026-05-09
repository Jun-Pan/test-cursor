# 量化投研交易系统（MVP）

这是一个可直接运行的量化系统基础骨架，覆盖了你提出的核心链路：

- 数据收集（实时行情模拟）
- 数据清洗（标准化 + 异常过滤）
- 数据存储（SQLite）
- 分析与特征工程（统计特征、Z-Score）
- 建模（均值回归基线模型）
- 交易信号（买/卖/观望）
- 风险控制（仓位、单笔下单、日内亏损）
- 交易执行（模拟撮合）
- 上线运行（实时循环引擎，支持后续接入真实券商/交易所 API）

## 目录结构

```text
quant_system/
  config.py
  core/
    events.py
    types.py
  data/
    collector.py
    cleaner.py
    storage.py
  research/
    features.py
    model.py
    backtest.py
  trading/
    signal.py
    risk.py
    execution.py
    live_engine.py
  scripts/
    run_backtest.py
    run_live_sim.py
  tests/
    test_backtest.py
```

## 快速开始

> 当前环境使用 `python3` 命令。

### 1) 运行回测

```bash
python3 -m quant_system.scripts.run_backtest
```

### 2) 运行实时模拟交易

```bash
python3 -m quant_system.scripts.run_live_sim
```

系统会：
1. 实时生成行情 tick；
2. 清洗并写入 SQLite；
3. 滚动计算特征并推断模型分数；
4. 产生日志信号并进行风控审核；
5. 通过模拟执行器成交并更新资金/持仓/PnL。

## 核心设计说明

### 1. 数据层（Data）
- `MockPriceCollector`: 模拟实时行情采集（后续可替换为 Binance/CTP/IB 等数据接口）
- `TickCleaner`: 对 tick 做合法性校验和标准化
- `SQLiteStorage`: 保存行情、订单、成交

### 2. 研究层（Research）
- `FeatureEngineer`: 计算收益率均值、波动率、价格 Z-Score
- `MeanReversionModel`: 生成连续分数（score）
- `run_backtest`: 离线验证策略逻辑与风控行为

### 3. 交易层（Trading）
- `SignalGenerator`: score -> BUY/SELL/HOLD
- `RiskManager`: 仓位约束、单笔下单限额、亏损保护
- `SimulatedExecutionEngine`: 模拟下单成交与组合状态更新
- `LiveTradingSystem`: 串联实时数据、策略、风控、执行

## 从模拟盘到实盘上线

你可以沿着以下顺序扩展：

1. **数据接入替换**
   - 将 `MockPriceCollector` 替换为交易所 WebSocket / 券商行情接口
2. **执行层替换**
   - 将 `SimulatedExecutionEngine` 替换为真实下单网关（REST/FIX）
3. **风控增强**
   - 增加品种级、组合级、账户级风控规则
4. **模型升级**
   - 引入多因子、机器学习模型、在线学习
5. **生产化**
   - 加入日志、监控、告警、容灾、参数中心与权限审计

## 注意事项

- 当前是 MVP 基线系统，重点是“端到端可运行”与“模块解耦”。
- 实盘前必须补充：
  - 交易时钟、交易日历、手续费滑点模型
  - 异常重试与断线重连
  - 合规审计与风险审批机制
