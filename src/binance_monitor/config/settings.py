from typing import Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from binance_monitor.notification import EmailConfig

class MonitorConfig(BaseModel):
    """监控任务配置"""
    symbols: list[str] = Field(..., description="监控交易对列表，例如 ['BTC/USDT', 'ETH/USDT']")
    timeframes: list[str] = Field(["4h", "1d"], description="监控周期列表")
    check_interval_minutes: int = Field(60, description="扫描间隔(分钟), 如果使用 cron_expression 则忽略此项")
    cron_expression: Optional[str] = Field(None, description="Cron表达式，例如 '1 */4 * * *'")

class BinanceConfig(BaseModel):
    """币安API配置"""
    api_key: Optional[str] = Field(None, description="API Key (可选)")
    secret_key: Optional[str] = Field(None, description="Secret Key (可选)")
    http_proxy: Optional[str] = Field(None, description="HTTP代理地址, 例如 http://127.0.0.1:7890")
    https_proxy: Optional[str] = Field(None, description="HTTPS代理地址, 例如 http://127.0.0.1:7890")

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
