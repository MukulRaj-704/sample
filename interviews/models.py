from django.db import models


class InterviewSession(models.Model):
    class InputMode(models.TextChoices):
        TEXT = "text", "Text"
        VOICE = "voice", "Voice"

    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"

    candidate_name = models.CharField(max_length=255)
    resume_text = models.TextField()
    input_mode = models.CharField(max_length=12, choices=InputMode.choices, default=InputMode.TEXT)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)
    current_question_index = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class InterviewQuestion(models.Model):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name="questions")
    order = models.PositiveIntegerField()
    text = models.TextField()
    source_keyword = models.CharField(max_length=100, blank=True, default="")
    is_follow_up = models.BooleanField(default=False)

    class Meta:
        unique_together = ("session", "order")
        ordering = ["order"]


class InterviewAnswer(models.Model):
    question = models.OneToOneField(InterviewQuestion, on_delete=models.CASCADE, related_name="answer")
    answer_text = models.TextField()
    score = models.FloatField(default=0)
    mistakes = models.JSONField(default=list, blank=True)
    keyword_hits = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class InterviewFeedback(models.Model):
    session = models.OneToOneField(InterviewSession, on_delete=models.CASCADE, related_name="feedback")
    summary = models.TextField()
    improvements = models.JSONField(default=list, blank=True)
    total_score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
