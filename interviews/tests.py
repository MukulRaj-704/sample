from django.test import TestCase

from .models import InterviewSession
from .services import DynamicInterviewEngine


class DynamicInterviewEngineTests(TestCase):
    def setUp(self):
        self.engine = DynamicInterviewEngine()

    def test_build_initial_questions_creates_at_least_25(self):
        session = InterviewSession.objects.create(
            candidate_name="Asha",
            resume_text="Python Django REST APIs PostgreSQL Docker leadership communication",
        )

        questions = self.engine.build_initial_questions(session)

        self.assertGreaterEqual(len(questions), 25)
        self.assertEqual(questions[0].order, 1)

    def test_submit_answer_creates_follow_up_and_next_question(self):
        session = InterviewSession.objects.create(
            candidate_name="Asha",
            resume_text="Python Django REST APIs PostgreSQL Docker",
        )
        questions = self.engine.build_initial_questions(session)

        answer, next_question = self.engine.submit_answer(
            session,
            questions[0],
            "I used Django in a project where I improved API latency by 40 percent with caching.",
        )

        self.assertIsNotNone(answer.id)
        self.assertIsNotNone(next_question)
        self.assertGreaterEqual(session.questions.count(), 26)

    def test_finalize_feedback_returns_improvements(self):
        session = InterviewSession.objects.create(
            candidate_name="Asha",
            resume_text="Python Django REST APIs PostgreSQL Docker",
        )
        questions = self.engine.build_initial_questions(session)
        self.engine.submit_answer(session, questions[0], "Short answer")

        feedback = self.engine.finalize_feedback(session)

        self.assertTrue(feedback.summary)
        self.assertTrue(isinstance(feedback.improvements, list))
