from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0002_quiz_is_active_quizattempt_time_taken_seconds_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='can_edit_profile',
            field=models.BooleanField(default=False),
        ),
    ]
