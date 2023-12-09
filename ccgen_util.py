IN_TO_MM_RATIO = 2.54 * 10
PT_TO_MM_RATIO = 0.352

def in_to_mm(inches: float) -> float:
    return inches * IN_TO_MM_RATIO


def pt_to_mm(pt: float) -> float:
    return PT_TO_MM_RATIO * pt


def round_up(n: int, size: int):
    return ((((n) + (size) - 1)) & (~((size) - 1)))


if __name__ == "__main__":
    print("ccgen_util should not be run as main!")
    exit(1)