import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

def compose_email_html(ranked_models, ranking_reason):
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .model-card {{ border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; border-left: 5px solid #007bff; }}
            .model-title {{ font-size: 1.2em; font-weight: bold; color: #007bff; }}
            .label {{ font-weight: bold; color: #555; }}
            .ranking-section {{ background: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <h1>Biweekly AI Model Digest</h1>
        <div class="ranking-section">
            <h3>Priority Ranking & Insight</h3>
            <p>{ranking_reason.replace('\\n', '<br>')}</p>
        </div>
    """
    
    for m in ranked_models:
        summary = m.get('summary', {})
        html += f"""
        <div class="model-card">
            <div class="model-title"><a href="https://huggingface.co/{m['id']}">{m['id']}</a></div>
            <p><span class="label">License:</span> {m.get('license', 'Unknown')}</p>
            <p><span class="label">Hardware Verdict:</span> {m.get('hardware_verdict')}</p>
            <p><span class="label">Summary:</span> {summary.get('one_line_summary')}</p>
            <p><span class="label">Use Case:</span> {summary.get('use_case')}</p>
            <p><span class="label">Key Innovation:</span> {summary.get('key_innovation')}</p>
            <p><span class="label">Benchmark Note:</span> {summary.get('benchmark_note', 'N/A')}</p>
        </div>
        """
    
    html += "</body></html>"
    return html

def send_email(html_content):
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", 587))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    to_email = os.getenv("DIGEST_TO_EMAIL")

    if not all([host, user, password, to_email]):
        logger.error("Missing email configuration. Cannot send digest.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Biweekly AI Model Watcher Digest"
    msg["From"] = user
    msg["To"] = to_email

    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(user, to_email, msg.as_string())
        logger.info("Digest email sent successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False
