# vireon_mensa_solver.py
#
# VIREON Mensa Solver (Fractal Edition, v3 – Hard Mode, faithful)
#
# This inverts the rules in vireon_mensa_engine.py:
# given (test_id, question_idx) it returns the unique correct answer.
#
# Domains and return formats:
#   Q  1–15 : int                          (missing number)
#   Q 16–25 : "TRUE" or "FALSE"           (string)
#   Q 26–35 : "(A, B)"                    (ordered arrow pair, string)
#   Q 36–45 : "A".."Z"                    (mapped letter)
#   Q 46–55 : int                          (samples per team)
#   Q 56–70 : "▲○(0°)"-style string       (Raven figure)
#   Q 71–80 : int                          (decimal value N)
#   Q 81–90 : (int, int)                  (counts of shape A, shape B in Fig. 5)
#   Q 91–100: int                          (self-ref count, exactly as in engine)

from vireon_mensa_engine import NUM_TESTS, QUESTIONS_PER_TEST


# ---------- Helpers shared across domains ----------

def _ensure_valid_indices(test_id: int, question_idx: int):
    if not (1 <= test_id <= NUM_TESTS):
        raise ValueError(f"test_id must be in 1..{NUM_TESTS}")
    if not (1 <= question_idx <= QUESTIONS_PER_TEST):
        raise ValueError(f"question_idx must be in 1..{QUESTIONS_PER_TEST}")


def _is_prime_like(n: int) -> bool:
    """
    'prime-like' as defined in the engine:
    n has no divisors in {2, 3, 5, 7}.
    (I.e. n is coprime to 2·3·5·7 = 210.)
    """
    for d in (2, 3, 5, 7):
        if n % d == 0:
            return False
    return True


def _is_prime(n: int) -> bool:
    """Basic primality check for self-referential questions."""
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    f = 3
    r = int(n ** 0.5)
    while f <= r:
        if n % f == 0:
            return False
        f += 2
    return True


# ---------- Domain 1: Numeric sequences (Q 1–15) ----------

def _solve_numeric(test_id: int, question_idx: int):
    """
    Recover the hidden term in the numeric sequence (hard mode).
    Mirrors generate_numeric_question().
    """
    local = question_idx  # 1..15
    length = 7

    base = (3 * test_id + 5 * local) % 97 + 10
    alpha = (2 * test_id + local) % 11 + 1   # linear
    beta = (test_id + 3 * local) % 7 + 1     # quadratic
    even_offset = (test_id * local) % 9
    odd_offset = (test_id + local) % 9

    seq = []
    for n in range(length):
        k = n + 1
        val = base + alpha * k + beta * (k * k)
        if k % 2 == 0:
            val += even_offset
        else:
            val += odd_offset
        seq.append(val)

    missing_pos = 2 + (local % 3)  # 2..4 (0-based)
    return seq[missing_pos]


# ---------- Domain 2: Logic propositions (Q 16–25) ----------

def _solve_logic(test_id: int, question_idx: int):
    """
    Evaluate the nested propositional statement.
    Returns "TRUE" or "FALSE" (string).
    """
    local = question_idx - 15  # 1..10
    pattern_type = (test_id + local) % 4

    p = (test_id % 2 == 0)
    q = (local % 3 == 0)
    r = _is_prime_like(test_id + local)

    if pattern_type == 0:
        # (p AND q) OR (NOT r)
        val = (p and q) or (not r)
    elif pattern_type == 1:
        # IF (p AND r) THEN (q XOR r)
        val = (not (p and r)) or (q ^ r)
    elif pattern_type == 2:
        # (p XOR q) AND (q OR r)
        val = (p ^ q) and (q or r)
    else:
        # IF (p OR q) THEN (NOT p AND r)
        val = (not (p or q)) or ((not p) and r)

    return "TRUE" if val else "FALSE"


# ---------- Domain 3: Dual arrow cycles (Q 26–35) ----------

def _solve_arrows(test_id: int, question_idx: int):
    """
    Compute the ordered pair (A, B) from the dual arrow cycles.
    Returns a string "(A, B)".
    """
    local = question_idx - 25  # 1..10
    primary = ["↑", "→", "↓", "←"]
    secondary = ["↖", "↗", "↘", "↙"]

    N1 = 7 * test_id + 11 * local
    N2 = 5 * test_id - 3 * local

    A = primary[(N1 - 1) % 4]
    B = secondary[(N2 - 1) % 4]

    return f"({A}, {B})"


# ---------- Domain 4: Letter analogies (Q 36–45) ----------

def _solve_letter(test_id: int, question_idx: int):
    """
    Recover the mapped letter for the query input.
    Mirrors generate_letter_question().
    """
    local = question_idx - 35  # 1..10

    a = (2 * test_id + 1) % 26
    if a % 2 == 0:
        a = (a + 1) % 26
    b = (3 * local + test_id) % 26

    x1 = (5 * test_id + local) % 26
    x2 = (x1 + 13) % 26

    def enc(i: int) -> str:
        return chr(ord('A') + (i % 26))

    answer_index = (a * x2 + b) % 26
    return enc(answer_index)


# ---------- Domain 5: Word-style arithmetic stories (Q 46–55) ----------

def _solve_word(test_id: int, question_idx: int):
    """
    Solve the layered word problem.
    Returns the integer number of samples per team.
    """
    local = question_idx - 45  # 1..10

    base_items = 4 + (test_id % 9)
    daily_gain = 1 + (local % 5)
    days = 3 + ((test_id + local) % 4)
    group = 2 + (test_id % 4)

    bonus_factor = 1 + ((test_id * local) % 3)
    loss = (base_items + daily_gain) % (group + 1)

    total = base_items + daily_gain * days
    total *= bonus_factor
    total -= loss

    return total // group


# ---------- Domain 6: Raven-style 3×3 matrices (Q 56–70) ----------

def _solve_raven(test_id: int, question_idx: int):
    """
    Return the figure that should replace '?' in the Raven-style matrix.
    Mirrors the engine's cell_symbol() + missing cell logic.
    """
    local = question_idx - 55  # 1..15
    shapes = ["▲", "■", "●", "★"]
    orientations = ["0°", "90°", "180°", "270°"]
    fills = ["○", "◐", "●"]  # empty, half, full

    base_idx = (test_id + local) % len(shapes)
    base_orient = (2 * test_id + local) % 4
    base_fill = (3 * test_id + 2 * local) % 3

    missing_mode = (test_id + local) % 3   # 0: bottom-right, 1: center, 2: top-right

    def cell_symbol(r: int, c: int) -> str:
        s_idx = (base_idx + r + 2 * c) % len(shapes)
        o_idx = (base_orient + 2 * r + c) % 4
        f_idx = (base_fill + r + c) % 3
        return f"{shapes[s_idx]}{fills[f_idx]}({orientations[o_idx]})"

    if missing_mode == 0:
        mr, mc = 2, 2  # bottom-right
    elif missing_mode == 1:
        mr, mc = 1, 1  # center
    else:
        mr, mc = 0, 2  # top-right

    return cell_symbol(mr, mc)


# ---------- Domain 7: Base conversion puzzles (Q 71–80) ----------

def _solve_base(test_id: int, question_idx: int):
    """
    Base conversion puzzles all encode a single hidden integer N.
    The answer is simply that N in base 10.
    """
    local = question_idx - 70  # 1..10
    N = 200 + 17 * test_id + 11 * local
    return N


# ---------- Domain 8: Shape sequences (Q 81–90) ----------

def _solve_shape_sequence(test_id: int, question_idx: int):
    """
    Compute the counts of shape A and shape B in Figure 5.
    Returns a tuple (count_A_5, count_B_5).
    """
    local = question_idx - 80  # 1..10

    modulus_A = 5 + ((test_id + local) % 5)        # 5..9
    modulus_B = 6 + ((2 * test_id + local) % 5)    # 6..10

    base_A = 1 + ((test_id + 2 * local) % modulus_A)
    base_B = 1 + ((2 * test_id + 3 * local) % modulus_B)

    step_A = 1 + ((3 * test_id + local) % modulus_A)
    step_B = 1 + ((4 * test_id + 2 * local) % modulus_B)

    k = 5
    a5 = (base_A + (k - 1) * step_A) % modulus_A
    b5 = (base_B + (k - 1) * step_B) % modulus_B
    if a5 == 0:
        a5 = modulus_A
    if b5 == 0:
        b5 = modulus_B

    return (a5, b5)


# ---------- Domain 9: Self-referential (Q 91–100) ----------

def _basic_self_ref_digit_mode(test_id: int, question_idx: int):
    """
    EXACTLY the same mapping as the engine:
      local = question_idx - 90 (1..10)
      digit = (test_id + local) % 10
      mode  = (test_id + 2*local) % 4
    """
    local = question_idx - 90  # 1..10
    digit = (test_id + local) % 10
    mode = (test_id + 2 * local) % 4
    return digit, mode


def _self_ref_count_for_digit_mode(digit: int, mode: int):
    """
    Given digit d and mode ∈ {0,1,2,3}, count n in [1..QUESTIONS_PER_TEST]
    satisfying the specified condition.
    Modes:
      0: contain digit d
      1: contain digit d AND even
      2: contain digit d AND prime
      3: contain digit d OR divisible by 9
    """
    def has_digit(n: int, d: int) -> bool:
        return str(d) in str(n)

    count = 0
    for n in range(1, QUESTIONS_PER_TEST + 1):
        has_d = has_digit(n, digit)
        if mode == 0:
            cond = has_d
        elif mode == 1:
            cond = has_d and (n % 2 == 0)
        elif mode == 2:
            cond = has_d and _is_prime(n)
        else:
            cond = has_d or (n % 9 == 0)

        if cond:
            count += 1
    return count


def _solve_self_referential(test_id: int, question_idx: int):
    """
    Self-referential questions: faithful inversion of the engine.
    No parity twist, no dependence on answers to other questions.
    """
    digit, mode = _basic_self_ref_digit_mode(test_id, question_idx)
    return _self_ref_count_for_digit_mode(digit, mode)


# ---------- Public API ----------

def solve_question(test_id: int, question_idx: int):
    """
    Main entrypoint: given (test_id, question_idx), return the canonical answer.
    """
    _ensure_valid_indices(test_id, question_idx)

    if 1 <= question_idx <= 15:
        return _solve_numeric(test_id, question_idx)
    elif 16 <= question_idx <= 25:
        return _solve_logic(test_id, question_idx)
    elif 26 <= question_idx <= 35:
        return _solve_arrows(test_id, question_idx)
    elif 36 <= question_idx <= 45:
        return _solve_letter(test_id, question_idx)
    elif 46 <= question_idx <= 55:
        return _solve_word(test_id, question_idx)
    elif 56 <= question_idx <= 70:
        return _solve_raven(test_id, question_idx)
    elif 71 <= question_idx <= 80:
        return _solve_base(test_id, question_idx)
    elif 81 <= question_idx <= 90:
        return _solve_shape_sequence(test_id, question_idx)
    else:  # 91..100
        return _solve_self_referential(test_id, question_idx)


# ---------- Minimal demo (optional) ----------

if __name__ == "__main__":
    t = 1
    for q in range(1, 21):
        print(f"Test {t}, Q{q} →", solve_question(t, q))
