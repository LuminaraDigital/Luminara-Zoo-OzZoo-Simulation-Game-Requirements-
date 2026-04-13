"""Optional AI advisor: OpenAI or Gemini, strict limits, never auto-runs the simulation."""

from __future__ import annotations

import os
import time
from typing import TYPE_CHECKING, List, Literal, Tuple

if TYPE_CHECKING:
    from zoo.zoo import Zoo


def _limits() -> Tuple[int, int, int]:
    """(max calls per in-game day, min seconds between calls, max output tokens)."""
    return (
        max(1, int(os.getenv("AI_MAX_CALLS_PER_SIM_DAY", "3"))),
        max(0, int(os.getenv("AI_MIN_SECONDS_BETWEEN_CALLS", "60"))),
        max(100, min(2000, int(os.getenv("AI_MAX_OUTPUT_TOKENS", "400")))),
    )


class AIUsageSession:
    """Rate-limit state; reset per in-game day boundary."""

    def __init__(self) -> None:
        self.__sim_day_marker: int = -1
        self.__calls_this_day = 0
        self.__last_mono: float = 0.0

    def sync_day(self, sim_day: int) -> None:
        if sim_day != self.__sim_day_marker:
            self.__sim_day_marker = sim_day
            self.__calls_this_day = 0

    def can_request(self, sim_day: int) -> Tuple[bool, str]:
        self.sync_day(sim_day)
        max_c, min_gap, _ = _limits()
        if self.__calls_this_day >= max_c:
            return False, (
                f"AI advisor daily limit reached ({max_c} uses per in-game day). "
                "Advance to a new day — the simulation never requires AI."
            )
        if self.__last_mono > 0.0 and min_gap > 0:
            elapsed = time.monotonic() - self.__last_mono
            if elapsed < min_gap:
                wait = int(min_gap - elapsed) + 1
                return False, f"AI cooldown: wait ~{wait}s before another advisor request."
        return True, ""

    def record_request(self) -> None:
        self.__calls_this_day += 1
        self.__last_mono = time.monotonic()

    def usage_this_day(self) -> int:
        return self.__calls_this_day


_SESSION = AIUsageSession()


def session_usage_this_day(zoo: Zoo) -> Tuple[int, int]:
    """Return (used_this_sim_day, limit_per_sim_day)."""
    _SESSION.sync_day(zoo.current_day)
    max_c, _, _ = _limits()
    return _SESSION.usage_this_day(), max_c


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass


def build_zoo_context(zoo: Zoo) -> str:
    """Short context string for the model (no secrets)."""
    st = zoo.get_zoo_status()
    animals = st.get("animals", [])[:12]
    lines = [
        f"Park: {st.get('park_name', 'Luminara Zoo')}",
        f"Day {st.get('day')}, funds ${st.get('funds_aud', 0):.0f}, "
        f"reputation {st.get('reputation', 0)}%, "
        f"population {st.get('population')}/{st.get('capacity')}.",
    ]
    for a in animals:
        lines.append(
            f"- {a.get('name')} ({a.get('taxon')}): H{a.get('health')} "
            f"hunger {a.get('hunger')} clean {a.get('cleanliness')} mood {a.get('happiness')}"
        )
    return "\n".join(lines)


def ask_advisor(
    *,
    provider: Literal["openai", "gemini"],
    user_question: str,
    zoo: Zoo,
) -> Tuple[bool, str]:
    """Returns (ok, message). Only call after explicit player confirmation in the UI."""
    _load_dotenv()
    ok, err = _SESSION.can_request(zoo.current_day)
    if not ok:
        return False, err

    _, _, max_tokens = _limits()
    system = (
        "You are a concise advisor for the Luminara Zoo Python simulation (Australian wildlife, "
        "budget, feeding, habitats). Reply in under 180 words. No API keys or real credentials. "
        "If asked to play the game, say the player must use the CLI menus — you only give tips."
    )
    context = build_zoo_context(zoo)
    prompt = f"Context:\n{context}\n\nManager question:\n{user_question.strip()}"

    try:
        if provider == "openai":
            text = _call_openai(system, prompt, max_tokens)
        else:
            text = _call_gemini(system, prompt, max_tokens)
    except Exception as exc:  # pragma: no cover - network/SDK
        return False, f"AI request failed ({provider}): {exc}"

    _SESSION.record_request()
    return True, text.strip()


def _call_openai(system: str, user: str, max_tokens: int) -> str:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set in the environment or .env file.")

    from openai import OpenAI

    client = OpenAI(api_key=key)
    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=max_tokens,
        temperature=0.6,
    )
    choice = resp.choices[0].message.content
    if not choice:
        return "(Empty response.)"
    return choice


def _call_gemini(system: str, user: str, max_tokens: int) -> str:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not set in the environment or .env file.")

    import google.generativeai as genai

    genai.configure(api_key=key)
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    model = genai.GenerativeModel(model_name)
    full = f"{system}\n\n{user}"
    gen_cfg = {"max_output_tokens": max_tokens, "temperature": 0.6}
    resp = model.generate_content(full, generation_config=gen_cfg)
    text = getattr(resp, "text", None) or ""
    if not text and getattr(resp, "candidates", None):
        parts: List[str] = []
        for c in resp.candidates:
            if c.content and c.content.parts:
                for p in c.content.parts:
                    if hasattr(p, "text") and p.text:
                        parts.append(p.text)
        text = "\n".join(parts)
    return text or "(Empty response.)"


def advisor_status_line(zoo: Zoo) -> str:
    """One-line hint for menus (no network)."""
    used, max_c = session_usage_this_day(zoo)
    _, min_gap, max_tok = _limits()
    return (
        f"AI advisor (optional): {used}/{max_c} uses this in-game day; "
        f"cooldown {min_gap}s; max ~{max_tok} tokens — simulation never requires AI."
    )
