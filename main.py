from council.orchestrator import CouncilOrchestrator
from utils.logger import setup_logger
from utils.validators import validate_query

logger = setup_logger(__name__)

def main():
    logger.info("Starting Uncertainty Agent Council")
    orchestrator = CouncilOrchestrator()
    
    print("Uncertainty Agent Council")
    print("=" * 50)
    
    while True:
        query = input("\nEnter your query (or 'quit' to exit): ")
        
        if query.lower() == 'quit':
            break
        
        if not validate_query(query):
            print("Invalid query. Please try again.")
            continue
        
        logger.info(f"Processing query: {query}")
        decision = orchestrator.process_query(query)
        
        print(f"\nConfidence Score: {decision.confidence_score:.2f}")
        if decision.warnings:
            print(f"Warnings: {', '.join(decision.warnings)}")
        print(f"\nResponse:\n{decision.final_response}")

if __name__ == "__main__":
    main()
