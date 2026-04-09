from micc.cli import MiccCore
import sys

def verify_paper_examples():
    core = MiccCore()
    
    print("--- Verifying Hempel Example (Expected Distance: 4) ---")
    # Hempel example from tests
    top = [21,7,8,9,10,11,22,23,24,0,1,2,3,4,5,6,12,13,14,15,16,17,18,19,20]
    bot = [9,10,11,12,13,14,15,1,2,3,4,5,16,17,18,19,20,21,22,23,24,0,6,7,8]
    
    # We need to set recursive=True for exact distance 4
    from micc.curves import CurvePair
    core.curve = CurvePair(top, bot, recursive=True)
    
    dist = core.get_distance()
    print(f"Hempel Distance: {dist}")
    
    assert dist == 4, f"Expected 4, got {dist}"
    
    print("\n--- Verifying Birman Example (Expected Distance: 3) ---")
    top_b = [4,3,3,1,0,0]
    bot_b = [5,5,4,2,2,1]
    core.curve = CurvePair(top_b, bot_b)
    dist_b = core.get_distance()
    print(f"Birman Distance: {dist_b}")
    
    assert dist_b == 3, f"Expected 3, got {dist_b}"
    
    print("\nVerification Successful!")

if __name__ == "__main__":
    verify_paper_examples()
