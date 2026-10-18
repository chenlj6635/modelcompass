"""Stable vocabulary used by the ModelCompass data contracts."""

from typing import Final

ABILITY_CLUSTERS: Final[frozenset[str]] = frozenset({
    "general", "reasoning", "mathematics", "science_reasoning", "software_engineering",
    "code_generation", "agent_tools", "long_context", "instruction_following", "chinese", "multimodal",
})
SOURCE_TYPES: Final[frozenset[str]] = frozenset({"official", "third_party", "manual"})
REPRODUCIBILITY_LEVELS: Final[frozenset[str]] = frozenset({"high", "medium", "low", "unknown"})
CONFIDENCE_LEVELS: Final[frozenset[str]] = frozenset({"high", "medium", "low", "unknown"})
SNAPSHOT_STATUSES: Final[frozenset[str]] = frozenset({"success", "stale", "source_changed", "parse_failed", "fetch_failed"})
