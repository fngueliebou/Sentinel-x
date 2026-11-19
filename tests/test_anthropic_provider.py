"""Unit tests for AnthropicProvider response handling - NO network, NO API key"""

from __future__ import annotations

import sys
import types

import pytest

from sentinelx.llm.anthropic_provider import AnthropicProvider, AnthropicResponseError
from sentinelx.llm.base import AnalysisRequest
from sentinelx.schemas import Disposition, Evidence, NormalizedAlert, Severity, SourceType


class _FakeAPIError(Exception):
    """Stand-in for an SDK/network error raised by messages.create()."""


def _install_fake_anthropic(monkeypatch, *, text=None, exc=None, usage=(11, 22)) -> None:

    module = types.ModuleType("anthropic")

    class _Block:
        def __init__(self, t: str) -> None:
            self.type = "text"
            self.text = t

    class _Usage:
        def __init__(self, i: int, o: int) -> None:
            self.input_tokens = i
            self.output_tokens = o

    class _Resp:
        def __init__(self, t: str) -> None:
            self.content = [_Block(t)]
            self.usage = _Usage(*usage)

    class _Messages:
        def create(self, **kwargs):
            if exc is not None:
                raise exc
            return _Resp(text)

    class Anthropic:
        def __init__(self, api_key=None) -> None:
            self.messages = _Messages()

    module.Anthropic = Anthropic  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "anthropic", module)


def _request() -> AnalysisRequest:
    alert = NormalizedAlert(
        id="A1", source="wazuh", timestamp="2022-01-18T13:14:31Z",
        title="t", severity=Severity.LOW,
    )
    ev = Evidence(id="EV-EVENT-1", source_type=SourceType.EVENT, source_ref="event:e1", content="x")
    return AnalysisRequest(alert=alert, evidence=[ev], prompt_version="inv-prompt-v1")


def _provider() -> AnthropicProvider:
    # Non-empty key/model satisfy the constructor; neither is ever sent anywhere (mock).
    return AnthropicProvider(api_key="test-key", model="claude-sonnet-5-5")


_VALID = (
    '{"disposition":"escalate","summary":"Priv-esc chain observed.",'
    '"facts":[{"statement":"sudo cat /etc/shadow","citations":[{"evidence_id":"EV-EVENT-1"}]}],'
    '"hypotheses":[],'
    '"unknowns":[{"statement":"initial access vector unknown"}],'
    '"recommendations":[{"statement":"review the sudo events"}]}'
)


def test_valid_json_response(monkeypatch):
    _install_fake_anthropic(monkeypatch, text=_VALID)
    out = _provider().analyze(_request())
    assert out.disposition is Disposition.ESCALATE
    assert out.summary.startswith("Priv-esc")
    assert len(out.facts) == 1
    assert out.facts[0].citations[0].evidence_id == "EV-EVENT-1"
    assert len(out.unknowns) == 1 and out.unknowns[0].citations == []
    assert out.model == "claude-sonnet-5-5"
    assert out.usage.input_tokens == 11 and out.usage.output_tokens == 22


def test_json_wrapped_in_markdown_fences(monkeypatch):
    fenced = "```json\n" + _VALID + "\n```"
    _install_fake_anthropic(monkeypatch, text=fenced)
    out = _provider().analyze(_request())
    assert out.disposition is Disposition.ESCALATE
    assert len(out.facts) == 1


def test_invalid_json_raises(monkeypatch):
    _install_fake_anthropic(monkeypatch, text="this is not JSON at all")
    with pytest.raises(AnthropicResponseError):
        _provider().analyze(_request())


def test_unknown_disposition_raises(monkeypatch):
    _install_fake_anthropic(monkeypatch, text='{"disposition":"explode","summary":"x"}')
    with pytest.raises(AnthropicResponseError):
        _provider().analyze(_request())


def test_missing_required_field_raises(monkeypatch):
    # 'summary' absent.
    _install_fake_anthropic(monkeypatch, text='{"disposition":"escalate"}')
    with pytest.raises(AnthropicResponseError):
        _provider().analyze(_request())


def test_wrong_field_type_raises(monkeypatch):
    # 'summary' is a number, not a string.
    _install_fake_anthropic(monkeypatch, text='{"disposition":"escalate","summary":123}')
    with pytest.raises(AnthropicResponseError):
        _provider().analyze(_request())


def test_fact_without_citation_raises(monkeypatch):
    # The ProviderOutput/Finding contract requires every FACT to cite evidence.
    _install_fake_anthropic(
        monkeypatch,
        text='{"disposition":"escalate","summary":"s","facts":[{"statement":"ungrounded"}]}',
    )
    with pytest.raises(AnthropicResponseError):
        _provider().analyze(_request())


def test_api_error_propagates_without_deterministic_fallback(monkeypatch):
    _install_fake_anthropic(monkeypatch, exc=_FakeAPIError("boom"))
    # The SDK error must propagate as-is - NOT be swallowed or replaced by a
    # deterministic ProviderOutput.
    with pytest.raises(_FakeAPIError):
        _provider().analyze(_request())