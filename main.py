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

    test_cases = [
        # ─── Basic literals ─────────────────────────────
        "a",            # Single character
        "abc",          # Concatenation: a → b → c

        # ─── Quantifiers ────────────────────────────────
        "a*",           # Zero or more 'a'
        "b+",           # One or more 'b'
        "c?",           # Zero or one 'c'
        "abc?",         # Optional 'c' at the end

        # ─── Alternation ────────────────────────────────
        "a|b",          
        "a|b|c",        # Multiple choices
        "a|b?",         # 'a' or optional 'b'
        "ab|cd",        
        "ab|cd|ef",     
        "[a-z]|c",      

        # ─── Grouping & nesting ─────────────────────────
        "(ab|cd)e",     # Group followed by 'e'
        "((a|b)c)+",    # Nested group repeated
        "(a+b)+",       
        "(a|b)*abb",    

        # ─── Character classes ──────────────────────────
        "[a-c][x-z]*",  
        "[a-zA-Z]+[0-9]?",
        "[a-zA-Z0-9]+",

        # ─── Mixed expressions ──────────────────────────
        "a(b|c)*d+",    
        "ab.c*d[a-c]",  
        "a?(a+b)*b",    

        # ─── Wildcards ──────────────────────────────────
        "a.",           # Any character after 'a'

        # ─── Complex / real-like patterns ───────────────
        "[a-zA-Z0-9]+2[a-zA-Z]+.[a-zA-Z]+",
        "(N|[oO]h?)?[a-z]*(g[.]?r[.]?e[.]?a[.]?t)[a-z]*",

        # ─── Case-insensitive style patterns ────────────
        "[Gg]et[Rr]ick[Rr]olled",
        "[Oo]sama+",
        "S[kK][iI][bB][iI][dD][iI]",

        # ─── Plain strings (no regex logic) ─────────────
        "ab",
        "TheBoysWishesUEidMubarak",
    ]

    for i, regex in enumerate(test_cases, start=1):
        output_name = f"outputs/testcase_{i}"
        print(f"\nProcessing regex: '{regex}' -> Output prefix: '{output_name}'")
        try:
            process_regex(regex, output_name)
        except ValueError as ve:
            print(f"Invalid regex '{regex}': {ve}")


# Run the extended test cases
if __name__ == "__main__":
    run_nfa_tests()
