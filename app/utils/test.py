import pytest
from datetime import datetime, date, timedelta
from uuid import uuid4


class TestTrendsUtils:
    """Тесты для утилит трендов"""

    def test_detect_consecutive_threshold_true(self):
        from .trends import detect_consecutive_threshold

        records = [
            {"intensity": 8},
            {"intensity": 9},
            {"intensity": 7},
            {"intensity": 8},
            {"intensity": 9}
        ]

        result = detect_consecutive_threshold(
            records=records,
            metric_name="intensity",
            threshold=7,
            consecutive_days=3
        )

        assert result is True

    def test_detect_consecutive_threshold_false(self):
        from .trends import detect_consecutive_threshold

        records = [
            {"intensity": 8},
            {"intensity": 5},
            {"intensity": 7},
            {"intensity": 4},
            {"intensity": 6}
        ]

        result = detect_consecutive_threshold(
            records=records,
            metric_name="intensity",
            threshold=7,
            consecutive_days=3
        )

        assert result is False

    def test_calculate_metric_improvement_true(self):
        from .trends import calculate_metric_improvement

        records = [
            {"intensity": 3},
            {"intensity": 4},
            {"intensity": 5},
            {"intensity": 7},
            {"intensity": 8},
            {"intensity": 9}
        ]

        result = calculate_metric_improvement(
            records=records,
            metric_name="intensity",
            delta=3,
            period_days=6
        )

        assert result is True

    def test_get_weekday_patterns(self):
        from .trends import get_weekday_patterns

        records = [
            {"weekday": 0, "intensity": 5},
            {"weekday": 0, "intensity": 6},
            {"weekday": 1, "intensity": 7},
            {"weekday": 2, "intensity": 8},
            {"weekday": 2, "intensity": 9}
        ]

        result = get_weekday_patterns(records, "intensity")

        assert isinstance(result, dict)
        assert 0 in result
        assert 1 in result

    def test_calculate_moving_average(self):
        from .trends import calculate_moving_average

        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        result = calculate_moving_average(values, window_size=3)

        assert len(result) == 8
        assert result[0] == 2.0
        assert result[-1] == 9.0


class TestTimeUtils:
    """Тесты для временных утилит"""

    def test_convert_to_timezone(self):
        from .time_utils import convert_to_timezone

        dt_utc = datetime(2024, 1, 1, 12, 0, 0)

        result = convert_to_timezone(dt_utc, "Europe/Moscow")

        assert result is not None

    def test_convert_to_timezone_invalid(self):
        from .time_utils import convert_to_timezone

        dt_utc = datetime(2024, 1, 1, 12, 0, 0)

        # Несуществующая временная зона - вернет исходную дату
        result = convert_to_timezone(dt_utc, "Invalid/Timezone")

        assert result == dt_utc

    def test_get_user_day_start(self):
        from .time_utils import get_user_day_start

        result = get_user_day_start("Europe/Moscow")

        assert result is not None

    def test_is_within_notification_window_true(self):
        from .time_utils import is_within_notification_window

        # Имитируем время 14:30
        now_utc = datetime(2024, 1, 1, 11, 30, 0)

        result = is_within_notification_window(
            start_time="09:00",
            end_time="18:00",
            timezone_str="Europe/Moscow",
            now_utc=now_utc
        )

        assert result is True

    def test_calculate_streak(self):
        from .time_utils import calculate_streak

        today = date.today()
        yesterday = today - timedelta(days=1)
        two_days_ago = today - timedelta(days=2)

        records = [
            {"date": today},
            {"date": yesterday},
            {"date": two_days_ago}
        ]

        result = calculate_streak(records)

        assert result >= 0


class TestRecommendationsEngine:
    """Тесты для движка рекомендаций"""

    def test_select_recommendation_with_candidates(self):
        from .recommendations_engine import select_recommendation

        candidates = [
            {"id": "rec_001", "priority": 10, "title": "High Priority"},
            {"id": "rec_002", "priority": 5, "title": "Low Priority"}
        ]

        result = select_recommendation(
            candidates=candidates,
            recent_ids=[],
            context=None
        )

        assert result is not None
        assert result["id"] == "rec_001"

    def test_select_recommendation_no_candidates(self):
        from .recommendations_engine import select_recommendation

        result = select_recommendation(
            candidates=[],
            recent_ids=[],
            context=None
        )

        assert result is None

    def test_check_rotation_rule_first_time(self):
        from .recommendations_engine import check_rotation_rule

        result = check_rotation_rule(last_shown_date=None)

        assert result is True

    def test_check_rotation_rule_not_expired(self):
        from .recommendations_engine import check_rotation_rule

        last_shown = datetime.utcnow() - timedelta(days=3)

        result = check_rotation_rule(
            last_shown_date=last_shown,
            min_days_interval=7
        )

        assert result is False

    def test_contextualize_message_with_name(self):
        from .recommendations_engine import contextualize_message

        result = contextualize_message(
            message="Привет, {name}! {greeting}",
            hour=10,
            user_name="Анна"
        )

        assert "Анна" in result
        assert "Доброе утро" in result

    def test_categorize_trigger_high_intensity(self):
        from .recommendations_engine import categorize_trigger

        result = categorize_trigger(metric="intensity", value=9)

        assert result == "high_intensity"

    def test_categorize_trigger_low_intensity(self):
        from .recommendations_engine import categorize_trigger

        result = categorize_trigger(metric="intensity", value=2)

        assert result == "low_intensity"

    def test_categorize_trigger_sleep_deprivation(self):
        from .recommendations_engine import categorize_trigger

        result = categorize_trigger(metric="sleep_hours", value=5)

        assert result == "sleep_deprivation"

    def test_categorize_trigger_unknown(self):
        from .recommendations_engine import categorize_trigger

        result = categorize_trigger(metric="unknown", value=5)

        assert result is None


class TestValidators:
    """Тесты для валидаторов"""

    def test_validate_timezone_valid(self):
        from .validators import validate_timezone

        result = validate_timezone("Europe/Moscow")

        assert result is True

    def test_validate_timezone_invalid(self):
        from .validators import validate_timezone

        result = validate_timezone("Invalid/Timezone")

        assert result is False

    def test_validate_sleep_time_valid(self):
        from .validators import validate_sleep_time

        assert validate_sleep_time("23:00") is True
        assert validate_sleep_time("00:00") is True
        assert validate_sleep_time("12:30") is True

    def test_validate_sleep_time_invalid(self):
        from .validators import validate_sleep_time

        assert validate_sleep_time("25:00") is False
        assert validate_sleep_time("12:60") is False
        assert validate_sleep_time("invalid") is False

    def test_validate_note_content_valid(self):
        from .validators import validate_note_content

        result = validate_note_content("This is a normal note")

        assert result["is_valid"] is True
        assert result["error"] is None

    def test_validate_note_content_too_long(self):
        from .validators import validate_note_content

        long_note = "a" * 2000

        result = validate_note_content(long_note)

        assert result["is_valid"] is False
        assert "too long" in result["error"]

    def test_validate_note_content_xss(self):
        from .validators import validate_note_content

        result = validate_note_content("<script>alert('xss')</script>")

        assert result["is_valid"] is False
        assert "forbidden" in result["error"]

    def test_validate_password_strength_strong(self):
        from .validators import validate_password_strength

        result = validate_password_strength("StrongPass123!")

        assert result is True

    def test_validate_password_strength_weak(self):
        from .validators import validate_password_strength

        assert validate_password_strength("weak") is False
        assert validate_password_strength("nouppercase123") is False
        assert validate_password_strength("NOLOWERCASE123") is False
        assert validate_password_strength("NoNumbers!") is False
        assert validate_password_strength("") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])