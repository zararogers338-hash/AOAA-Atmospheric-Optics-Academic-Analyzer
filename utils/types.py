# -*- coding: utf-8 -*-
"""Shared data structures for AOAA analysis results.

All analysis pipeline outputs conform to these types so that consumers
(UI, exports, AI backends) don't need to guess dict shapes.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class ParseResult:
    """Single file parse output."""
    text: str
    success: bool = True
    format: str = "txt"
    error: Optional[str] = None
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class KeywordScore:
    """A keyword with its TF-IDF or match score."""
    keyword: str
    score: float = 0.0


@dataclass
class MatchedKeyword:
    """Keyword matched to a phenomenon with extended stats."""
    keyword: str
    tfidf: float = 0.0
    match_score: float = 0.0
    connections: int = 0


@dataclass
class CooccurrenceEdge:
    """An edge in the co-occurrence graph."""
    source: str
    target: str
    weight: int = 0


@dataclass
class TFIDFResult:
    """TF-IDF analysis result."""
    per_doc: List[List[Tuple[str, float]]] = field(default_factory=list)
    global_top: List[Tuple[str, float]] = field(default_factory=list)
    feature_names: List[str] = field(default_factory=list)
    matrix: object = None  # scipy sparse matrix


@dataclass
class CooccurrenceResult:
    """Co-occurrence analysis result."""
    matrix: Dict[str, Dict[str, int]] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    edges: List[Dict] = field(default_factory=list)


@dataclass
class YearTrendResult:
    """Year-based publication trend."""
    years: List[int] = field(default_factory=list)
    counts: List[int] = field(default_factory=list)
    avg_citations: List[float] = field(default_factory=list)
    total_with_year: int = 0
    total_without_year: int = 0


@dataclass
class CitationStatsResult:
    """Citation statistics."""
    available: bool = False
    count: int = 0
    mean: float = 0.0
    median: float = 0.0
    max: int = 0
    min: int = 0
    std: float = 0.0
    values: List[int] = field(default_factory=list)
    distribution: Dict[int, int] = field(default_factory=dict)


@dataclass
class AtmosphereZoneEntry:
    """A single entry in an atmosphere zone."""
    keyword: str
    tfidf: float = 0.0
    betweenness: float = 0.0


@dataclass
class AtmosphereResult:
    """Atmosphere classification result."""
    high_pressure: List[Dict] = field(default_factory=list)
    low_pressure: List[Dict] = field(default_factory=list)
    fronts: List[Dict] = field(default_factory=list)
    jet_streams: List[Dict] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Full analysis pipeline output."""
    tfidf: Dict = field(default_factory=dict)
    cooccurrence: Dict = field(default_factory=dict)
    year_trend: Dict = field(default_factory=dict)
    citation_stats: Dict = field(default_factory=dict)
    meta_keywords: Dict[str, int] = field(default_factory=dict)
    doc_count: int = 0
    valid_text_count: int = 0
