from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="InterviewSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("candidate_name", models.CharField(max_length=255)),
                ("resume_text", models.TextField()),
                (
                    "input_mode",
                    models.CharField(
                        choices=[("text", "Text"), ("voice", "Voice")],
                        default="text",
                        max_length=12,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("in_progress", "In progress"), ("completed", "Completed")],
                        default="in_progress",
                        max_length=20,
                    ),
                ),
                ("current_question_index", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="InterviewQuestion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order", models.PositiveIntegerField()),
                ("text", models.TextField()),
                ("source_keyword", models.CharField(blank=True, default="", max_length=100)),
                ("is_follow_up", models.BooleanField(default=False)),
                (
                    "session",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="interviews.interviewsession"),
                ),
            ],
            options={"ordering": ["order"], "unique_together": {("session", "order")}},
        ),
        migrations.CreateModel(
            name="InterviewFeedback",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("summary", models.TextField()),
                ("improvements", models.JSONField(blank=True, default=list)),
                ("total_score", models.FloatField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "session",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="feedback", to="interviews.interviewsession"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="InterviewAnswer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("answer_text", models.TextField()),
                ("score", models.FloatField(default=0)),
                ("mistakes", models.JSONField(blank=True, default=list)),
                ("keyword_hits", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "question",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="answer", to="interviews.interviewquestion"),
                ),
            ],
        ),
    ]
