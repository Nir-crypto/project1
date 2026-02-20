import hashlib
import random


TOPIC_STEP_BANK = {
    'Python': [
        ('Python Fundamentals Sprint', 'Refresh syntax, loops, functions, and data structures.', 'Can solve beginner Python tasks confidently'),
        ('Error Handling Mastery', 'Practice exceptions, debugging, and tracing.', 'Diagnose runtime errors faster'),
        ('OOP in Practice', 'Implement classes, inheritance, and composition.', 'Design cleaner and reusable modules'),
        ('Mini Project: CLI Tool', 'Build a command-line productivity utility.', 'Ship a small usable Python product'),
        ('Revision / Quiz', 'Timed MCQ and coding revision on weak areas.', 'Retain core concepts and improve speed'),
    ],
    'JavaScript': [
        ('JS Core Revision', 'Strengthen arrays, objects, functions, and scope.', 'Write bug-free fundamental JS'),
        ('Async Patterns', 'Practice promises, async/await, and API calls.', 'Build reliable async workflows'),
        ('DOM & Events', 'Handle event propagation and dynamic rendering.', 'Create interactive interfaces confidently'),
        ('Mini Project: Interactive App', 'Build a small browser app with modular code.', 'End-to-end frontend execution ability'),
        ('Revision / Quiz', 'Take topic-based quizzes and targeted corrections.', 'Higher consistency in assessments'),
    ],
    'Data Science': [
        ('Data Wrangling Basics', 'Clean and prepare tabular datasets in pandas.', 'Produce analysis-ready datasets'),
        ('EDA Deep Dive', 'Apply visual and statistical exploratory workflows.', 'Generate clear data insights'),
        ('Modeling Fundamentals', 'Train baseline models and compare metrics.', 'Select models with justified metrics'),
        ('Mini Project: End-to-End Analysis', 'Build a complete mini DS workflow from raw data to report.', 'Portfolio-ready project output'),
        ('Revision / Quiz', 'Reinforce metrics, preprocessing, and validation concepts.', 'Better reliability under timed tests'),
    ],
    'SQL': [
        ('SQL Query Essentials', 'Practice SELECT, JOIN, GROUP BY, and filtering.', 'Write production-grade analytical queries'),
        ('Optimization Basics', 'Use indexes and query plans to improve performance.', 'Improve query runtime systematically'),
        ('Mini Project: Reporting Schema', 'Design and query a reporting database.', 'Deliver actionable insights from relational data'),
        ('Revision / Quiz', 'Timed SQL practice with common interview patterns.', 'Higher accuracy and speed in SQL tasks'),
    ],
    'Web Development': [
        ('HTML/CSS Foundation Refresh', 'Strengthen semantic structure and responsive layouts.', 'Build cleaner responsive pages'),
        ('Backend API Patterns', 'Implement CRUD and auth-safe endpoint design.', 'Develop maintainable service APIs'),
        ('Mini Project: Full Feature Module', 'Build one complete module from UI to API.', 'Improve full-stack integration confidence'),
        ('Revision / Quiz', 'Review architecture, security, and deployment basics.', 'Solidify full-stack fundamentals'),
    ],
    'Java': [
        ('Java Core Revision', 'Review classes, objects, methods, and access modifiers.', 'Write cleaner Java fundamentals'),
        ('Collections and Generics', 'Practice List, Set, Map, and typed containers.', 'Use data structures effectively in Java'),
        ('OOP Deep Practice', 'Apply abstraction, inheritance, and polymorphism with real examples.', 'Design maintainable object models'),
        ('Mini Project: Console Application', 'Build a complete menu driven Java app with file IO.', 'Deliver a working Java project'),
        ('Revision / Quiz', 'Reinforce exceptions, streams, and interview style MCQs.', 'Improve speed and consistency in assessments'),
    ],
    'AI/ML': [
        ('ML Math Refresher', 'Review core probability, loss, and optimization basics.', 'Stronger intuition for model behavior'),
        ('Feature Engineering Lab', 'Create robust features and validate impact.', 'Improve model quality via data-centric tuning'),
        ('Model Evaluation Deep Dive', 'Use cross-validation and error analysis workflows.', 'Make reliable model selection decisions'),
        ('Mini Project: ML Pipeline', 'Build a train-evaluate-report mini pipeline.', 'Complete a deployable baseline model'),
        ('Revision / Quiz', 'Reinforce overfitting, leakage, and metric tradeoffs.', 'Better judgment in real model development'),
    ],
    'Cloud': [
        ('Cloud Core Concepts', 'Review compute, storage, and networking services.', 'Understand service tradeoffs confidently'),
        ('Deployment Basics', 'Package and deploy application workloads.', 'Ship repeatable cloud deployments'),
        ('Mini Project: Cloud Deployment', 'Deploy and monitor one app in cloud.', 'Hands-on cloud delivery confidence'),
        ('Revision / Quiz', 'Security, cost, and reliability review quiz.', 'Improve cloud architecture decision quality'),
    ],
}


RESOURCE_BANK = [
    ('Official Documentation', ''),
    ('Hands-on Practice Sheet', ''),
    ('Guided Lab', ''),
    ('Reference Notes', ''),
]


def _prompt_signature(course_id, current_level, overall_points, interests_snapshot):
    text = f"{course_id}|{current_level}|{round(overall_points)}|{interests_snapshot}"
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def generate_local_ai_roadmap(user, course, current_level, overall_points, interests_list):
    interests_snapshot = ','.join(sorted(interests_list or []))
    signature = _prompt_signature(course.id, current_level, overall_points, interests_snapshot)

    seed_input = f"{user.id}:{course.id}:{current_level}:{round(overall_points)}:{interests_snapshot}"
    seed = int(hashlib.sha256(seed_input.encode('utf-8')).hexdigest(), 16) % (2 ** 32)
    rng = random.Random(seed)

    if current_level == 'Beginner':
        step_count = rng.randint(8, 10)
    elif current_level == 'Intermediate':
        step_count = rng.randint(7, 9)
    else:
        step_count = rng.randint(6, 8)

    topic_key = course.topic if course.topic in TOPIC_STEP_BANK else 'Python'
    base_steps = TOPIC_STEP_BANK[topic_key][:]
    rng.shuffle(base_steps)

    steps = []
    idx = 1

    needs_fundamentals = overall_points < 50
    advanced_focus = overall_points > 80

    while len(steps) < step_count:
        title, description, outcome = base_steps[len(steps) % len(base_steps)]

        if needs_fundamentals and 'Mini Project' in title:
            title = 'Fundamentals Deep Practice'
            description = 'Spend extra cycles on core concepts and worked examples.'
            outcome = 'Strong concept base before advanced tasks'

        if advanced_focus and 'Revision / Quiz' in title:
            title = 'Capstone Readiness Check'
            description = 'Perform advanced scenario-based quiz and architecture review.'
            outcome = 'Confident transition to complex project execution'

        if interests_list and idx <= 2:
            description = f"{description} Emphasis: {interests_list[(idx - 1) % len(interests_list)]}."

        est_time = round(rng.uniform(0.5, 10.0), 1)
        resource_title, resource_url = RESOURCE_BANK[rng.randint(0, len(RESOURCE_BANK) - 1)]

        steps.append(
            {
                'step_no': idx,
                'title': title,
                'description': description,
                'est_time_hours': est_time,
                'outcome': outcome,
                'resource_title': resource_title,
                'resource_url': resource_url,
            }
        )
        idx += 1

    titles = [step['title'].lower() for step in steps]
    if not any('mini project' in title for title in titles):
        steps[-2]['title'] = 'Mini Project Implementation'
        steps[-2]['description'] = f"Build a practical project in {course.topic} using your current skill stack."
        steps[-2]['outcome'] = 'Demonstrate real-world implementation ability'

    if not any('revision' in title or 'quiz' in title for title in titles):
        steps[-1]['title'] = 'Revision / Quiz'
        steps[-1]['description'] = 'Take a timed assessment to reinforce key concepts and weak areas.'
        steps[-1]['outcome'] = 'Improved retention and faster problem-solving'

    return {
        'prompt_signature': signature,
        'interests_snapshot': interests_snapshot,
        'steps': steps,
    }
