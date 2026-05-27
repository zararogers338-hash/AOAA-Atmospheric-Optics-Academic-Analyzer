# -*- coding: utf-8 -*-
"""NLP analysis: TF-IDF, co-occurrence matrix, year trends, citation stats."""

import re
from collections import Counter, defaultdict
from typing import List, Dict, Any, Tuple, Optional

import numpy as np
from utils.logger import log_info, log_warn, log_error


def extract_year(text: str, metadata: dict) -> Optional[int]:
    """Extract publication year from metadata or text."""
    # From metadata
    for key in ["year", "PY", "py", "Year", "date", "publication_year"]:
        val = metadata.get(key)
        if val:
            try:
                y = int(str(val).strip()[:4])
                if 1900 <= y <= 2100:
                    return y
            except (ValueError, TypeError):
                continue
    # From records_detail
    for rec in metadata.get("records_detail", []):
        if "year" in rec:
            try:
                y = int(str(rec["year"]).strip()[:4])
                if 1900 <= y <= 2100:
                    return y
            except (ValueError, TypeError):
                continue
    # Regex from text
    years = re.findall(r"\b(19[5-9]\d|20[0-2]\d)\b", text[:5000])
    if years:
        return int(Counter(years).most_common(1)[0][0])
    return None


def extract_citations(metadata: dict) -> Optional[int]:
    """Extract citation count from metadata."""
    for key in ["citations", "TC", "tc", "cited_by", "citation_count"]:
        val = metadata.get(key)
        if val is not None:
            try:
                return int(str(val).strip())
            except (ValueError, TypeError):
                continue
    for rec in metadata.get("records_detail", []):
        if "citations" in rec:
            try:
                return int(str(rec["citations"]).strip())
            except (ValueError, TypeError):
                continue
    return None


def extract_keywords_from_metadata(metadata: dict) -> List[str]:
    """Extract keywords from metadata fields."""
    kws = []
    for key in ["keywords", "DE", "de", "Keywords", "keyword"]:
        val = metadata.get(key)
        if val:
            kws.extend([k.strip() for k in str(val).replace(";", ",").split(",") if k.strip()])
    for rec in metadata.get("records_detail", []):
        if "keywords" in rec:
            kws.extend([k.strip() for k in str(rec["keywords"]).replace(";", ",").split(",") if k.strip()])
    return list(set(kws))


def compute_tfidf(texts: List[str], top_k: int = 20, max_features: int = 500) -> Dict[str, Any]:
    """Compute TF-IDF keywords for each document and corpus-wide."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
    except ImportError:
        log_error("scikit-learn not available for TF-IDF")
        return {"per_doc": [], "global_top": [], "feature_names": [], "matrix": None}

    if not texts:
        return {"per_doc": [], "global_top": [], "feature_names": [], "matrix": None}

    vectorizer = TfidfVectorizer(
        max_features=max_features,
        stop_words="english",
        token_pattern=r"(?u)\b[a-zA-Z\u4e00-\u9fff]{2,}\b",
        max_df=0.95,
        min_df=1
    )

    try:
        matrix = vectorizer.fit_transform(texts)
        feature_names = vectorizer.get_feature_names_out()
    except Exception as e:
        log_error("TF-IDF computation failed", e)
        return {"per_doc": [], "global_top": [], "feature_names": [], "matrix": None}

    # Per-document top keywords
    per_doc = []
    for i in range(matrix.shape[0]):
        row = matrix[i].toarray().flatten()
        top_indices = row.argsort()[-top_k:][::-1]
        doc_kws = [(feature_names[j], float(row[j])) for j in top_indices if row[j] > 0]
        per_doc.append(doc_kws)

    # Global top keywords
    mean_scores = np.asarray(matrix.mean(axis=0)).flatten()
    top_global_idx = mean_scores.argsort()[-top_k * 2:][::-1]
    global_top = [(feature_names[j], float(mean_scores[j])) for j in top_global_idx if mean_scores[j] > 0]

    log_info(f"TF-IDF computed: {matrix.shape[0]} docs, {len(feature_names)} features")
    return {
        "per_doc": per_doc,
        "global_top": global_top[:top_k],
        "feature_names": list(feature_names),
        "matrix": matrix
    }


def compute_cooccurrence(texts: List[str], top_k: int = 30, window: int = 5) -> Dict[str, Any]:
    """Compute keyword co-occurrence matrix using window method."""
    from sklearn.feature_extraction.text import CountVectorizer

    if not texts:
        return {"matrix": {}, "keywords": [], "edges": []}

    vectorizer = CountVectorizer(
        max_features=top_k * 3,
        stop_words="english",
        token_pattern=r"(?u)\b[a-zA-Z\u4e00-\u9fff]{2,}\b",
        max_df=0.95,
        min_df=1
    )

    try:
        count_matrix = vectorizer.fit_transform(texts)
        feature_names = list(vectorizer.get_feature_names_out())
    except Exception as e:
        log_error("Co-occurrence computation failed", e)
        return {"matrix": {}, "keywords": [], "edges": []}

    # Co-occurrence: dot product of binary matrix
    binary = (count_matrix > 0).astype(int)
    cooc = (binary.T @ binary).toarray()
    np.fill_diagonal(cooc, 0)

    # Top keywords by frequency
    freq = np.asarray(count_matrix.sum(axis=0)).flatten()
    top_idx = freq.argsort()[-top_k:][::-1]
    keywords = [feature_names[i] for i in top_idx]

    # Build edge list
    edges = []
    idx_set = set(top_idx)
    for i in top_idx:
        for j in top_idx:
            if i < j and cooc[i][j] > 0:
                edges.append({
                    "source": feature_names[i],
                    "target": feature_names[j],
                    "weight": int(cooc[i][j])
                })

    edges.sort(key=lambda x: x["weight"], reverse=True)
    log_info(f"Co-occurrence: {len(keywords)} keywords, {len(edges)} edges")

    # Build safe index lookup
    fn_idx = {name: i for i, name in enumerate(feature_names)}
    matrix_dict = {}
    for kw in keywords:
        if kw not in fn_idx:
            continue
        row = {}
        for kw2 in keywords:
            if kw2 == kw or kw2 not in fn_idx:
                continue
            val = int(cooc[fn_idx[kw]][fn_idx[kw2]])
            if val > 0:
                row[kw2] = val
        matrix_dict[kw] = row

    return {
        "matrix": matrix_dict,
        "keywords": keywords,
        "edges": edges[:200]  # Limit edges
    }


def compute_year_trend(parsed_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute year-based publication trend."""
    year_counts = Counter()
    year_citations = defaultdict(list)

    for r in parsed_results:
        year = extract_year(r.get("text", ""), r.get("metadata", {}))
        if year:
            year_counts[year] += 1
            cit = extract_citations(r.get("metadata", {}))
            if cit is not None:
                year_citations[year].append(cit)

    years = sorted(year_counts.keys())
    counts = [year_counts[y] for y in years]
    avg_citations = [np.mean(year_citations[y]) if year_citations[y] else 0 for y in years]

    return {
        "years": years,
        "counts": counts,
        "avg_citations": avg_citations,
        "total_with_year": sum(counts),
        "total_without_year": len(parsed_results) - sum(counts)
    }


def compute_citation_stats(parsed_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute citation statistics."""
    citations = []
    for r in parsed_results:
        c = extract_citations(r.get("metadata", {}))
        if c is not None:
            citations.append(c)

    if not citations:
        return {"available": False, "count": 0}

    arr = np.array(citations)
    return {
        "available": True,
        "count": len(citations),
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "max": int(np.max(arr)),
        "min": int(np.min(arr)),
        "std": float(np.std(arr)),
        "values": citations,
        "distribution": dict(Counter(citations))
    }


def run_full_analysis(parsed_results: List[Dict[str, Any]], config: dict) -> Dict[str, Any]:
    """Run complete NLP analysis pipeline."""
    log_info(f"Starting full analysis on {len(parsed_results)} documents")
    top_k = config.get("tfidf_top_k", 20)

    texts = [r["text"] for r in parsed_results if r.get("text", "").strip()]
    if not texts:
        log_warn("No valid text found for analysis")
        return {"tfidf": {}, "cooccurrence": {}, "year_trend": {}, "citation_stats": {}}

    tfidf = compute_tfidf(texts, top_k=top_k)
    cooc = compute_cooccurrence(texts, top_k=top_k)
    trend = compute_year_trend(parsed_results)
    cit_stats = compute_citation_stats(parsed_results)

    # Extract all keywords from metadata
    all_meta_kws = []
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
        "valid_text_count": len(texts)
    }
