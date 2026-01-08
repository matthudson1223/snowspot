"""Initial schema with all tables

Revision ID: 4930e9a489c5
Revises:
Create Date: 2026-01-08 19:36:13.581878

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "4930e9a489c5"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all initial tables."""

    # Create resorts table
    op.create_table(
        "resorts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("latitude", sa.DECIMAL(precision=10, scale=8), nullable=False),
        sa.Column("longitude", sa.DECIMAL(precision=11, scale=8), nullable=False),
        sa.Column(
            "timezone", sa.String(length=50), nullable=False, server_default="America/Denver"
        ),
        sa.Column("region", sa.String(length=100), nullable=True),
        sa.Column("state", sa.String(length=50), nullable=True),
        sa.Column("country", sa.String(length=50), server_default="USA", nullable=True),
        sa.Column("base_elevation_ft", sa.Integer(), nullable=True),
        sa.Column("summit_elevation_ft", sa.Integer(), nullable=True),
        sa.Column("vertical_drop_ft", sa.Integer(), nullable=True),
        sa.Column("total_lifts", sa.Integer(), nullable=True),
        sa.Column("total_runs", sa.Integer(), nullable=True),
        sa.Column("total_acres", sa.Integer(), nullable=True),
        sa.Column("official_url", sa.String(length=500), nullable=True),
        sa.Column("data_source_config", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("snotel_station_ids", sa.ARRAY(sa.Text()), nullable=True),
        sa.Column("weather_station_id", sa.String(length=50), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_resorts_id"), "resorts", ["id"], unique=False)
    op.create_index(op.f("ix_resorts_slug"), "resorts", ["slug"], unique=True)
    op.create_index(op.f("ix_resorts_state"), "resorts", ["state"], unique=False)
    op.create_index(op.f("ix_resorts_is_active"), "resorts", ["is_active"], unique=False)

    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("favorite_resort_ids", sa.ARRAY(sa.Integer()), nullable=True),
        sa.Column(
            "timezone", sa.String(length=50), server_default="America/Denver", nullable=True
        ),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=True),
        sa.Column("email_verified", sa.Boolean(), server_default="false", nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("last_login", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    # Create snotel_stations table
    op.create_table(
        "snotel_stations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("station_id", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("latitude", sa.DECIMAL(precision=10, scale=8), nullable=True),
        sa.Column("longitude", sa.DECIMAL(precision=11, scale=8), nullable=True),
        sa.Column("elevation_ft", sa.Integer(), nullable=True),
        sa.Column("state", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("station_id"),
    )
    op.create_index(op.f("ix_snotel_stations_id"), "snotel_stations", ["id"], unique=False)
    op.create_index(
        op.f("ix_snotel_stations_station_id"), "snotel_stations", ["station_id"], unique=True
    )

    # Create conditions table (time-series)
    op.create_table(
        "conditions",
        sa.Column("time", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("resort_id", sa.Integer(), nullable=False),
        sa.Column("base_depth_in", sa.DECIMAL(precision=6, scale=2), nullable=True),
        sa.Column("summit_depth_in", sa.DECIMAL(precision=6, scale=2), nullable=True),
        sa.Column("new_snow_24h_in", sa.DECIMAL(precision=6, scale=2), nullable=True),
        sa.Column("new_snow_48h_in", sa.DECIMAL(precision=6, scale=2), nullable=True),
        sa.Column("new_snow_7d_in", sa.DECIMAL(precision=6, scale=2), nullable=True),
        sa.Column("temperature_f", sa.DECIMAL(precision=5, scale=2), nullable=True),
        sa.Column("wind_speed_mph", sa.DECIMAL(precision=5, scale=2), nullable=True),
        sa.Column("wind_direction", sa.Integer(), nullable=True),
        sa.Column("precipitation_in", sa.DECIMAL(precision=6, scale=3), nullable=True),
        sa.Column("humidity_percent", sa.Integer(), nullable=True),
        sa.Column("visibility_miles", sa.DECIMAL(precision=5, scale=2), nullable=True),
        sa.Column("lifts_open", sa.Integer(), nullable=True),
        sa.Column("lifts_total", sa.Integer(), nullable=True),
        sa.Column("runs_open", sa.Integer(), nullable=True),
        sa.Column("runs_total", sa.Integer(), nullable=True),
        sa.Column("terrain_parks_open", sa.Integer(), nullable=True),
        sa.Column("snow_quality_score", sa.DECIMAL(precision=5, scale=2), nullable=True),
        sa.Column("skiability_index", sa.DECIMAL(precision=5, scale=2), nullable=True),
        sa.Column("crowd_level", sa.Integer(), nullable=True),
        sa.Column("data_sources", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("confidence_score", sa.DECIMAL(precision=4, scale=3), nullable=True),
        sa.ForeignKeyConstraint(["resort_id"], ["resorts.id"]),
        sa.PrimaryKeyConstraint("time", "resort_id"),
        sa.CheckConstraint(
            "snow_quality_score >= 0 AND snow_quality_score <= 100",
            name="check_snow_quality_score_range",
        ),
        sa.CheckConstraint(
            "skiability_index >= 0 AND skiability_index <= 100",
            name="check_skiability_index_range",
        ),
        sa.CheckConstraint("crowd_level >= 1 AND crowd_level <= 5", name="check_crowd_level_range"),
    )

    # Create snotel_readings table (time-series)
    op.create_table(
        "snotel_readings",
        sa.Column("time", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("station_id", sa.String(length=50), nullable=False),
        sa.Column("snow_depth_in", sa.DECIMAL(precision=6, scale=2), nullable=True),
        sa.Column("snow_water_equivalent_in", sa.DECIMAL(precision=6, scale=2), nullable=True),
        sa.Column("temperature_f", sa.DECIMAL(precision=5, scale=2), nullable=True),
        sa.Column("precipitation_in", sa.DECIMAL(precision=6, scale=3), nullable=True),
        sa.PrimaryKeyConstraint("time", "station_id"),
    )

    # Create weather_forecasts table
    op.create_table(
        "weather_forecasts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("resort_id", sa.Integer(), nullable=False),
        sa.Column("generated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("forecast_for", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("temperature_high_f", sa.DECIMAL(precision=5, scale=2), nullable=True),
        sa.Column("temperature_low_f", sa.DECIMAL(precision=5, scale=2), nullable=True),
        sa.Column("predicted_snowfall_in", sa.DECIMAL(precision=6, scale=2), nullable=True),
        sa.Column("wind_speed_mph", sa.DECIMAL(precision=5, scale=2), nullable=True),
        sa.Column("precipitation_prob_percent", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(length=50), nullable=True),
        sa.Column("model", sa.String(length=50), nullable=True),
        sa.Column("confidence", sa.DECIMAL(precision=4, scale=3), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["resort_id"], ["resorts.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "resort_id", "forecast_for", "generated_at", "source", name="uq_forecast_resort_time_source"
        ),
    )
    op.create_index(op.f("ix_weather_forecasts_id"), "weather_forecasts", ["id"], unique=False)

    # Create webcams table
    op.create_table(
        "webcams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("resort_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=True),
        sa.Column("position", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["resort_id"], ["resorts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_webcams_id"), "webcams", ["id"], unique=False)

    # Create webcam_snapshots table
    op.create_table(
        "webcam_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("webcam_id", sa.Integer(), nullable=False),
        sa.Column("captured_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("visibility_rating", sa.Integer(), nullable=True),
        sa.Column("snow_visible", sa.Boolean(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["webcam_id"], ["webcams.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_webcam_snapshots_id"), "webcam_snapshots", ["id"], unique=False)
    op.create_index(
        op.f("ix_webcam_snapshots_captured_at"), "webcam_snapshots", ["captured_at"], unique=False
    )

    # Create alerts table
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("resort_id", sa.Integer(), nullable=False),
        sa.Column("alert_type", sa.String(length=50), nullable=False),
        sa.Column("threshold_config", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("delivery_method", sa.String(length=20), server_default="email", nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=True),
        sa.Column("last_triggered_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("trigger_count", sa.Integer(), server_default="0", nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["resort_id"], ["resorts.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_alerts_id"), "alerts", ["id"], unique=False)
    op.create_index(op.f("ix_alerts_user_id"), "alerts", ["user_id"], unique=False)
    op.create_index(op.f("ix_alerts_resort_id"), "alerts", ["resort_id"], unique=False)
    op.create_index(op.f("ix_alerts_is_active"), "alerts", ["is_active"], unique=False)

    # Create scraper_runs table
    op.create_table(
        "scraper_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("scraper_name", sa.String(length=100), nullable=False),
        sa.Column("resort_id", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("completed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.DECIMAL(precision=10, scale=3), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("records_collected", sa.Integer(), server_default="0", nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("error_details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("version", sa.String(length=20), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["resort_id"], ["resorts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_scraper_runs_id"), "scraper_runs", ["id"], unique=False)
    op.create_index(op.f("ix_scraper_runs_scraper_name"), "scraper_runs", ["scraper_name"], unique=False)
    op.create_index(op.f("ix_scraper_runs_status"), "scraper_runs", ["status"], unique=False)

    # Create data_quality_checks table
    op.create_table(
        "data_quality_checks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("check_name", sa.String(length=100), nullable=False),
        sa.Column("resort_id", sa.Integer(), nullable=True),
        sa.Column("executed_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("issue_description", sa.Text(), nullable=True),
        sa.Column("severity", sa.String(length=20), nullable=True),
        sa.Column("affected_records", sa.Integer(), nullable=True),
        sa.Column("check_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(["resort_id"], ["resorts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_data_quality_checks_id"), "data_quality_checks", ["id"], unique=False)


def downgrade() -> None:
    """Drop all tables in reverse order."""
    op.drop_index(op.f("ix_data_quality_checks_id"), table_name="data_quality_checks")
    op.drop_table("data_quality_checks")

    op.drop_index(op.f("ix_scraper_runs_status"), table_name="scraper_runs")
    op.drop_index(op.f("ix_scraper_runs_scraper_name"), table_name="scraper_runs")
    op.drop_index(op.f("ix_scraper_runs_id"), table_name="scraper_runs")
    op.drop_table("scraper_runs")

    op.drop_index(op.f("ix_alerts_is_active"), table_name="alerts")
    op.drop_index(op.f("ix_alerts_resort_id"), table_name="alerts")
    op.drop_index(op.f("ix_alerts_user_id"), table_name="alerts")
    op.drop_index(op.f("ix_alerts_id"), table_name="alerts")
    op.drop_table("alerts")

    op.drop_index(op.f("ix_webcam_snapshots_captured_at"), table_name="webcam_snapshots")
    op.drop_index(op.f("ix_webcam_snapshots_id"), table_name="webcam_snapshots")
    op.drop_table("webcam_snapshots")

    op.drop_index(op.f("ix_webcams_id"), table_name="webcams")
    op.drop_table("webcams")

    op.drop_index(op.f("ix_weather_forecasts_id"), table_name="weather_forecasts")
    op.drop_table("weather_forecasts")

    op.drop_table("snotel_readings")

    op.drop_table("conditions")

    op.drop_index(op.f("ix_snotel_stations_station_id"), table_name="snotel_stations")
    op.drop_index(op.f("ix_snotel_stations_id"), table_name="snotel_stations")
    op.drop_table("snotel_stations")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")

    op.drop_index(op.f("ix_resorts_is_active"), table_name="resorts")
    op.drop_index(op.f("ix_resorts_state"), table_name="resorts")
    op.drop_index(op.f("ix_resorts_slug"), table_name="resorts")
    op.drop_index(op.f("ix_resorts_id"), table_name="resorts")
    op.drop_table("resorts")
