from app.services.crm_context import build_dashboard, heuristic_answer
from app.services.cursor_analyst import answer_with_cursor

__all__ = ["build_dashboard", "heuristic_answer", "answer_with_cursor", "answer_analytics"]


def answer_analytics(db, message: str):
    return answer_with_cursor(db, message)
