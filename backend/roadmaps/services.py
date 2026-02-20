from learning.models import AssessmentAttempt, Course
from .models import AIRoadmap, AIRoadmapStep
from .local_ai_generator import generate_local_ai_roadmap


def roadmap_payload(roadmap):
    return {
        'id': roadmap.id,
        'course_id': roadmap.course_id,
        'current_level': roadmap.current_level,
        'overall_points': roadmap.overall_points,
        'generated_by': roadmap.generated_by,
        'version': roadmap.version,
        'created_at': roadmap.created_at.isoformat() if roadmap.created_at else None,
        'steps': [
            {
                'step_no': step.step_no,
                'title': step.title,
                'description': step.description,
                'est_time_hours': step.est_time_hours,
                'outcome': step.outcome,
                'resource_title': step.resource_title,
                'resource_url': step.resource_url,
            }
            for step in roadmap.steps.all().order_by('step_no')
        ],
    }


def get_or_generate_roadmap(user, course, current_level, overall_points, interests_list):
    generated = generate_local_ai_roadmap(user, course, current_level, overall_points, interests_list)
    signature = generated['prompt_signature']

    cached = (
        AIRoadmap.objects.filter(user=user, course=course, prompt_signature=signature)
        .prefetch_related('steps')
        .order_by('-created_at')
        .first()
    )
    if cached:
        return roadmap_payload(cached)

    roadmap = AIRoadmap.objects.create(
        user=user,
        course=course,
        current_level=current_level,
        overall_points=overall_points,
        interests_snapshot=generated['interests_snapshot'],
        prompt_signature=signature,
        generated_by='LocalAI',
        version='v1',
    )

    AIRoadmapStep.objects.bulk_create(
        [
            AIRoadmapStep(
                roadmap=roadmap,
                step_no=step['step_no'],
                title=step['title'],
                description=step['description'],
                est_time_hours=step['est_time_hours'],
                outcome=step['outcome'],
                resource_title=step['resource_title'],
                resource_url=step['resource_url'],
            )
            for step in generated['steps']
        ]
    )

    roadmap = AIRoadmap.objects.prefetch_related('steps').get(id=roadmap.id)
    return roadmap_payload(roadmap)


def get_latest_or_generate_for_course(user, course_id):
    course = Course.objects.get(id=course_id)
    latest = (
        AIRoadmap.objects.filter(user=user, course=course)
        .prefetch_related('steps')
        .order_by('-created_at')
        .first()
    )
    if latest:
        return roadmap_payload(latest)

    latest_attempt = (
        AssessmentAttempt.objects.filter(user=user, selected_course=course, finished_at__isnull=False)
        .order_by('-finished_at')
        .first()
    )
    points = latest_attempt.overall_points if latest_attempt else 50
    level = user.profile.current_level or 'Beginner'
    interests = list(user.profile.interests.values_list('name', flat=True))
    return get_or_generate_roadmap(user, course, level, points, interests)
