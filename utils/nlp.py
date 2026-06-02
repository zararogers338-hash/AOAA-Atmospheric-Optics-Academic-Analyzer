# -*- coding: utf-8 -*-
"""NLP analysis: TF-IDF, co-occurrence matrix, year trends, citation stats.

Chinese text support: jieba tokenization is used when available; falls back to
character-level n-grams otherwise.
"""

import re
from collections import Counter, defaultdict
from typing import List, Dict, Any, Optional, Tuple

import numpy as np
from utils.logger import log_info, log_warn, log_error

# ── Optional jieba for Chinese tokenization ──
_JIEBA_AVAILABLE = False
try:
    import jieba
    jieba.setLogLevel(20)  # Suppress jieba debug output
    _JIEBA_AVAILABLE = True
except ImportError:
    pass


def _tokenize_text(text: str) -> List[str]:
    """Tokenize text, using jieba for CJK content if available.

    Returns a list of tokens (words).
    """
    tokens: List[str] = []

    # Split text into CJK and non-CJK segments
    cjk_ranges = (
        ('一', '鿿'),   # CJK Unified
        ('㐀', '䶿'),   # CJK Extension A
        ('豈', '﫿'),   # CJK Compatibility
    )

    def _is_cjk(ch: str) -> bool:
        return any(lo <= ch <= hi for lo, hi in cjk_ranges)

    # Extract CJK runs and tokenize them
    segments: List[Tuple[bool, str]] = []
    if not text:
        return tokens

    buf = text[0]
    buf_is_cjk = _is_cjk(buf)
    for ch in text[1:]:
        is_cjk = _is_cjk(ch)
        if is_cjk == buf_is_cjk:
            buf += ch
        else:
            segments.append((buf_is_cjk, buf))
            buf = ch
            buf_is_cjk = is_cjk
    segments.append((buf_is_cjk, buf))

    for is_cjk, seg in segments:
        if is_cjk:
            if _JIEBA_AVAILABLE and len(seg) >= 2:
                tokens.extend([w for w in jieba.cut(seg) if len(w.strip()) >= 2])
            else:
                # Bigram fallback for Chinese without jieba
                tokens.extend([seg[i:i+2] for i in range(len(seg)-1)])
        else:
            # Non-CJK: extract word tokens
            words = re.findall(r'[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]|[a-zA-Z0-9]', seg)
            tokens.extend([w.lower() for w in words if len(w) >= 2])

    return tokens


def _tokenize_for_vectorizer(texts: List[str]) -> List[str]:
    """Tokenize a list of texts into space-separated strings for sklearn vectorizers."""
    return [" ".join(_tokenize_text(t)) for t in texts]


# ── Year extraction ──

def extract_year(text: str, metadata: dict) -> Optional[int]:
    """Extract publication year from metadata or text.

    Checks metadata keys, nested records_detail, and falls back to regex on text.
    """
    # From top-level metadata
    for key in ("year", "PY", "py", "Year", "date", "publication_year",
                "pubyear", "pub_year", "publication_date"):
        val = metadata.get(key)
        if val:
            try:
                # Handle list values
                s = str(val)
                if isinstance(val, list) and len(val) > 0:
                    s = str(val[0])
                # Extract first 4-digit year in range
                m = re.search(r"(19[5-9]\d|20[0-2]\d)", s)
                if m:
                    y = int(m.group(1))
                    if 1900 <= y <= 2100:
                        return y
            except (ValueError, TypeError):
                continue

    # From records_detail
    for rec in metadata.get("records_detail", []):
        for key in ("year", "PY", "date", "publication_year"):
            val = rec.get(key)
            if val:
                try:
                    s = str(val)
                    m = re.search(r"(19[5-9]\d|20[0-2]\d)", s)
                    if m:
                        y = int(m.group(1))
                        if 1900 <= y <= 2100:
                            return y
                except (ValueError, TypeError):
                    continue

    # Regex from first 5000 chars of text
    years = re.findall(r"\b(19[5-9]\d|20[0-2]\d)\b", text[:5000])
    if years:
        return int(Counter(years).most_common(1)[0][0])
    return None


# ── Citation extraction ──

def extract_citations(metadata: dict) -> Optional[int]:
    """Extract citation count from metadata."""
    for key in ("citations", "TC", "tc", "cited_by", "citation_count",
                "times_cited", "citedby", "citation-number"):
        val = metadata.get(key)
        if val is not None:
            try:
                return int(str(val).strip())
            except (ValueError, TypeError):
                continue
    for rec in metadata.get("records_detail", []):
        for key in ("citations", "TC", "cited_by", "times_cited"):
            val = rec.get(key)
            if val is not None:
                try:
                    return int(str(val).strip())
                except (ValueError, TypeError):
                    continue
    return None


def extract_keywords_from_metadata(metadata: dict) -> List[str]:
    """Extract keywords from metadata fields."""
    kws = []
    for key in ("keywords", "DE", "de", "Keywords", "keyword", "KW", "subject"):
        val = metadata.get(key)
        if val:
            kws.extend([k.strip() for k in str(val).replace(";", ",").split(",") if k.strip()])
    for rec in metadata.get("records_detail", []):
        for key in ("keywords", "DE", "KW", "keyword"):
            val = rec.get(key)
            if val:
                kws.extend([k.strip() for k in str(val).replace(";", ",").split(",") if k.strip()])
    return list(set(kws))


# ── TF-IDF ──

def compute_tfidf(texts: List[str], top_k: int = 20, max_features: int = 500) -> Dict[str, Any]:
    """Compute TF-IDF keywords for each document and corpus-wide."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
    except ImportError:
        log_error("scikit-learn not available for TF-IDF")
        return {"per_doc": [], "global_top": [], "feature_names": [], "matrix": None}

    if not texts:
        return {"per_doc": [], "global_top": [], "feature_names": [], "matrix": None}

    # Tokenize with jieba support
    tokenized = _tokenize_for_vectorizer(texts)

    vectorizer = TfidfVectorizer(
        max_features=max_features,
        stop_words="english",
        token_pattern=r"(?u)\b\w{2,}\b",
        max_df=0.95,
        min_df=1,
    )

    try:
        matrix = vectorizer.fit_transform(tokenized)
        feature_names = vectorizer.get_feature_names_out()
    except Exception as e:
        log_error("TF-IDF computation failed", e)
        return {"per_doc": [], "global_top": [], "feature_names": [], "matrix": None}

    # Per-document top keywords
    per_doc = []
    for i in range(matrix.shape[0]):
        row = matrix[i].toarray().flatten()
        top_indices = row.argsort()[-top_k:][::-1]
        doc_kws = [(str(feature_names[j]), float(row[j])) for j in top_indices if row[j] > 0]
        per_doc.append(doc_kws)

    # Global top keywords
    mean_scores = np.asarray(matrix.mean(axis=0)).flatten()
    top_global_idx = mean_scores.argsort()[-top_k * 2:][::-1]
    global_top = [(str(feature_names[j]), float(mean_scores[j])) for j in top_global_idx if mean_scores[j] > 0]

    log_info(f"TF-IDF computed: {matrix.shape[0]} docs, {len(feature_names)} features")
    return {
        "per_doc": per_doc,
        "global_top": global_top[:top_k],
        "feature_names": [str(f) for f in feature_names],
        "matrix": matrix,
    }


# ── Co-occurrence ──

def compute_cooccurrence(texts: List[str], top_k: int = 30, window: int = 5) -> Dict[str, Any]:
    """Compute keyword co-occurrence using a sliding window within each document.

    The *window* parameter is the number of tokens on each side; a pair of
    keywords co-occurs when they appear within *window* tokens of each other
    in the same document.
    """
    if not texts:
        return {"matrix": {}, "keywords": [], "edges": []}

    # Tokenize all texts
    token_lists = [_tokenize_text(t) for t in texts]

    # Collect all tokens for frequency ranking
    all_tokens = [tok for tl in token_lists for tok in tl]
    token_freq = Counter(all_tokens)

    # Select top keywords by frequency
    top_keywords = [kw for kw, _ in token_freq.most_common(top_k * 3)]
    top_set = set(top_keywords)

    # Sliding-window co-occurrence
    cooc_counter = Counter()
    for tokens in token_lists:
        n = len(tokens)
        for i in range(n):
            a = tokens[i]
            if a not in top_set:
                continue
            # Look at tokens within window to the right
            for j in range(i + 1, min(n, i + window + 1)):
                b = tokens[j]
                if b not in top_set or a == b:
                    continue
                pair = (a, b) if a < b else (b, a)
                cooc_counter[pair] += 1

    # Filter to top_k keywords
    final_kws = [kw for kw, _ in token_freq.most_common(top_k)]
    final_set = set(final_kws)

    # Build edge list
    edges = []
    for (a, b), w in cooc_counter.items():
        if a in final_set and b in final_set:
            edges.append({"source": a, "target": b, "weight": w})

    edges.sort(key=lambda x: x["weight"], reverse=True)
    log_info(f"Co-occurrence (window={window}): {len(final_kws)} keywords, {len(edges)} edges")

    # Build matrix dict for lookup
    matrix_dict: Dict[str, Dict[str, int]] = {}
    kw_to_idx = {kw: i for i, kw in enumerate(final_kws)}
    for edge in edges[:200]:
        s, t, w = edge["source"], edge["target"], edge["weight"]
        matrix_dict.setdefault(s, {})[t] = w
        matrix_dict.setdefault(t, {})[s] = w

    return {
        "matrix": matrix_dict,
        "keywords": final_kws,
        "edges": edges[:200],
    }


# ── Year trend ──

def compute_year_trend(parsed_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute year-based publication trend."""
    year_counts: Counter = Counter()
    year_citations: Dict[int, List[int]] = defaultdict(list)

    for r in parsed_results:
        year = extract_year(r.get("text", ""), r.get("metadata", {}))
        if year:
            year_counts[year] += 1
            cit = extract_citations(r.get("metadata", {}))
            if cit is not None:
                year_citations[year].append(cit)

    years = sorted(year_counts.keys())
    counts = [year_counts[y] for y in years]
    avg_citations = [float(np.mean(year_citations[y])) if year_citations[y] else 0.0 for y in years]

    return {
        "years": years,
        "counts": counts,
        "avg_citations": avg_citations,
        "total_with_year": sum(counts),
        "total_without_year": len(parsed_results) - sum(counts),
    }


# ── Citation stats ──

def compute_citation_stats(parsed_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute citation statistics."""
    citations = []
    for r in parsed_results:
        c = extract_citations(r.get("metadata", {}))
        if c is not None:
            citations.append(c)

    if not citations:
        return {"available": False, "count": 0}

    arr = np.array(citations, dtype=np.float64)
    return {
        "available": True,
        "count": len(citations),
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "max": int(np.max(arr)),
        "min": int(np.min(arr)),
        "std": float(np.std(arr)),
        "values": citations,
        "distribution": dict(Counter(citations)),
    }


# ── Full pipeline ──

def run_full_analysis(parsed_results: List[Dict[str, Any]], config: dict) -> Dict[str, Any]:
    """Run complete NLP analysis pipeline."""
    log_info(f"Starting full analysis on {len(parsed_results)} documents")
    top_k = config.get("tfidf_top_k", 20)
    window = config.get("cooccurrence_window", 5)

    texts = [r["text"] for r in parsed_results if r.get("text", "").strip()]
    if not texts:
        log_warn("No valid text found for analysis")
        return {"tfidf": {}, "cooccurrence": {}, "year_trend": {},
                "citation_stats": {}, "meta_keywords": {}, "doc_count": 0,
                "valid_text_count": 0}

    tfidf = compute_tfidf(texts, top_k=top_k)
    cooc = compute_cooccurrence(texts, top_k=top_k, window=window)
    trend = compute_year_trend(parsed_results)
    cit_stats = compute_citation_stats(parsed_results)

    # Extract all keywords from metadata
    all_meta_kws: List[str] = []
    for r in parsed_results:
        all_meta_kws.extend(extract_keywords_from_metadata(r.get("metadata", {})))
    meta_kw_counts = Counter(all_meta_kws)

    log_info("Full analysis complete")
    return {
        "tfidf": tfidf,
        "cooccurrence": cooc,
        "year_trend": trend,
        "citation_stats": cit_stats,
        "meta_keywords": dict(meta_kw_counts.most_common(50)),
        "doc_count": len(parsed_results),
        "valid_text_count": len(texts),
    }
