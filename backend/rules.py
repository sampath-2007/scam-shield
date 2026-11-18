"""Rule-based message analysis, kept separate from the FastAPI routes."""

import difflib
import ipaddress
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


_CONFIG_PATH = Path(__file__).with_name("rules.json")
with _CONFIG_PATH.open(encoding="utf-8") as config_file:
    _CONFIG: dict[str, Any] = json.load(config_file)

_RULES = _CONFIG["rules"]
_COMPILED_PATTERNS = {
    rule["code"]: [re.compile(pattern, re.IGNORECASE) for pattern in rule["patterns"]]
    for rule in _RULES
}
_OTP_NOTICE_CONFIG = _CONFIG["otp_notice"]
_OTP_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in _OTP_NOTICE_CONFIG["otp_patterns"]
]
_OTP_DISCLAIMER_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in _OTP_NOTICE_CONFIG["disclaimer_patterns"]
]
_OTP_DISCLAIMER_REMOVAL_PATTERN = re.compile(
    _OTP_NOTICE_CONFIG["disclaimer_removal_pattern"],
    re.IGNORECASE,
)
_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?;।])\s+|[\r\n]+")
_URL_PATTERN = re.compile(
    r"(?<![@\w])(?:https?://|www\.)[^\s<>\"']+"
    r"|(?<![@\w])(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"[a-z]{2,63}(?::\d{1,5})?(?:/[^\s<>\"']*)?",
    re.IGNORECASE,
)


def _localized_rule(rule: dict[str, Any]) -> dict[str, Any]:
    return {
        "code": rule["code"],
        "risk_weight": rule["weight"],
        "explanations": rule["explanations"],
    }


def _extract_links(text: str) -> list[str]:
    links: list[str] = []
    for match in _URL_PATTERN.finditer(text):
        link = match.group(0).rstrip(".,;:!?)]}")
        if link and link not in links:
            links.append(link)
    return links


def _domain_for(link: str) -> str | None:
    candidate = link if "://" in link else f"//{link}"
    try:
        return urlsplit(candidate).hostname
    except ValueError:
        return None


def _is_official_domain(host: str, official_domains: list[str]) -> bool:
    return any(host == domain or host.endswith(f".{domain}") for domain in official_domains)


def _is_lookalike_domain(host: str) -> bool:
    for details in _CONFIG["brands"].values():
        if _is_official_domain(host, details["official_domains"]):
            continue

        labels = host.split(".")
        aliases = details["aliases"]
        if any(alias in label for alias in aliases for label in labels):
            return True

        for label in labels:
            for alias in aliases:
                if len(alias) >= 4 and difflib.SequenceMatcher(None, alias, label).ratio() >= 0.82:
                    return True
    return False


def _has_suspicious_domain_signal(host: str, link: str) -> bool:
    if "@" in link:
        return True
    if host.startswith("xn--") or ".xn--" in host:
        return True

    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        pass

    top_level_domain = host.rsplit(".", 1)[-1]
    if top_level_domain in _CONFIG["risky_tlds"]:
        return True

    return any(
        re.search(pattern, host, re.IGNORECASE)
        for pattern in _CONFIG["suspicious_domain_patterns"]
    )


def _messages_for(language: str) -> dict[str, str]:
    return _CONFIG["verdict_explanations"][language]


def _has_legitimate_otp_notice(text: str) -> bool:
    sentences = [sentence for sentence in _SENTENCE_BOUNDARY.split(text) if sentence.strip()]
    for index, sentence in enumerate(sentences):
        if not any(pattern.search(sentence) for pattern in _OTP_PATTERNS):
            continue

        # A warning may follow the code sentence, but must be in the same or adjacent sentence.
        nearby_sentences = sentences[max(0, index - 1) : min(len(sentences), index + 2)]
        if any(
            pattern.search(nearby_sentence)
            for nearby_sentence in nearby_sentences
            for pattern in _OTP_DISCLAIMER_PATTERNS
        ):
            return True
    return False


def analyze_message(text: str, language: str = "en") -> dict[str, Any]:
    """Return a weighted risk score, matched reasons, and extracted links."""
    links = _extract_links(text)
    matched_codes: set[str] = set()
    matched_rules: list[dict[str, Any]] = []

    legitimate_otp_notice = _has_legitimate_otp_notice(text)

    for rule in _RULES:
        code = rule["code"]
        if code == "LEGITIMATE_OTP_NOTICE":
            is_match = legitimate_otp_notice
        elif code in {"SUSPICIOUS_SHORT_LINK", "SUSPICIOUS_WEBSITE_DOMAIN", "LOOKALIKE_DOMAIN"}:
            domains = [(link, _domain_for(link)) for link in links]
            if code == "SUSPICIOUS_SHORT_LINK":
                shorteners = _CONFIG["short_link_domains"]
                is_match = any(
                    host is not None
                    and any(host == domain or host.endswith(f".{domain}") for domain in shorteners)
                    for _, host in domains
                )
            elif code == "LOOKALIKE_DOMAIN":
                is_match = any(host is not None and _is_lookalike_domain(host) for _, host in domains)
            else:
                is_match = any(
                    host is not None and _has_suspicious_domain_signal(host, link)
                    for link, host in domains
                )
        elif code == "CREDENTIAL_REQUEST":
            credential_text = text
            if legitimate_otp_notice:
                # Ignore disclaimer clauses only; other credential requests remain detectable.
                credential_text = _OTP_DISCLAIMER_REMOVAL_PATTERN.sub("", text)
            is_match = any(
                pattern.search(credential_text) for pattern in _COMPILED_PATTERNS[code]
            )
        else:
            is_match = any(pattern.search(text) for pattern in _COMPILED_PATTERNS[code])

        if is_match and code not in matched_codes:
            matched_codes.add(code)
            matched_rules.append(rule)

    score = min(100, sum(rule["weight"] for rule in matched_rules))
    if score >= 60:
        verdict = "SCAM"
    elif score >= 30:
        verdict = "SUSPICIOUS"
    else:
        verdict = "SAFE"

    verdict_explanations = _messages_for(language)
    return {
        "verdict": verdict,
        "score": score,
        "reasons": [_localized_rule(rule) for rule in matched_rules],
        "extracted_links": links,
        "explanation": verdict_explanations[verdict],
        "language": language,
    }
