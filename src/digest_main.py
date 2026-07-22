import logging
from .state import load_pending_digest, clear_pending_digest
from .ai_client import AIClient
from .digest import compose_email_html, send_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    pending = load_pending_digest()
    if not pending:
        logger.info("No pending models for digest. Skipping.")
        return

    ai = AIClient()
    logger.info(f"Generating digest for {len(pending)} models.")
    
    try:
        # Rank models
        ranking_reason = ai.rank_models(pending)
        
        # We assume the AI returns a ranked list or insight. 
        # For simplicity in this version, we use the original list but show the AI's insight.
        # A more complex version would parse the AI's list to reorder.
        
        html = compose_email_html(pending, ranking_reason)
        
        if send_email(html):
            clear_pending_digest()
            logger.info("Digest sent and queue cleared.")
        else:
            logger.error("Failed to send digest email.")
            
    except Exception as e:
        logger.error(f"Error generating digest: {e}")

if __name__ == "__main__":
    main()
