from pydantic import BaseModel, Field

class BTCData(BaseModel):
    type: str = Field(..., alias="TYPE")
    market: str = Field(..., alias="MARKET")
    instrument: str = Field(..., alias="INSTRUMENT")
    ccseq: int = Field(..., alias="CCSEQ")
    value: float = Field(..., alias="VALUE")
    value_flag: str = Field(..., alias="VALUE_FLAG")
    value_last_update_ts: int = Field(..., alias="VALUE_LAST_UPDATE_TS")
    value_last_update_ts_ns: int = Field(..., alias="VALUE_LAST_UPDATE_TS_NS")
    last_update_quantity: float = Field(..., alias="LAST_UPDATE_QUANTITY")
    last_update_quote_quantity: float = Field(..., alias="LAST_UPDATE_QUOTE_QUANTITY")
    last_update_volume_top_tier: float = Field(..., alias="LAST_UPDATE_VOLUME_TOP_TIER")
    last_update_quote_volume_top_tier: float = Field(..., alias="LAST_UPDATE_QUOTE_VOLUME_TOP_TIER")
    last_update_volume_direct: float = Field(..., alias="LAST_UPDATE_VOLUME_DIRECT")
    last_update_quote_volume_direct: float = Field(..., alias="LAST_UPDATE_QUOTE_VOLUME_DIRECT")
    last_update_volume_top_tier_direct: float = Field(..., alias="LAST_UPDATE_VOLUME_TOP_TIER_DIRECT")
    last_update_quote_volume_top_tier_direct: float = Field(..., alias="LAST_UPDATE_QUOTE_VOLUME_TOP_TIER_DIRECT")
    last_update_ccseq: int = Field(..., alias="LAST_UPDATE_CCSEQ")
    current_hour_volume: float = Field(..., alias="CURRENT_HOUR_VOLUME")
    current_hour_quote_volume: float = Field(..., alias="CURRENT_HOUR_QUOTE_VOLUME")
    current_hour_open: float = Field(..., alias="CURRENT_HOUR_OPEN")
    current_hour_high: float = Field(..., alias="CURRENT_HOUR_HIGH")
    current_hour_low: float = Field(..., alias="CURRENT_HOUR_LOW")
    current_hour_change: float = Field(..., alias="CURRENT_HOUR_CHANGE")
    current_hour_change_percentage: float = Field(..., alias="CURRENT_HOUR_CHANGE_PERCENTAGE")

class BTCDataResponse(BaseModel):
    btc_data: BTCData = Field(..., alias="BTC-DATA")

class APIResponse(BaseModel):
    data: BTCDataResponse
    err: dict = Field(default_factory=dict, alias="Err")