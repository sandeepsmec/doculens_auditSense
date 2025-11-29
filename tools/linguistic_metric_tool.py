# tools/originality_check_tool.py
from crewai.tools import BaseTool
import re
import math
from typing import Dict


class LinguisticMetricTool(BaseTool):
    name: str = "Linguistic Metric Tool"
    description: str = (
        "Computes linguistic metrics — lexical diversity, repetition ratio, "
        "and normalized length score — without making interpretive judgments."
    )

    def _run(self, document_text: str, domain_keywords: str = "") -> Dict:
        try:
            text = (document_text or "").strip()
            if not text:
                return self._empty("No content to evaluate.", domain_keywords)

            diversity = self._calc_diversity(text)
            repetition = self._calc_repetition(text)
            length_score, word_count = self._calc_length_score(text)

            composite_score = round(
                0.4 * diversity + 0.3 * (1 - repetition) + 0.3 * length_score, 2
            )

            return {
                "composite_score": composite_score,
                "metrics": {
                    "lexical_diversity": round(diversity, 3),
                    "repetition_ratio": round(repetition, 3),
                    "length_score": round(length_score, 3),
                    "word_count": word_count,
                },
                "domain_keywords": domain_keywords,
                "reasoning": (
                    f"Diversity={diversity:.2f}, Repetition={repetition:.2f}, "
                    f"LengthScore={length_score:.2f}, Words={word_count}"
                ),
                "status": "ok",
            }

        except Exception as e:
            return self._empty(f"Error: {str(e)}", domain_keywords)

    def _calc_diversity(self, text: str) -> float:
        """Measures lexical diversity as unique_words / total_words."""
        words = re.findall(r"\b\w+\b", text.lower())
        total = len(words)
        return len(set(words)) / total if total else 0.0

    def _calc_repetition(self, text: str) -> float:
        """Estimates word repetition ratio (0 = diverse, 1 = repetitive)."""
        words = re.findall(r"\b\w+\b", text.lower())
        if not words:
            return 0.0
        freq = {w: words.count(w) for w in set(words)}
        avg_reps = sum(freq.values()) / len(freq)
        return min((avg_reps - 1) / 10, 1.0)

    def _calc_length_score(self, text: str):
        """Scores document length on a logarithmic scale."""
        words = re.findall(r"\b\w+\b", text)
        word_count = len(words)
        length_score = min(math.log10(word_count + 1) / 3, 1.0)
        return length_score, word_count

    def _empty(self, reason: str, domain_keywords: str) -> Dict:
        """Fallback structure when content is missing or errors occur."""
        return {
            "composite_score": 0.0,
            "metrics": {
                "lexical_diversity": 0.0,
                "repetition_ratio": 0.0,
                "length_score": 0.0,
                "word_count": 0,
            },
            "reasoning": reason,
            "domain_keywords": domain_keywords,
            "status": "fallback",
        }
