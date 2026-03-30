from pydantic import Field
from datetime import date
from typing import Any
from .common import BaseSchema, MetricType, ChartType

class AnalyticsRequest(BaseSchema):
    period_days: int = Field(default=30, ge=1, le=365)
    metrics: list[MetricType] = [MetricType.MOOD, MetricType.ANXIETY, MetricType.FATIGUE]
    chart_type: ChartType = ChartType.LINE
    start_date: date | None = None
    end_date: date | None = None

class TrendInsight(BaseSchema):
    type: str  # e.g., "improvement", "decline", "stable"
    metric: str
    change: float
    message: str  # Поддерживающее сообщение пользователю

class LLMInsight(BaseSchema):
    summary: str  # Саммари заметок
    triggers: list[str]  # Выявленные триггеры
    recommendations: list[str]  # Советы на основе заметок

class AnalyticsResponse(BaseSchema):
    period: dict[str, Any]  # start, end, days
    statistics: dict[str, dict[str, float]]  # avg, min, max per metric
    weekday_patterns: dict[int, dict[str, float]]  # 0-6 day of week
    trends: list[TrendInsight]
    insights: LLMInsight | None = None
    records_count: int
    data_points: list[dict[str, Any]]  # Данные для графика (date, mood, anxiety, fatigue)
