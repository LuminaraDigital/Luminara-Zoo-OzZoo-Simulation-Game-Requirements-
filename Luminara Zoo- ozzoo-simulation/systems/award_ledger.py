"""In-game awards (additive only; core simulation does not depend on this)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Set, Tuple

if TYPE_CHECKING:
    from zoo.zoo import Zoo

# (id, display title, description for trophy case)
_AWARD_DEFS: Tuple[Tuple[str, str, str], ...] = (
    ("dawn_patrol", "Dawn Patrol", "Completed your first end-of-day simulation tick."),
    ("steady_provider", "Steady Provider", "Fed animals 5 times (any feeding path)."),
    ("conservation_voice", "Conservation Voice", "Adopted 3 animals into Luminara."),
    ("new_generation", "New Generation", "Welcomed offspring through the breeding program."),
    ("vet_champion", "Vet Champion", "Applied medicine 5 times."),
    ("pantry_builder", "Pantry Builder", "Purchased food from the market 10 times."),
    ("groundskeeper_star", "Groundskeeper Star", "Cleaned habitats 5 times."),
    ("deep_reserve", "Deep Reserve", "Treasury reached $100,000."),
    ("full_house", "Full House", "Every adoption slot is occupied."),
    ("luminara_legend", "Luminara Legend", "Held elite reputation for 30 consecutive days."),
    ("heat_steady", "Heat Steady", "Survived a heatwave day with no deaths."),
    ("ten_clear_skies", "Ten Clear Skies", "Ran 10 day ticks with no animal deaths."),
)


class AwardLedger:
    """Tracks cumulative player actions and unlocks cosmetic awards."""

    def __init__(self) -> None:
        self.__unlocked: Set[str] = set()
        self.__feed_count = 0
        self.__adopt_count = 0
        self.__breed_count = 0
        self.__medicine_count = 0
        self.__food_purchases = 0
        self.__clean_count = 0
        self.__day_ticks = 0
        self.__days_without_death_streak = 0

    def snapshot(self) -> Dict[str, Any]:
        """Serialise for ``get_zoo_status``."""
        return {
            "unlocked_ids": sorted(self.__unlocked),
            "trophies": [self._describe(i) for i in sorted(self.__unlocked)],
        }

    def _describe(self, aid: str) -> Dict[str, str]:
        for i, title, desc in _AWARD_DEFS:
            if i == aid:
                return {"id": i, "title": title, "description": desc}
        return {"id": aid, "title": aid, "description": ""}

    def _unlock(self, aid: str) -> str | None:
        if aid in self.__unlocked:
            return None
        self.__unlocked.add(aid)
        for i, title, _ in _AWARD_DEFS:
            if i == aid:
                return title
        return aid

    def _try_unlocks(self, zoo: Zoo) -> List[str]:
        """Evaluate threshold awards; return newly unlocked display titles."""
        new_titles: List[str] = []
        checks: List[Tuple[str, bool]] = [
            ("dawn_patrol", self.__day_ticks >= 1),
            ("steady_provider", self.__feed_count >= 5),
            ("conservation_voice", self.__adopt_count >= 3),
            ("new_generation", self.__breed_count >= 1),
            ("vet_champion", self.__medicine_count >= 5),
            ("pantry_builder", self.__food_purchases >= 10),
            ("groundskeeper_star", self.__clean_count >= 5),
            ("deep_reserve", zoo.treasury.balance >= 100_000),
            ("full_house", zoo.population >= zoo.capacity and zoo.capacity > 0),
            ("luminara_legend", zoo.has_won_campaign),
            ("ten_clear_skies", self.__days_without_death_streak >= 10),
        ]
        for aid, cond in checks:
            if cond:
                t = self._unlock(aid)
                if t:
                    new_titles.append(t)
        return new_titles

    def on_feed_success(self, zoo: Zoo) -> List[str]:
        self.__feed_count += 1
        return self._try_unlocks(zoo)

    def on_adopt_success(self, zoo: Zoo) -> List[str]:
        self.__adopt_count += 1
        return self._try_unlocks(zoo)

    def on_breed_success(self, zoo: Zoo) -> List[str]:
        self.__breed_count += 1
        return self._try_unlocks(zoo)

    def on_medicine_success(self, zoo: Zoo) -> List[str]:
        self.__medicine_count += 1
        return self._try_unlocks(zoo)

    def on_food_purchase(self, zoo: Zoo) -> List[str]:
        self.__food_purchases += 1
        return self._try_unlocks(zoo)

    def on_medicine_restock(self, zoo: Zoo) -> List[str]:
        return self._try_unlocks(zoo)

    def on_clean_success(self, zoo: Zoo) -> List[str]:
        self.__clean_count += 1
        return self._try_unlocks(zoo)

    def on_day_end(
        self,
        zoo: Zoo,
        *,
        had_death_today: bool,
        heatwave: bool,
    ) -> List[str]:
        self.__day_ticks += 1
        if had_death_today:
            self.__days_without_death_streak = 0
        else:
            self.__days_without_death_streak += 1
        new_titles = self._try_unlocks(zoo)
        if heatwave and not had_death_today:
            t = self._unlock("heat_steady")
            if t:
                new_titles.append(t)
        return new_titles
