from datetime import UTC, datetime

from abnb_guidance.leakage import FeatureObservation, eligible_for_view


EVENT_TIME = datetime(2024, 11, 7, 21, 5, tzinfo=UTC)


def observation(availability_class: str, public_time=None, management_time=None):
    return FeatureObservation(
        observation_id="D1",
        availability_class=availability_class,
        public_available_at_utc=public_time,
        known_to_management_by_utc=management_time,
    )


def test_post_event_observation_is_rejected_from_every_predictive_view():
    obs = observation(
        "post_event_ineligible",
        public_time=datetime(2025, 2, 1, tzinfo=UTC),
    )

    result = eligible_for_view(obs, EVENT_TIME, "management_information_view")

    assert result.eligible is False
    assert result.reason_code == "post_event"


def test_contemporaneous_actual_is_management_only():
    obs = observation("contemporaneous_management_known", management_time=EVENT_TIME)

    assert eligible_for_view(obs, EVENT_TIME, "management_information_view").eligible
    assert not eligible_for_view(obs, EVENT_TIME, "public_prior_view").eligible


def test_public_prior_requires_strictly_earlier_timestamp():
    same_time = observation("public_prior", public_time=EVENT_TIME)
    prior = observation(
        "public_prior",
        public_time=datetime(2024, 11, 7, 20, 59, tzinfo=UTC),
    )

    assert not eligible_for_view(same_time, EVENT_TIME, "public_prior_view").eligible
    assert eligible_for_view(prior, EVENT_TIME, "public_prior_view").eligible


def test_management_private_proxy_needs_separate_proxy_view():
    obs = observation("management_private_proxy", management_time=EVENT_TIME)

    assert not eligible_for_view(obs, EVENT_TIME, "management_information_view").eligible
    assert eligible_for_view(obs, EVENT_TIME, "management_proxy_view").eligible
