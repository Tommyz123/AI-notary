"""Utility functions for simple vector-based lesson search.

This module implements a lightweight bag-of-words approach to
vectorise lesson content and compute cosine similarity.  It avoids
external dependencies by using Python's standard library only.
"""

import math
import re
from collections import Counter
from typing import Dict, List

Lesson = Dict[str, str]
Vector = Counter


def _tokenise(text: str) -> List[str]:
    """Split text into lowercase alphanumeric tokens."""
    return re.findall(r"\w+", text.lower())


def text_to_vector(text: str) -> Vector:
    """Convert a piece of text into a bag-of-words vector."""
    return Counter(_tokenise(text))


def cosine_similarity(v1: Vector, v2: Vector) -> float:
    """Compute cosine similarity between two bag-of-words vectors."""
    if not v1 or not v2:
        return 0.0
    intersection = set(v1) & set(v2)
    numerator = sum(v1[x] * v2[x] for x in intersection)
    sum1 = sum(v * v for v in v1.values())
    sum2 = sum(v * v for v in v2.values())
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    return numerator / denominator if denominator else 0.0


def build_lesson_vectors(lessons: List[Lesson]) -> Dict[str, Vector]:
    """Pre-compute vectors for each lesson's content."""
    return {lesson["No"]: text_to_vector(lesson["Content"]) for lesson in lessons}


def search_lessons(query: str, lessons: List[Lesson], vectors: Dict[str, Vector], top_k: int = 3) -> List[Lesson]:
    """Return the most similar lessons to a query."""
    query_vec = text_to_vector(query)
    scored = []
    for lesson in lessons:
        score = cosine_similarity(query_vec, vectors.get(lesson["No"], Counter()))
        if score > 0:
            scored.append((score, lesson))
    scored.sort(reverse=True, key=lambda x: x[0])
    return [lesson for _, lesson in scored[:top_k]]
