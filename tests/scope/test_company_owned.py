import pytest
from django.core.exceptions import ValidationError

from src.company.models.location import Location
from src.company.models.location_type import LocationType


@pytest.fixture
def location_types(company_apple, company_google):
    return (
        LocationType(company=company_apple, slug="warehouse", name="Warehouse"),
        LocationType(company=company_google, slug="warehouse", name="Warehouse"),
    )


@pytest.mark.django_db
def test_save_accepts_relation_from_same_company(
    company_apple, activate_apple_context, location_types
):
    apple_type, _ = location_types
    apple_type.save()

    location = Location.add_root(
        company=company_apple,
        location_type=apple_type,
        slug="apple-root",
        name="Apple root",
    )

    assert location.pk is not None


@pytest.mark.django_db
def test_save_rejects_relation_from_another_company(
    company_apple, activate_apple_context, location_types
):
    _, google_type = location_types
    google_type.save()

    with pytest.raises(ValidationError) as exc_info:
        Location.add_root(
            company=company_apple,
            location_type=google_type,
            slug="invalid-root",
            name="Invalid root",
        )

    assert "location_type" in exc_info.value.message_dict


@pytest.mark.django_db
def test_save_rejects_relation_changed_to_another_company(
    company_apple, activate_apple_context, location_types
):
    apple_type, google_type = location_types
    apple_type.save()
    google_type.save()
    location = Location.add_root(
        company=company_apple,
        location_type=apple_type,
        slug="apple-root",
        name="Apple root",
    )

    location.location_type = google_type

    with pytest.raises(ValidationError) as exc_info:
        location.save()

    assert "location_type" in exc_info.value.message_dict


@pytest.mark.django_db
def test_tree_node_rejects_parent_from_another_company(
    company_apple, company_google, activate_apple_context, location_types
):
    apple_type, google_type = location_types
    apple_type.save()
    google_type.save()
    parent = Location.add_root(
        company=company_apple,
        location_type=apple_type,
        slug="apple-root",
        name="Apple root",
    )

    with pytest.raises(ValidationError) as exc_info:
        parent.add_child(
            company=company_google,
            location_type=google_type,
            slug="google-child",
            name="Google child",
        )

    assert "company" in exc_info.value.message_dict


@pytest.mark.django_db
def test_tree_node_rejects_move_to_another_company(
    company_apple, company_google, activate_apple_context, location_types
):
    apple_type, google_type = location_types
    apple_type.save()
    google_type.save()
    apple_root = Location.add_root(
        company=company_apple,
        location_type=apple_type,
        slug="apple-root",
        name="Apple root",
    )
    google_location = Location(
        company=company_google,
        location_type=google_type,
        slug="google-root",
        name="Google root",
    )

    with pytest.raises(ValidationError) as exc_info:
        apple_root.move(google_location, "sorted-child")

    assert "company" in exc_info.value.message_dict
