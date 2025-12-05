from typing import Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from binance_monitor.notification import EmailConfig

class MonitorConfig(BaseModel):
    """监控任务配置"""
    symbol: str = Field(..., description="监控交易对，例如 BTC/USDT")
    target_price_upper: Optional[float] = Field(None, description="目标价格上限")
    target_price_lower: Optional[float] = Field(None, description="目标价格下限")
    check_interval_seconds: int = Field(60, description="检查间隔(秒)")

class BinanceConfig(BaseModel):
    """币安API配置"""
    api_key: Optional[str] = Field(None, description="API Key (可选)")
    secret_key: Optional[str] = Field(None, description="Secret Key (可选)")

class AppConfig(BaseSettings):
    """应用总配置"""
    monitor: MonitorConfig
    email: EmailConfig
    binance: BinanceConfig = Field(default_factory=BinanceConfig)

    model_config = SettingsConfigDict(
        yaml_file="config/config.yaml",
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore"
    )

def load_config(config_path: str = "config/config.yaml") -> AppConfig:
    """加载配置"""
    # pydantic-settings 默认不支持直接读取 yaml，这里我们需要一个辅助加载器
    # 或者我们可以简单地用 pyyaml 读取字典传给 AppConfig
    # 为了现代化和健壮性，这里我们使用 pyyaml 读取并验证
    import yaml
    import os
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
        
    with open(config_path, 'r', encoding='utf-8') as f:
        config_dict = yaml.safe_load(f)
        
    return AppConfig(**config_dict)
