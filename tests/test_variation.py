"""variation 엔진 테스트."""
import pytest

from app.services.variation import pick_variant, make_seed, _stable_hash


def test_pick_variant_deterministic():
    v = ["a", "b", "c"]
    seed = ("user-1", "daily", "2026-10-18")
    r1 = pick_variant(v, seed_parts=seed)
    r2 = pick_variant(v, seed_parts=seed)
    assert r1 == r2


def test_pick_variant_across_processes():
    """_stable_hash는 sha256 기반 → 프로세스 재시작에도 동일."""
    v = ["x", "y", "z"]
    seed = ("u", "daily", "2026-10-18")
    # 여러 번 호출해도 같은 값
    results = {pick_variant(v, seed_parts=seed) for _ in range(10)}
    assert len(results) == 1


def test_pick_variant_different_seeds_may_differ():
    """다른 시드는 반드시 달라야 하는 건 아니지만, 통계적으로 분포한다."""
    v = ["a", "b", "c", "d", "e"]
    picks = {
        pick_variant(v, seed_parts=("user", "daily", f"2026-01-{i:02d}"))
        for i in range(1, 32)
    }
    assert len(picks) >= 3  # 5 variants 중 최소 3개는 등장해야 함


def test_pick_variant_single_element():
    assert pick_variant(["only"], seed_parts=("x",)) == "only"


def test_pick_variant_empty_raises():
    with pytest.raises(ValueError, match="must not be empty"):
        pick_variant([], seed_parts=("x",))


def test_stable_hash_deterministic():
    h1 = _stable_hash("user", "daily", "2026-10-18")
    h2 = _stable_hash("user", "daily", "2026-10-18")
    assert h1 == h2
    assert isinstance(h1, int)
    assert h1 > 0


def test_make_seed_priority():
    # user_id 우선
    s1 = make_seed(user_id="U", birth_date="B", scope="daily", discriminator="D")
    assert s1[0] == "U"

    # birth_date fallback
    s2 = make_seed(user_id=None, birth_date="B", scope="daily", discriminator="D")
    assert s2[0] == "B"

    # anonymous fallback
    s3 = make_seed(user_id=None, birth_date=None, scope="daily", discriminator="D")
    assert s3[0] == "anonymous"


def test_make_seed_shape():
    s = make_seed(user_id="U", birth_date=None, scope="daily", discriminator="2026-10-18")
    assert len(s) == 3
    assert s[1] == "daily"
    assert s[2] == "2026-10-18"
