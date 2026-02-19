from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Iterable


DISALLOWED_CLAIM_PATTERNS = [
    r"fake experience",
    r"inflate years",
    r"claim certification",
    r"add .*certification.*(don't|do not) have",
    r"pretend",
    r"lie",
    r"fabricate",
]

ACTION_VERBS = [
    "Led",
    "Built",
    "Implemented",
    "Optimized",
    "Streamlined",
    "Automated",
    "Improved",
    "Coordinated",
    "Analyzed",
    "Delivered",
]


@dataclass
class ResumeScore:
    ats_compatibility: int
    role_relevance: int
    clarity_and_impact: int
    overall_score: int

    def as_json(self) -> str:
        return json.dumps(
            {
                "ats_compatibility": self.ats_compatibility,
                "role_relevance": self.role_relevance,
                "clarity_and_impact": self.clarity_and_impact,
                "overall_score": self.overall_score,
            },
            ensure_ascii=False,
        )


class ResumeIntelligenceEngine:
    """Ethical, ATS-conscious resume content helper."""

    def _is_unethical_request(self, text: str) -> bool:
        lowered = text.lower()
        return any(re.search(pattern, lowered) for pattern in DISALLOWED_CLAIM_PATTERNS)

    def safety_gate(self, request: str) -> str | None:
        if self._is_unethical_request(request):
            return (
                "Request cannot be fulfilled because it asks for inaccurate resume claims. "
                "Use verified experience and achievements, and rewrite wording for stronger impact instead."
            )
        return None

    def generate_summary(
        self,
        job_title: str,
        experience_level: str,
        skills: Iterable[str],
        value_focus: str,
    ) -> str:
        skills_text = ", ".join(skills)
        return (
            f"{experience_level} {job_title} with strengths in {skills_text}. "
            f"Delivers {value_focus} through structured execution, clear stakeholder communication, and measurable outcomes. "
            "Builds ATS-aligned, business-relevant solutions with concise and impact-focused documentation."
        )

    def generate_experience_bullets(self, tasks: Iterable[str]) -> list[str]:
        bullets: list[str] = []
        for idx, task in enumerate(tasks):
            verb = ACTION_VERBS[idx % len(ACTION_VERBS)]
            cleaned = task.strip().rstrip(".")
            bullets.append(f"{verb} {cleaned} to improve delivery quality and operational efficiency.")
        return bullets

    def rewrite_content(self, content: str) -> str:
        rewritten = re.sub(r"\b(I|me|my|we|our|us)\b", "", content, flags=re.IGNORECASE)
        rewritten = re.sub(r"\s+", " ", rewritten).strip()
        if rewritten and rewritten[-1] not in ".!?":
            rewritten += "."
        return rewritten

    def optimize_ats_keywords(self, content: str, keywords: Iterable[str]) -> str:
        optimized = content.strip()
        for kw in keywords:
            if kw.lower() not in optimized.lower():
                optimized += f" {kw}."
        return optimized

    def align_with_job_description(
        self,
        resume_text: str,
        job_description: str,
        existing_experience_bullets: Iterable[str],
    ) -> dict[str, list[str] | str]:
        jd_tokens = {t.lower() for t in re.findall(r"[A-Za-z][A-Za-z0-9+#.-]{2,}", job_description)}
        resume_tokens = {t.lower() for t in re.findall(r"[A-Za-z][A-Za-z0-9+#.-]{2,}", resume_text)}
        missing = sorted(t for t in jd_tokens - resume_tokens if t.isalpha())[:12]

        rewritten_bullets = []
        for bullet in existing_experience_bullets:
            line = self.rewrite_content(bullet)
            rewritten_bullets.append(line)

        return {
            "missing_keywords": missing,
            "alignment_suggestions": (
                "Prioritize missing keywords in summary, skills, and existing experience bullets without adding new claims."
            ),
            "rewritten_bullets": rewritten_bullets,
        }

    def score_resume(self, resume_text: str, target_role_keywords: Iterable[str]) -> str:
        text = resume_text.lower()
        keywords = [k.lower() for k in target_role_keywords]
        hits = sum(1 for k in keywords if k in text)
        keyword_ratio = int((hits / max(len(keywords), 1)) * 100)

        bullet_count = len(re.findall(r"(^|\n)[-•*]", resume_text))
        clarity = min(100, 40 + bullet_count * 5)

        ats = min(100, 50 + keyword_ratio // 2)
        relevance = min(100, 35 + keyword_ratio)
        overall = int((ats + relevance + clarity) / 3)

        return ResumeScore(ats, relevance, clarity, overall).as_json()

    def identify_skill_gaps(self, current_skills: Iterable[str], jd_skills: Iterable[str]) -> list[str]:
        current = {s.lower() for s in current_skills}
        return [skill for skill in jd_skills if skill.lower() not in current]

    def generate_cover_letter(
        self,
        role: str,
        company: str,
        strengths: Iterable[str],
        contribution_goal: str,
    ) -> str:
        strengths_text = ", ".join(strengths)
        return (
            f"Dear Hiring Team,\n\n"
            f"Application submitted for the {role} position at {company}. "
            f"Background includes {strengths_text}, with consistent focus on business outcomes and execution quality. "
            f"Primary goal is to {contribution_goal} while supporting cross-functional collaboration and reliable delivery.\n\n"
            "Thank you for your time and consideration."
        )

    def suggest_sections(self, experience_level: str) -> list[str]:
        base = ["Professional Summary", "Core Skills", "Professional Experience", "Education", "Projects"]
        if experience_level.lower() in {"senior", "lead", "leadership", "director"}:
            return ["Executive Profile", "Key Achievements", "Leadership Experience", "Core Skills", "Education"]
        if experience_level.lower() in {"fresher", "entry", "entry-level", "junior"}:
            return ["Profile", "Skills", "Internships / Projects", "Education", "Certifications"]
        return base
