import re
from collections import Counter
from dataclasses import dataclass
from statistics import mean

from .models import InterviewAnswer, InterviewFeedback, InterviewQuestion, InterviewSession


@dataclass
class AnswerEvaluation:
    score: float
    mistakes: list[str]
    keyword_hits: list[str]


class DynamicInterviewEngine:
    """Adaptive interview engine that builds questions from resume + previous answers."""

    STOP_WORDS = {
        "the", "a", "an", "and", "or", "is", "are", "to", "in", "on", "for", "of", "with",
        "i", "my", "we", "our", "you", "your", "it", "this", "that", "as", "at", "be", "have",
        "has", "had", "from", "by", "was", "were", "will", "would", "can", "could", "should",
    }

    BASE_TEMPLATES = [
        "Can you explain your experience using {keyword} in a real project?",
        "What are the best practices you follow when working with {keyword}?",
        "Describe a challenge you faced with {keyword} and how you solved it.",
        "How do you measure success when delivering work related to {keyword}?",
        "If you had to mentor a junior on {keyword}, what would you teach first?",
    ]

    FOLLOW_UP_TEMPLATES = [
        "You mentioned {keyword}. Can you go deeper with a practical example?",
        "How would you optimize your approach for {keyword} at scale?",
        "What trade-offs should be considered when using {keyword}?",
    ]

    MIN_QUESTIONS = 25

    def extract_keywords(self, text: str, limit: int = 12) -> list[str]:
        words = re.findall(r"[a-zA-Z][a-zA-Z0-9#+.-]{1,}", text.lower())
        filtered = [w for w in words if w not in self.STOP_WORDS and len(w) > 2]
        if not filtered:
            return ["problem-solving", "communication", "teamwork"]
        counts = Counter(filtered)
        return [word for word, _ in counts.most_common(limit)]

    def build_initial_questions(self, session: InterviewSession) -> list[InterviewQuestion]:
        keywords = self.extract_keywords(session.resume_text)
        generated = []
        order = 1

        while len(generated) < self.MIN_QUESTIONS:
            for keyword in keywords:
                for template in self.BASE_TEMPLATES:
                    if len(generated) >= self.MIN_QUESTIONS:
                        break
                    generated.append(
                        InterviewQuestion(
                            session=session,
                            order=order,
                            text=template.format(keyword=keyword),
                            source_keyword=keyword,
                            is_follow_up=False,
                        )
                    )
                    order += 1
                if len(generated) >= self.MIN_QUESTIONS:
                    break

        InterviewQuestion.objects.bulk_create(generated)
        return list(session.questions.order_by("order"))

    def evaluate_answer(self, answer_text: str, expected_keyword: str) -> AnswerEvaluation:
        mistakes: list[str] = []
        keyword_hits = self.extract_keywords(answer_text, limit=5)
        length = len(answer_text.split())
        score = 10.0

        if length < 20:
            mistakes.append("Answer is too short; add context, action, and outcome.")
            score -= 2
        if expected_keyword.lower() not in answer_text.lower():
            mistakes.append(f"You did not clearly connect the answer to '{expected_keyword}'.")
            score -= 2
        if not re.search(r"\b(example|project|result|impact|metric)\b", answer_text.lower()):
            mistakes.append("Include at least one concrete example or measurable result.")
            score -= 2
        if re.search(r"\b(um|uh|like|you know)\b", answer_text.lower()):
            mistakes.append("Avoid filler words to improve clarity.")
            score -= 1

        return AnswerEvaluation(score=max(score, 1), mistakes=mistakes, keyword_hits=keyword_hits)

    def add_follow_up_question(self, session: InterviewSession, answer_text: str) -> InterviewQuestion | None:
        keywords = self.extract_keywords(answer_text, limit=1)
        if not keywords:
            return None

        keyword = keywords[0]
        template = self.FOLLOW_UP_TEMPLATES[(session.current_question_index + 1) % len(self.FOLLOW_UP_TEMPLATES)]
        next_order = session.questions.count() + 1

        return InterviewQuestion.objects.create(
            session=session,
            order=next_order,
            text=template.format(keyword=keyword),
            source_keyword=keyword,
            is_follow_up=True,
        )

    def submit_answer(
        self,
        session: InterviewSession,
        question: InterviewQuestion,
        answer_text: str,
    ) -> tuple[InterviewAnswer, InterviewQuestion | None]:
        evaluation = self.evaluate_answer(answer_text, question.source_keyword)

        answer = InterviewAnswer.objects.create(
            question=question,
            answer_text=answer_text,
            score=evaluation.score,
            mistakes=evaluation.mistakes,
            keyword_hits=evaluation.keyword_hits,
        )

        self.add_follow_up_question(session, answer_text)

        session.current_question_index += 1
        session.save(update_fields=["current_question_index", "updated_at"])

        next_question = session.questions.filter(order=session.current_question_index + 1).first()
        if next_question is None:
            session.status = InterviewSession.Status.COMPLETED
            session.save(update_fields=["status", "updated_at"])

        return answer, next_question

    def finalize_feedback(self, session: InterviewSession) -> InterviewFeedback:
        answers = InterviewAnswer.objects.filter(question__session=session)
        if not answers.exists():
            summary = "Interview not completed yet."
            improvements = ["Provide answers to generate actionable feedback."]
            score = 0
        else:
            score = round(mean(answer.score for answer in answers), 2)
            all_mistakes = [mistake for answer in answers for mistake in answer.mistakes]
            common = Counter(all_mistakes).most_common(5)
            improvements = [item[0] for item in common] or ["Keep giving structured, metric-backed answers."]
            summary = (
                f"You completed {answers.count()} questions with an average score of {score}/10. "
                "Focus on structure (Situation, Action, Result), clarity, and measurable impact."
            )

        feedback, _ = InterviewFeedback.objects.update_or_create(
            session=session,
            defaults={
                "summary": summary,
                "improvements": improvements,
                "total_score": score,
            },
        )
        return feedback
