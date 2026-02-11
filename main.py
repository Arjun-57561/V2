#!/usr/bin/env python3
"""
Main entry point for Uncertainty-First Agent Council
"""
import sys
import json
from pathlib import Path
from typing import Optional

from council.orchestrator import UncertaintyFirstCouncil
from utils.logger import get_logger

logger = get_logger(__name__)

def main():
    """Main CLI interface"""
    
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║              UNCERTAINTY-FIRST AGENT COUNCIL                                  ║
║              An Agentic AI System that Explicitly Models Unknowns             ║
║                                                                               ║
║              Team: Amitkumar Racha, Bontha Mallikarjun Reddy, Neil Cardoz   ║
║              Symbiosis Institute of Technology, Pune                          ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Initialize council
        print("🚀 Initializing council...\n")
        council = UncertaintyFirstCouncil()
        
        # Interactive mode
        if len(sys.argv) == 1:
            interactive_mode(council)
        # Single query mode
        elif len(sys.argv) >= 2:
            query = " ".join(sys.argv[1:])
            process_single_query(council, query)
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        sys.exit(1)

def interactive_mode(council: UncertaintyFirstCouncil):
    """Interactive query mode"""
    
    print("💬 Interactive Mode")
    print("   Type your query and press Enter.")
    print("   Type 'quit' or 'exit' to quit.")
    print("   Type 'save' to save the last result to JSON.")
    print("   Type 'examples' to see sample queries.\n")
    
    last_output = None
    
    while True:
        try:
            query = input("❓ Your query: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if query.lower() == 'examples':
                show_examples()
                continue
            
            if query.lower() == 'save' and last_output:
                save_output(last_output)
                continue
            
            # Process query
            output = council.process_query(query, verbose=True)
            
            # Display user-friendly response
            user_response = council.get_user_friendly_response(output)
            print(user_response)
            
            last_output = output
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            print(f"\n❌ Error: {e}\n")

def process_single_query(council: UncertaintyFirstCouncil, query: str):
    """Process a single query and exit"""
    
    output = council.process_query(query, verbose=True)
    user_response = council.get_user_friendly_response(output)
    print(user_response)
    
    # Optionally save to file
    save_output(output, auto=True)

def show_examples():
    """Show example queries"""
    
    print("\n" + "="*80)
    print("EXAMPLE QUERIES".center(80))
    print("="*80)
    
    examples = [
        "I am 23 years old, earning 2.5 LPA, from Telangana, OBC category. Am I eligible for PM Kisan scheme?",
        "I am a 45-year-old farmer from Maharashtra with 3 acres of land. What government schemes can I apply for?",
        "I am 19, student, from Delhi, want to know about education loan schemes",
        "My annual income is 8 lakhs, I'm from Karnataka, General category, age 30. Which housing schemes am I eligible for?",
        "I don't have income certificate but earn around 3 LPA, from Bihar, SC category, age 25"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example}")
    
    print("\n" + "="*80 + "\n")

def save_output(output, auto: bool = False):
    """Save output to JSON file"""
    
    timestamp = output.query_processor.cleaned_query[:30].replace(" ", "_").replace("/", "_")
    filename = f"output_{timestamp}_{output.processing_time_seconds}s.json"
    
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    filepath = output_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output.to_dict(), f, indent=2, ensure_ascii=False)
    
    if not auto:
        print(f"\n💾 Output saved to: {filepath}\n")
    else:
        logger.info(f"Output saved to: {filepath}")

if __name__ == "__main__":
    main()
