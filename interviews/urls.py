from django.urls import path

from . import views

urlpatterns = [
    path("start/", views.start_interview, name="interview-start"),
    path("answer/", views.submit_answer, name="interview-answer"),
    path("report/<int:session_id>/", views.interview_report, name="interview-report"),
]
