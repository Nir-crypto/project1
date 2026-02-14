from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('learning', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedbackQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField()),
                ('type', models.CharField(choices=[('RADIO', 'RADIO'), ('SCALE', 'SCALE')], max_length=10)),
                ('options', models.JSONField(default=list)),
            ],
        ),
        migrations.CreateModel(
            name='RecommendationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('courses_json', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('attempt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recommendation_logs', to='learning.assessmentattempt')),
            ],
        ),
        migrations.CreateModel(
            name='FeedbackResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('responses', models.JSONField(default=dict)),
                ('comment', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedback_responses', to='learning.course')),
                ('final_attempt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedback_responses', to='learning.finalassessmentattempt')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedback_responses', to='auth.user')),
            ],
        ),
    ]
