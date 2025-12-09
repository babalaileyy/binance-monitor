from typing import List, Dict, Any, Optional
from loguru import logger

class StrategyAnalyzer:
    """策略分析器"""

    def analyze(self, symbol: str, timeframe: str, klines: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析K线数据，返回分析结果
        :return: 字典包含 'is_pinbar', 'is_priority', 'message' 等字段
        """
        result = {
            "is_pinbar": False,
            "is_priority": False,
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": None,
            "details": ""
        }

        if len(klines) < 41:
            logger.warning(f"Insufficient data for {symbol} {timeframe}: {len(klines)} candles")
            return result

        # 1. 获取最新的已完成K线 (index 1)
        pinbar = klines[1] 
        prev_40 = klines[2:42] # 取前40根
        
        result["timestamp"] = pinbar['timestamp']
        
        # 2. 判断是否是 Pinbar (流程1)
        if not self._is_pinbar(pinbar):
            return result
            
        result["is_pinbar"] = True
        logger.info(f"Pinbar detected for {symbol} {timeframe} at {pinbar['timestamp']}")

        # 3. 判断上下文 (流程2) - 如果满足则标记为重点
        if self._check_context(pinbar, prev_40):
            result["is_priority"] = True
            direction = "UP" if self._get_main_shadow_direction(pinbar) == "UP" else "DOWN"
            direction_cn = "看涨" if direction == "UP" else "看跌"
            result["details"] = (
                f"方向: {direction_cn} (反转信号), "
                f"价格: 开={pinbar['open']}, 高={pinbar['high']}, 低={pinbar['low']}, 收={pinbar['close']}"
            )
        else:
            result["details"] = f"价格: 开={pinbar['open']}, 高={pinbar['high']}, 低={pinbar['low']}, 收={pinbar['close']}"

        return result

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
