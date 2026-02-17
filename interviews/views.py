import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import InterviewQuestion, InterviewSession
from .services import DynamicInterviewEngine


engine = DynamicInterviewEngine()


def _json_request(request):
    try:
        return json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        return {}


@csrf_exempt
def start_interview(request):
    if request.method != "POST":
        return JsonResponse({"error": "Use POST"}, status=405)

    payload = _json_request(request)
    candidate_name = payload.get("candidate_name", "Candidate")
    resume_text = payload.get("resume_text", "")
    input_mode = payload.get("input_mode", InterviewSession.InputMode.TEXT)

    if input_mode not in [InterviewSession.InputMode.TEXT, InterviewSession.InputMode.VOICE]:
        return JsonResponse({"error": "input_mode must be text or voice"}, status=400)

    session = InterviewSession.objects.create(
        candidate_name=candidate_name,
        resume_text=resume_text,
        input_mode=input_mode,
    )

    questions = engine.build_initial_questions(session)
    first_question = questions[0] if questions else None

    return JsonResponse(
        {
            "session_id": session.id,
            "input_mode": session.input_mode,
            "question": {
                "id": first_question.id,
                "order": first_question.order,
                "text": first_question.text,
            } if first_question else None,
            "total_questions": len(questions),
        }
    )


@csrf_exempt
def submit_answer(request):
    if request.method != "POST":
        return JsonResponse({"error": "Use POST"}, status=405)

    payload = _json_request(request)
    session_id = payload.get("session_id")
    question_id = payload.get("question_id")
    answer_text = payload.get("answer_text", "")

    if not session_id or not question_id:
        return JsonResponse({"error": "session_id and question_id are required"}, status=400)

    try:
        session = InterviewSession.objects.get(pk=session_id)
        question = InterviewQuestion.objects.get(pk=question_id, session=session)
    except (InterviewSession.DoesNotExist, InterviewQuestion.DoesNotExist):
        return JsonResponse({"error": "Session/question not found"}, status=404)

    if session.input_mode == InterviewSession.InputMode.VOICE and not answer_text:
        return JsonResponse(
            {"error": "For voice interviews, send transcribed text in answer_text."},
            status=400,
        )

    answer, next_question = engine.submit_answer(session, question, answer_text)

    response = {
        "answer_id": answer.id,
        "score": answer.score,
        "mistakes": answer.mistakes,
        "next_question": None,
        "completed": next_question is None,
    }

    if next_question:
        response["next_question"] = {
            "id": next_question.id,
            "order": next_question.order,
            "text": next_question.text,
            "is_follow_up": next_question.is_follow_up,
        }

    return JsonResponse(response)


@csrf_exempt
def interview_report(request, session_id: int):
    if request.method != "GET":
        return JsonResponse({"error": "Use GET"}, status=405)

    try:
        session = InterviewSession.objects.get(pk=session_id)
    except InterviewSession.DoesNotExist:
        return JsonResponse({"error": "Session not found"}, status=404)

    feedback = engine.finalize_feedback(session)
    return JsonResponse(
        {
            "session_id": session.id,
            "status": session.status,
            "summary": feedback.summary,
            "total_score": feedback.total_score,
            "improvements": feedback.improvements,
        }
    )
