import pytest

from backend.services.providers.base_provider import BaseAIProvider


def test_base_provider_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BaseAIProvider()


def test_concrete_provider_uses_base_health_check():
    class TestProvider(BaseAIProvider):

        @property
        def provider_name(self) -> str:
            return "TestProvider"

        def review_code(
            self,
            code: str,
            language: str,
        ) -> dict:
            return {
                "success": True,
                "summary": "Test review.",
                "issues": [],
            }

    provider = TestProvider()

    assert provider.health_check() is True


def test_concrete_provider_implements_abstract_interface():
    class TestProvider(BaseAIProvider):

        @property
        def provider_name(self) -> str:
            return "TestProvider"

        def review_code(
            self,
            code: str,
            language: str,
        ) -> dict:
            return {
                "success": True,
                "summary": "Test review.",
                "issues": [],
            }

    provider = TestProvider()

    assert provider.provider_name == "TestProvider"

    result = provider.review_code(
        "print('hello')",
        "Python",
    )

    assert result["success"] is True