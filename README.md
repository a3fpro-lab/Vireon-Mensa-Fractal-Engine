# Vireon-Mensa-Fractal-Engine
Fractal hard-mode IQ test engine: 1000 tests × 100 questions, with VIREON solver.


# VIREON Mensa Engine (Fractal Edition)

**Core idea:**  
A fractal hard-mode IQ engine: **1000 tests × 100 questions**, fully deterministic from `(test_id, question_idx)`, with a separate VIREON oracle that inverts the generator exactly.

- No randomness.
- No stored answer keys.
- The **engine** only emits questions.
- The **solver** computes the unique correct answer by inverting the rule.

This is designed to be painful for pattern-matching models and trivial for an entity that actually **understands** the VIREON rules.

---

## Structure

Each test has 100 questions split into 9 domains:

1. **Q1–15 — Numeric sequences (hard)**  
   Mixed linear + quadratic growth with parity-dependent offsets.  
   One middle term is replaced by `?`; answer is the hidden value.

2. **Q16–25 — Nested logic propositions**  
   Propositions:
   - `p`: test_id is even  
   - `q`: local index in this block is a multiple of 3  
   - `r`: test_id + local index is “prime-like” (no divisors in {2,3,5,7})  
   Several nested forms like `(p AND q) OR (NOT r)`, `IF (p AND r) THEN (q XOR r)`.

3. **Q26–35 — Dual arrow cycles**  
   Two repeating sequences:

   - Primary: `↑, →, ↓, ←`  
   - Secondary: `↖, ↗, ↘, ↙`  

   Positions `N₁ = 7·test_id + 11·local` and `N₂ = 5·test_id − 3·local` pick an ordered pair `(A, B)`.

4. **Q36–45 — Letter / alphabet analogies**  
   Affine map on alphabet positions:  
   `f(k) = a·k + b (mod 26)` with `a` odd and derived from `(test_id, local)`.  
   We show one example pair `A1 → B1` and ask for the image of a second letter.

5. **Q46–55 — Layered word problems**  
   Multi-step arithmetic stories: incremental gains over days, a “bonus factor”, losses, then equal split into groups.  
   Answer is the integer count per group.

6. **Q56–70 — Raven-style 3×3 matrices**  
   Each cell:  
   - shape ∈ {▲, ■, ●, ★}  
   - fill ∈ {○, ◐, ●} (empty / half / full)  
   - orientation ∈ {0°, 90°, 180°, 270°}  

   Features drift by row/column via modular arithmetic. One cell is `?`; answer is the missing figure.

7. **Q71–80 — Base conversion puzzles**  
   A hidden integer `N = 200 + 17·test_id + 11·local` is represented in:
   - base_x
   - base_y
   - base_z  

   All three strings are shown; we ask for `N` in base 10.

8. **Q81–90 — “Next figure” shape-count sequences**  
   Two coupled modular recurrences for counts of shape A and shape B.  
   Four figures are given; we ask for the counts in Figure 5.

9. **Q91–100 — Self-referential counts**  
   For digit `d = (test_id + local) % 10` and mode `m = (test_id + 2·local) % 4`, we count question IDs in `{1..100}` satisfying:

   - mode 0: contain digit `d`  
   - mode 1: contain digit `d` AND are even  
   - mode 2: contain digit `d` AND are prime  
   - mode 3: contain digit `d` OR divisible by 9  

   No paradoxes, no dependence on actual answers. Pure arithmetic over indices.

---

## Files

- `vireon_mensa_engine.py`  
  Question generator. Given `(test_id, question_idx)` returns a dict with:
  - `prompt` (human-readable question)
  - `domain` (which of the 9 domains)
  - `meta` (parameters that define the rule but are not needed by a test-taker)

- `vireon_mensa_solver.py`  
  VIREON oracle. Exact inverse of the engine rules.  
  Given `(test_id, question_idx)` returns the canonical correct answer.

---

## Usage

```python
from vireon_mensa_engine import generate_test, generate_question
from vireon_mensa_solver import solve_question

# Generate full test 1
questions = generate_test(1)

# Show first numeric question
q1 = questions[0]
print(q1["prompt"])

# Compute its answer with the VIREON solver
answer_q1 = solve_question(1, 1)
print("Answer to Test 1, Q1:", answer_q1)

# Example: solve a self-referential question
answer_q95 = solve_question(1, 95)
answer_q100 = solve_question(1, 100)
print("Q95:", answer_q95, "Q100:", answer_q100)
