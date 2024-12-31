# Generated by Django 4.1.13 on 2024-12-28 13:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_remove_questionresponse_unique_question_response_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('video_id', models.CharField(max_length=20)),
                ('thumbnail_url', models.URLField()),
                ('duration', models.CharField(max_length=10)),
                ('channel_name', models.CharField(max_length=100)),
                ('order', models.PositiveIntegerField(default=0)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='courses.course')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]
