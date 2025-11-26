# vireon_mensa_engine.py
#
# VIREON Mensa Engine (Fractal Edition, v3 – Hard Mode)
# 1000 tests × 100 questions, deterministic from (test_id, question_idx)
# No answers are computed or stored here – question generation only.
#
# Domains per test (by question index):
#  1–15   : numeric sequences (mixed linear / quadratic / parity rules)
# 16–25   : logic propositions with nested conditionals
# 26–35   : symbolic arrow cycles with multi-step indexing
# 36–45   : letter / alphabet analogies with coupled shifts
# 46–55   : word-style arithmetic stories with layered operations
# 56–70   : Raven-style 3×3 matrices (rotation / reflection / xor mixtures)
# 71–80   : number base conversion puzzles (cross-base, cross-digit tricks)
# 81–90   : “next figure” modulo-based shape-count sequences with drift
# 91–100  : self-referential questions over the whole test index set

NUM_TESTS = 1000
QUESTIONS_PER_TEST = 100


# ---------- Domain 1: Numeric sequences (Q 1–15) ----------

def generate_numeric_question(test_id: int, question_idx: int) -> dict:
    """
    Numeric sequence with one missing term.
    Underlying rule mixes:
      - a linear component,
      - a quadratic component in n,
      - and parity-dependent offsets.

    We only show the terms, not the rule.
    """
    local = question_idx  # 1..15
    length = 7

    # Seed parameters from test_id and question_idx
    base = (3 * test_id + 5 * local) % 97 + 10
    alpha = (2 * test_id + local) % 11 + 1   # linear
    beta = (test_id + 3 * local) % 7 + 1     # quadratic
    even_offset = (test_id * local) % 9
    odd_offset = (test_id + local) % 9

    # Generate sequence a_n = base + alpha*n + beta*n^2 + parity_offset
    seq = []
    for n in range(length):
        k = n + 1
        val = base + alpha * k + beta * (k * k)
        if k % 2 == 0:
            val += even_offset
        else:
            val += odd_offset
        seq.append(val)

    # Hide a middle term
    missing_pos = 2 + (local % 3)  # 2..4
    shown = []
    for i, x in enumerate(seq):
        if i == missing_pos:
            shown.append("?")
        else:
            shown.append(str(x))

    prompt = (
        f"Test {test_id}, Q{question_idx} (Numeric sequence – hard):\n"
        f"Fill in the missing number. The rule may depend on position,\n"
        f"parity, and more than one type of growth.\n\n"
        f"Sequence: " + ", ".join(shown)
    )
    return {
        "test_id": test_id,
        "question_idx": question_idx,
        "domain": "numeric_sequence_hard",
        "prompt": prompt,
        "meta": {
            "local_index": local,
            "length": length,
            "pattern_hint": "mix of linear, quadratic, and parity-based offsets",
        }
    }


# ---------- Domain 2: Logic propositions (Q 16–25) ----------

def generate_logic_question(test_id: int, question_idx: int) -> dict:
    """
    Nested propositional logic with three atomic propositions p, q, r.

    p: test_id is even
    q: local index in this block is a multiple of 3
    r: test_id + local index is prime-like (pseudo condition)

    We do NOT compute truth here.
    """
    local = question_idx - 15  # 1..10
    # Choose a pattern among several nested forms
    pattern_type = (test_id + local) % 4

    if pattern_type == 0:
        stmt = "(p AND q) OR (NOT r)"
    elif pattern_type == 1:
        stmt = "IF (p AND r) THEN (q XOR r)"
    elif pattern_type == 2:
        stmt = "(p XOR q) AND (q OR r)"
    else:
        stmt = "IF (p OR q) THEN (NOT p AND r)"

    pseudo_prime_def = (
        "Call an integer 'prime-like' here if it has no divisors in "
        "the set {2, 3, 5, 7} other than 1."
    )

    prompt = (
        f"Test {test_id}, Q{question_idx} (Nested logic – hard):\n"
        f"Let p be: 'test id {test_id} is even'.\n"
        f"Let q be: 'local index {local} (1–10 in this block) is a multiple of 3'.\n"
        f"Let r be: 'test_id + local_index is prime-like'.\n\n"
        f"{pseudo_prime_def}\n\n"
        f"Consider the compound statement:\n"
        f"    {stmt}\n\n"
        f"Is this statement TRUE or FALSE?"
    )
    return {
        "test_id": test_id,
        "question_idx": question_idx,
        "domain": "nested_logic_hard",
        "prompt": prompt,
        "meta": {
            "local_index": local,
            "statement_form": stmt,
            "prime_like_rule": "no divisors in {2,3,5,7} besides 1",
        }
    }


# ---------- Domain 3: Symbolic arrow cycles (Q 26–35) ----------

def generate_spatial_like_question(test_id: int, question_idx: int) -> dict:
    """
    Symbolic 'spatial' pattern using two coupled arrow cycles at different speeds.

    Primary cycle: ↑, →, ↓, ←
    Secondary cycle: ↖, ↗, ↘, ↙

    Effective position uses a nontrivial index mapping from (test_id, local).
    """
    local = question_idx - 25  # 1..10
    primary = ["↑", "→", "↓", "←"]
    secondary = ["↖", "↗", "↘", "↙"]

    # Two-layer index:
    # N1 for primary, N2 for secondary
    N1 = 7 * test_id + 11 * local
    N2 = 5 * test_id - 3 * local

    prompt = (
        f"Test {test_id}, Q{question_idx} (Dual-arrow cycle – hard):\n"
        f"Consider two infinite repeating sequences:\n"
        f"  Primary:   {', '.join(primary)} (then repeats)\n"
        f"  Secondary: {', '.join(secondary)} (then repeats)\n\n"
        f"At position N₁ = 7·{test_id} + 11·{local} in the Primary sequence,\n"
        f"and position N₂ = 5·{test_id} − 3·{local} in the Secondary sequence,\n"
        f"a pair of arrows (A, B) is observed.\n\n"
        f"What is the ordered pair (A, B)?"
    )
    return {
        "test_id": test_id,
        "question_idx": question_idx,
        "domain": "dual_arrow_cycle_hard",
        "prompt": prompt,
        "meta": {
            "local_index": local,
            "primary_cycle": primary,
            "secondary_cycle": secondary,
            "N1_expression": f"7*{test_id} + 11*{local}",
            "N2_expression": f"5*{test_id} - 3*{local}",
        }
    }


# ---------- Domain 4: Letter / alphabet analogies (Q 36–45) ----------

def generate_letter_question(test_id: int, question_idx: int) -> dict:
    """
    Alphabet analogy with coupled affine maps on positions.

    Map f(k) = a*k + b (mod 26), with parameters derived from (test_id, local).
    We show one example pair and one query pair.
    """
    local = question_idx - 35  # 1..10

    # Coefficients a, b in Z_26, with a odd to be invertible.
    a = (2 * test_id + 1) % 26
    if a % 2 == 0:
        a = (a + 1) % 26
    b = (3 * local + test_id) % 26

    # Example input letter index and query input index
    x1 = (5 * test_id + local) % 26
    x2 = (x1 + 13) % 26

    def enc(pos: int) -> str:
        return chr(ord('A') + (pos % 26))

    A1 = enc(x1)
    B1 = enc((a * x1 + b) % 26)
    A2 = enc(x2)

    prompt = (
        f"Test {test_id}, Q{question_idx} (Letter analogy – hard):\n"
        f"A secret code maps each letter to another letter according to\n"
        f"a fixed rule on its position in the alphabet.\n\n"
        f"Example:\n"
        f"    {A1} → {B1}\n\n"
        f"Using the same hidden rule, what letter does {A2} map to?\n"
        f"(All letters are in A–Z, positions taken modulo 26.)"
    )

    return {
        "test_id": test_id,
        "question_idx": question_idx,
        "domain": "letter_analogy_hard",
        "prompt": prompt,
        "meta": {
            "local_index": local,
            "a_mod_26": a,
            "b_mod_26": b,
            "example_input_index": x1,
            "query_input_index": x2,
        }
    }


# ---------- Domain 5: Word-style arithmetic stories (Q 46–55) ----------

def generate_word_question(test_id: int, question_idx: int) -> dict:
    """
    Multi-step arithmetic story: additions, multiplications, and a final ratio.

    We don't simplify in the prompt; solver must carefully track operations.
    """
    local = question_idx - 45  # 1..10

    # Parameters derived from test and local indices
    base_items = 4 + (test_id % 9)
    daily_gain = 1 + (local % 5)
    days = 3 + ((test_id + local) % 4)
    group = 2 + (test_id % 4)

    bonus_factor = 1 + ((test_id * local) % 3)
    loss = (base_items + daily_gain) % (group + 1)

    prompt = (
        f"Test {test_id}, Q{question_idx} (Layered word problem – hard):\n"
        f"A researcher starts with {base_items} experimental samples.\n"
        f"Each day, they create {daily_gain} new samples, and this continues "
        f"for {days} days. After that, they multiply the total number of "
        f"samples they have by a 'bonus factor' of {bonus_factor}.\n"
        f"Finally, they must discard exactly {loss} samples due to defects, "
        f"and then divide the remaining samples equally among {group} teams.\n\n"
        f"How many samples does each team receive?"
    )

    return {
        "test_id": test_id,
        "question_idx": question_idx,
        "domain": "word_arithmetic_hard",
        "prompt": prompt,
        "meta": {
            "local_index": local,
            "base_items": base_items,
            "daily_gain": daily_gain,
            "days": days,
            "bonus_factor": bonus_factor,
            "loss": loss,
            "groups": group,
        }
    }


# ---------- Domain 6: Raven-style 3×3 matrices (Q 56–70) ----------

def generate_raven_matrix_question(test_id: int, question_idx: int) -> dict:
    """
    Raven-style 3×3 matrix with multiple latent features:

      - shape ∈ {▲, ■, ●, ★}
      - orientation ∈ {0°, 90°, 180°, 270°}
      - fill ∈ {empty, half, full}

    Rules combine row-wise and column-wise operations (rotation increments,
    orientation xor, etc.). We do not show the explicit rule.
    """
    local = question_idx - 55  # 1..15
    shapes = ["▲", "■", "●", "★"]
    orientations = ["0°", "90°", "180°", "270°"]
    fills = ["○", "◐", "●"]  # empty, half, full

    base_idx = (test_id + local) % len(shapes)
    base_orient = (2 * test_id + local) % 4
    base_fill = (3 * test_id + 2 * local) % 3

    rule_type = (test_id + 2 * local) % 4  # 0..3
    missing_mode = (test_id + local) % 3   # 0: bottom-right, 1: center, 2: top-right

    def cell_symbol(r: int, c: int) -> str:
        # multi-feature drift by row, col
        s_idx = (base_idx + r + 2 * c) % len(shapes)
        o_idx = (base_orient + 2 * r + c) % 4
        f_idx = (base_fill + r + c) % 3
        return f"{shapes[s_idx]}{fills[f_idx]}({orientations[o_idx]})"

    grid = []
    for r in range(3):
        row = []
        for c in range(3):
            row.append(cell_symbol(r, c))
        grid.append(row)

    if missing_mode == 0:
        missing_rc = (2, 2)  # bottom-right
    elif missing_mode == 1:
        missing_rc = (1, 1)  # center
    else:
        missing_rc = (0, 2)  # top-right

    mr, mc = missing_rc
    grid[mr][mc] = " ? "

    grid_lines = []
    for r in range(3):
        grid_lines.append(" | ".join(grid[r]))
    grid_text = "\n".join(grid_lines)

    hints = [
        "Row-wise, orientation changes in fixed increments.",
        "Column-wise, fill levels behave like addition modulo 3.",
        "Shapes drift systematically across rows and columns.",
        "Some rows can be interpreted as an 'xor' of feature patterns."
    ]
    hint = hints[rule_type]

    prompt = (
        f"Test {test_id}, Q{question_idx} (Raven-style matrix – hard):\n"
        f"Below is a 3×3 grid of abstract figures; one cell is replaced by '?'.\n\n"
        f"{grid_text}\n\n"
        f"The grid obeys a consistent rule combining row and column changes\n"
        f"in shape, orientation, and fill.\n"
        f"Which figure should replace '?'?\n\n"
        f"Hint: {hint}"
    )

    return {
        "test_id": test_id,
        "question_idx": question_idx,
        "domain": "raven_matrix_hard",
        "prompt": prompt,
        "meta": {
            "local_index": local,
            "rule_type": rule_type,
            "missing_cell": {"row": mr, "col": mc},
        }
    }


# ---------- Helper: integer → base representation ----------

def _to_base(n: int, base: int) -> str:
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if n == 0:
        return "0"
    out = ""
    x = n
    while x > 0:
        out = digits[x % base] + out
        x //= base
    return out


# ---------- Domain 7: Base conversion puzzles (Q 71–80) ----------

def generate_base_conversion_question(test_id: int, question_idx: int) -> dict:
    """
    Hard base conversion: same integer represented in base_x and base_y,
    plus an intermediate base_z in the text.

    We still only ask for the decimal value.
    """
    local = question_idx - 70  # 1..10

    base_x = 5 + ((test_id + local) % 12)       # 5..16
    base_y = 5 + ((2 * test_id + local) % 12)   # 5..16
    if base_y == base_x:
        base_y = 5 + ((3 * test_id + local) % 12)
        if base_y == base_x:
            base_y = 16

    # Hidden integer
    N = 200 + 17 * test_id + 11 * local

    repr_x = _to_base(N, base_x)
    repr_y = _to_base(N, base_y)

    base_z = 5 + ((test_id + 2 * local) % 12)   # extra base mentioned
    repr_z = _to_base(N, base_z)

    prompt = (
        f"Test {test_id}, Q{question_idx} (Base conversion – hard):\n"
        f"A certain integer N is written as {repr_x} in base {base_x} and as "
        f"{repr_y} in base {base_y}. When expressed in base {base_z}, it "
        f"would be written as {repr_z}.\n\n"
        f"All three representations refer to the same integer N.\n"
        f"What is the value of N when written in base 10 (ordinary decimal)?"
    )

    return {
        "test_id": test_id,
        "question_idx": question_idx,
        "domain": "base_conversion_hard",
        "prompt": prompt,
        "meta": {
            "local_index": local,
            "base_x": base_x,
            "base_y": base_y,
            "base_z": base_z,
            "repr_x": repr_x,
            "repr_y": repr_y,
            "repr_z": repr_z,
        }
    }


# ---------- Domain 8: Next figure (modulo-based shape counts) (Q 81–90) ----------

def generate_shape_sequence_question(test_id: int, question_idx: int) -> dict:
    """
    Sequence of figures described by counts of two shapes (A, B),
    both following coupled modular recurrences.

    Solver must track both sequences and extrapolate to Figure 5.
    """
    local = question_idx - 80  # 1..10

    modulus_A = 5 + ((test_id + local) % 5)       # 5..9
    modulus_B = 6 + ((2 * test_id + local) % 5)   # 6..10

    base_A = 1 + ((test_id + 2 * local) % modulus_A)
    base_B = 1 + ((2 * test_id + 3 * local) % modulus_B)

    step_A = 1 + ((3 * test_id + local) % modulus_A)
    step_B = 1 + ((4 * test_id + 2 * local) % modulus_B)

    shapeA = ["●", "■", "▲"][(test_id + local) % 3]
    shapeB = ["◆", "✚", "✕"][(2 * test_id + local) % 3]

    counts_A = []
    counts_B = []
    for k in range(1, 5):
        a = (base_A + (k - 1) * step_A) % modulus_A
        b = (base_B + (k - 1) * step_B) % modulus_B
        if a == 0:
            a = modulus_A
        if b == 0:
            b = modulus_B
        counts_A.append(a)
        counts_B.append(b)

    lines = []
    for i in range(4):
        lines.append(
            f"Figure {i+1}: {counts_A[i]} {shapeA} symbols and "
            f"{counts_B[i]} {shapeB} symbols."
        )

    sequence_text = "\n".join(lines)

    prompt = (
        f"Test {test_id}, Q{question_idx} (Next figure – coupled modulo):\n"
        f"Consider the sequence of abstract figures:\n\n"
        f"{sequence_text}\n\n"
        f"The counts of {shapeA} and {shapeB} symbols each follow a modular\n"
        f"arithmetic rule (but possibly with different moduli and steps).\n\n"
        f"In Figure 5, how many {shapeA} symbols and how many {shapeB} symbols "
        f"should appear?"
    )

    return {
        "test_id": test_id,
        "question_idx": question_idx,
        "domain": "shape_sequence_coupled_modulo_hard",
        "prompt": prompt,
        "meta": {
            "local_index": local,
            "modulus_A": modulus_A,
            "modulus_B": modulus_B,
            "shapeA": shapeA,
            "shapeB": shapeB,
            "first_four_A": counts_A,
            "first_four_B": counts_B,
            "rule_hint": "two coupled linear progressions modulo different bases",
        }
    }


# ---------- Domain 9: Self-referential questions (Q 91–100) ----------

def generate_self_referential_question(test_id: int, question_idx: int) -> dict:
    """
    Self-referential puzzle over the set {1..QUESTIONS_PER_TEST}.

    We vary what property is counted:
      - presence of a digit d,
      - parity of the index,
      - primality of the index,
      - divisibility conditions, etc.

    Still well-defined; no paradoxes, no meta-parity, no dependence on answers.
    """
    local = question_idx - 90  # 1..10
    digit = (test_id + local) % 10  # 0..9
    mode = (test_id + 2 * local) % 4

    if mode == 0:
        condition_text = (
            f"contain the digit {digit} at least once (in decimal notation)"
        )
    elif mode == 1:
        condition_text = (
            f"contain the digit {digit} at least once AND are even numbers"
        )
    elif mode == 2:
        condition_text = (
            f"contain the digit {digit} at least once AND are prime numbers"
        )
    else:
        condition_text = (
            f"contain the digit {digit} at least once OR are divisible by 9"
        )

    prompt = (
        f"Test {test_id}, Q{question_idx} (Self-referential – hard):\n"
        f"In this test, questions are numbered from 1 to {QUESTIONS_PER_TEST}.\n"
        f"Consider those question numbers that {condition_text}.\n\n"
        f"How many such question numbers are there?"
    )

    return {
        "test_id": test_id,
        "question_idx": question_idx,
        "domain": "self_referential_hard",
        "prompt": prompt,
        "meta": {
            "local_index": local,
            "digit": digit,
            "mode": mode,
            "range": (1, QUESTIONS_PER_TEST),
        }
    }


# ---------- Dispatcher & top-level iterators ----------

def generate_question(test_id: int, question_idx: int) -> dict:
    """
    Master dispatcher: given (test_id, question_idx), returns a question dict.
    test_id in 1..NUM_TESTS
    question_idx in 1..QUESTIONS_PER_TEST
    """
    if not (1 <= test_id <= NUM_TESTS):
        raise ValueError(f"test_id must be in 1..{NUM_TESTS}")
    if not (1 <= question_idx <= QUESTIONS_PER_TEST):
        raise ValueError(f"question_idx must be in 1..{QUESTIONS_PER_TEST}")

    if 1 <= question_idx <= 15:
        return generate_numeric_question(test_id, question_idx)
    elif 16 <= question_idx <= 25:
        return generate_logic_question(test_id, question_idx)
    elif 26 <= question_idx <= 35:
        return generate_spatial_like_question(test_id, question_idx)
    elif 36 <= question_idx <= 45:
        return generate_letter_question(test_id, question_idx)
    elif 46 <= question_idx <= 55:
        return generate_word_question(test_id, question_idx)
    elif 56 <= question_idx <= 70:
        return generate_raven_matrix_question(test_id, question_idx)
    elif 71 <= question_idx <= 80:
        return generate_base_conversion_question(test_id, question_idx)
    elif 81 <= question_idx <= 90:
        return generate_shape_sequence_question(test_id, question_idx)
    else:  # 91..100
        return generate_self_referential_question(test_id, question_idx)


def generate_test(test_id: int) -> list:
    """
    Generate all 100 questions for a given test_id.
    """
    return [generate_question(test_id, q) for q in range(1, QUESTIONS_PER_TEST + 1)]


def iter_all_tests():
    """
    Generator over all tests (1..NUM_TESTS), each as a list of question dicts.
    """
    for t in range(1, NUM_TESTS + 1):
        yield t, generate_test(t)


# ---------- Minimal demo (optional) ----------

if __name__ == "__main__":
    # Print a small sample to sanity-check structure
    sample_test_id = 1
    questions = generate_test(sample_test_id)
    for q in questions[:15]:
        print("=" * 60)
        print(q["prompt"])
