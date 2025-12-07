from typing import List, Dict, Any, Optional
from loguru import logger

class StrategyAnalyzer:
    """策略分析器"""

    def analyze(self, symbol: str, timeframe: str, klines: List[Dict[str, Any]]) -> Optional[str]:
        """
        分析K线数据，如果符合策略则返回消息，否则返回None
        :param klines: K线数据列表，按时间倒序排列（最新的在index 0）
                       要求至少包含当前K线 + 前40根K线 = 41根
        """
        if len(klines) < 41:
            logger.warning(f"Insufficient data for {symbol} {timeframe}: {len(klines)} candles")
            return None

        # 1. 获取最新的已完成K线 (假设index 0是当前正在进行的，index 1是刚完成的)
        # 或者假设传入的是已经切分好的历史数据。
        # 通常 fetch_ohlcv 返回包含当前未完成的K线。
        # 我们这里取 index 1 (上一根) 作为要分析的目标 "Pinbar"
        # index 2...41 是 "前40根"
        
        # 修正：根据常规逻辑，我们分析的是“刚走完的那一根”
        pinbar = klines[1] 
        prev_40 = klines[2:42] # 取前40根
        
        # 2. 判断是否是 Pinbar (流程1)
        if not self._is_pinbar(pinbar):
            return None
            
        logger.info(f"Pinbar detected for {symbol} {timeframe} at {pinbar['timestamp']}")

        # 3. 判断上下文 (流程2)
        if self._check_context(pinbar, prev_40):
            # 4. 触发通知 (流程3)
            direction = "UP" if self._get_main_shadow_direction(pinbar) == "UP" else "DOWN"
            return (
                f"Pinbar Alert for {symbol} ({timeframe})\n"
                f"Time: {pinbar['timestamp']}\n"
                f"Price: Open={pinbar['open']}, High={pinbar['high']}, Low={pinbar['low']}, Close={pinbar['close']}\n"
                f"Direction: {direction} (Reversal Signal)\n"
                f"Condition met: Pinbar with valid context."
            )
            
        return None

    def _is_pinbar(self, kline: Dict[str, Any]) -> bool:
        """
        判断是否是 Pinbar
        规则：主影线长度 > 整个K线长度的 2/3
        """
        open_p = kline['open']
        close_p = kline['close']
        high_p = kline['high']
        low_p = kline['low']
        
        total_length = high_p - low_p
        if total_length == 0:
            return False
            
        upper_shadow = high_p - max(open_p, close_p)
        lower_shadow = min(open_p, close_p) - low_p
        
        # 主影线是较长的那根
        main_shadow = max(upper_shadow, lower_shadow)
        
        return main_shadow > (total_length * (2/3))

    def _get_main_shadow_direction(self, kline: Dict[str, Any]) -> str:
        open_p = kline['open']
        close_p = kline['close']
        high_p = kline['high']
        low_p = kline['low']
        
        upper_shadow = high_p - max(open_p, close_p)
        lower_shadow = min(open_p, close_p) - low_p
        
        return "UP" if upper_shadow > lower_shadow else "DOWN"

    def _check_context(self, pinbar: Dict[str, Any], prev_klines: List[Dict[str, Any]]) -> bool:
        """
        流程2：上下文判断
        """
        direction = self._get_main_shadow_direction(pinbar)
        pinbar_length = pinbar['high'] - pinbar['low']
        
        if direction == "UP":
            # 主影线向上 (Shooting Star) -> 看跌
            # 判断pinbar的最高点减去前40根K线的最高点的值的绝对值是否小于这个pinbar的长度
            # 或者如果当前pinbar的最低值高于前40根k线的最高值 (Gap Up)
            
            prev_highs = [k['high'] for k in prev_klines]
            max_prev_high = max(prev_highs)
            
            cond1 = abs(pinbar['high'] - max_prev_high) < pinbar_length
            cond2 = pinbar['low'] > max_prev_high
            
            if cond1 or cond2:
                logger.info("Context valid (UP shadow): cond1={cond1}, cond2={cond2}")
                return True
                
        else: # direction == "DOWN"
            # 主影线向下 (Hammer) -> 看涨
            # 判断pinbar的最低点减去前40根K线的最低点的值的绝对值是否小于这个pinbar的长度
            # 或者当前pinbar的最高值小于前40根k线的最低值 (Gap Down)
            
            prev_lows = [k['low'] for k in prev_klines]
            min_prev_low = min(prev_lows)
            
            cond1 = abs(pinbar['low'] - min_prev_low) < pinbar_length
            cond2 = pinbar['high'] < min_prev_low
            
            if cond1 or cond2:
                logger.info("Context valid (DOWN shadow): cond1={cond1}, cond2={cond2}")
                return True
                
        return False
