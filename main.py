from __future__ import annotations
from dfa.DFA import DFA
from regex.RegexValidator import RegexValidator
from nfa.NFAVisualizer import NFAVisualizer
from nfa.NFABuilder import NFABuilder


def process_regex(regex: str, output_name: str):
    """Generates NFA JSON and image for given regex."""
    RegexValidator.validate(regex)
    nfa_builder = NFABuilder()
    nfa = nfa_builder.from_regex(regex)

    # Save JSON
    nfa_json_path = f"{output_name}_nfa.json"
    with open(nfa_json_path, "w") as f:
        f.write(nfa.to_json())

    # Save Image
    nfa_img_path = f"{output_name}_nfa.png"
    NFAVisualizer.save_image(nfa, nfa_img_path)
    print(f"NFA JSON saved: {nfa_json_path}")
    print(f"NFA image saved: {nfa_img_path}")

    dfa = DFA.build_minimized_dfa(nfa)
    # Save JSON
    dfa_json_path = f"{output_name}_dfa.json"
    with open(dfa_json_path, "w") as f:
        f.write(dfa.to_json())

    # Save Image
    dfa_img_path = f"{output_name}_dfa.png"
    NFAVisualizer.save_image(dfa, dfa_img_path)
    print(f"DFA JSON saved: {dfa_json_path}")
    print(f"DFA image saved: {dfa_img_path}")


def run_nfa_tests():
    testcases = [
        # Single literal
        "a",  # Single character
        # Concatenation
        "abc",  # a followed by b followed by c
        # Optional
        "abc?",  # c is optional
        # Alternation with optional
        "a|b?",  # a or optional b
        # Character class + wildcard + concatenation
        "a[1-9A-Z]x.z",  # a followed by range [1-9A-Z], then x, then any char, then z
        # Kleene star
        "a*",  # zero or more 'a's
        # One or more
        "b+",  # one or more 'b's
        # Zero or one
        "c?",  # zero or one 'c'
        # Alternation
        "a|b|c",  # matches a or b or c
        # Grouping
        "(ab|cd)e",  # group ab or cd, then e
        # Nested groups
        "((a|b)c)+",  # group (a or b)c repeated one or more times
        # Multiple character classes
        "[a-c][x-z]*",  # char a-c followed by zero or more chars x-z
        # Mix of all operators
        "a(b|c)*d+",  # a followed by zero or more (b|c), then one or more d
    ]

    for i, regex in enumerate(testcases, start=1):
        output_name = f"outputs/testcase_{i}"
        print(f"\nProcessing regex: '{regex}' -> Output prefix: '{output_name}'")
        try:
            process_regex(regex, output_name)
        except ValueError as ve:
            print(f"Invalid regex '{regex}': {ve}")


# Run the extended test cases
if __name__ == "__main__":
    run_nfa_tests()
