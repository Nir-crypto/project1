import { QUESTION_BANK } from '../data/questionBank';

const STORAGE_KEY = 'rbep_store_v1';
const TOTAL_QUESTIONS = 10;
const FINAL_QUESTIONS = 5;
const TARGET_TIME = 20;
const DIFFICULTY_ORDER = ['easy', 'medium', 'hard'];

const DEFAULT_INTERESTS = [
  { id: 1, name: 'Python' },
  { id: 2, name: 'JavaScript' },
  { id: 3, name: 'Data Science' },
];

const DEFAULT_COURSES = [
  { id: 1, title: 'Python Fundamentals', topic: 'Python', difficulty: 'easy', description: 'Core Python basics.', url: 'https://example.com/python-fundamentals' },
  { id: 2, title: 'Python OOP', topic: 'Python', difficulty: 'medium', description: 'OOP and clean architecture.', url: 'https://example.com/python-oop' },
  { id: 3, title: 'Advanced Python Patterns', topic: 'Python', difficulty: 'hard', description: 'Advanced idioms and patterns.', url: 'https://example.com/advanced-python' },
  { id: 4, title: 'Python for APIs', topic: 'Python', difficulty: 'medium', description: 'Building REST APIs.', url: 'https://example.com/python-apis' },
  { id: 5, title: 'Python Testing', topic: 'Python', difficulty: 'hard', description: 'Reliable tests in Python.', url: 'https://example.com/python-testing' },
  { id: 6, title: 'Automation with Python', topic: 'Python', difficulty: 'easy', description: 'Automate daily tasks.', url: 'https://example.com/python-automation' },
  { id: 7, title: 'JavaScript Basics', topic: 'JavaScript', difficulty: 'easy', description: 'JS syntax and fundamentals.', url: 'https://example.com/js-basics' },
  { id: 8, title: 'Modern JavaScript', topic: 'JavaScript', difficulty: 'medium', description: 'ES6+, modules, async.', url: 'https://example.com/modern-js' },
  { id: 9, title: 'Advanced JavaScript', topic: 'JavaScript', difficulty: 'hard', description: 'Closures, prototypes, event loop.', url: 'https://example.com/advanced-js' },
  { id: 10, title: 'React Essentials', topic: 'JavaScript', difficulty: 'medium', description: 'Reusable component architecture.', url: 'https://example.com/react-essentials' },
  { id: 11, title: 'Frontend Performance', topic: 'JavaScript', difficulty: 'hard', description: 'Optimize render and bundle.', url: 'https://example.com/frontend-performance' },
  { id: 12, title: 'DOM and Browser APIs', topic: 'JavaScript', difficulty: 'easy', description: 'DOM and browser integration.', url: 'https://example.com/dom-browser' },
  { id: 13, title: 'Data Science Foundations', topic: 'Data Science', difficulty: 'easy', description: 'Data workflows and basics.', url: 'https://example.com/ds-foundations' },
  { id: 14, title: 'Pandas and NumPy', topic: 'Data Science', difficulty: 'medium', description: 'Data manipulation toolkit.', url: 'https://example.com/pandas-numpy' },
  { id: 15, title: 'Feature Engineering', topic: 'Data Science', difficulty: 'hard', description: 'Feature building techniques.', url: 'https://example.com/feature-eng' },
  { id: 16, title: 'Data Visualization', topic: 'Data Science', difficulty: 'easy', description: 'Present clear insights.', url: 'https://example.com/data-viz' },
  { id: 17, title: 'Machine Learning Intro', topic: 'Data Science', difficulty: 'medium', description: 'Train and evaluate models.', url: 'https://example.com/ml-intro' },
  { id: 18, title: 'Production ML Workflows', topic: 'Data Science', difficulty: 'hard', description: 'Ship ML to production.', url: 'https://example.com/production-ml' },
];

const DEFAULT_FEEDBACK_QUESTIONS = [
  { id: 1, question_text: 'How relevant was this course to your goals?', type: 'SCALE', options: ['1', '2', '3', '4', '5'] },
  { id: 2, question_text: 'How was the difficulty?', type: 'RADIO', options: ['Too Easy', 'Just Right', 'Too Hard'] },
  { id: 3, question_text: 'Would you recommend this course?', type: 'RADIO', options: ['Yes', 'Maybe', 'No'] },
  { id: 4, question_text: 'How satisfied are you overall?', type: 'SCALE', options: ['1', '2', '3', '4', '5'] },
];

function cloneQuestions() {
  return QUESTION_BANK.map((q) => ({ ...q }));
}

function needsQuestionMigration(store) {
  if (!Array.isArray(store.questions) || store.questions.length < 30) {
    return true;
  }
  return store.questions.some(
    (q) => typeof q?.text === 'string' && q.text.includes('choose the best answer.')
  );
}

function loadStore() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    const initial = {
      interests: DEFAULT_INTERESTS,
      courses: DEFAULT_COURSES,
      questions: cloneQuestions(),
      feedbackQuestions: DEFAULT_FEEDBACK_QUESTIONS,
      users: [],
      assessments: [],
      finalAttempts: [],
      courseProgress: [],
      feedbackResponses: [],
      session: null,
      counters: { user: 1, attempt: 1, finalAttempt: 1, feedback: 1 },
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(initial));
    return initial;
  }

  const store = JSON.parse(raw);
  if (needsQuestionMigration(store)) {
    store.questions = cloneQuestions();
    saveStore(store);
  }
  return store;
}

function saveStore(store) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
}

function nowIso() {
  return new Date().toISOString();
}

function randomToken(prefix) {
  return `${prefix}_${Math.random().toString(36).slice(2)}${Date.now().toString(36)}`;
}

function publicQuestion(question) {
  if (!question) return null;
  return {
    id: question.id,
    topic: question.topic,
    difficulty: question.difficulty,
    text: question.text,
    option_a: question.option_a,
    option_b: question.option_b,
    option_c: question.option_c,
    option_d: question.option_d,
  };
}

function levelFromPoints(overallPoints) {
  if (overallPoints < 50) return 'Beginner';
  if (overallPoints < 75) return 'Intermediate';
  return 'Advanced';
}

function levelDifficulty(level) {
  if (level === 'Advanced') return 'hard';
  if (level === 'Intermediate') return 'medium';
  return 'easy';
}

function normalizeError(message) {
  throw new Error(message);
}

function getSessionUser(store) {
  if (!store.session?.userId) return null;
  return store.users.find((u) => u.id === store.session.userId) || null;
}

function userPayload(store, user) {
  const interests = user.interestIds.map((id) => store.interests.find((x) => x.id === id)).filter(Boolean);
  return {
    name: user.name,
    email: user.email,
    interests,
    current_level: user.currentLevel,
  };
}

function pickRandom(list) {
  return list[Math.floor(Math.random() * list.length)];
}

function nextDifficulty(current, isCorrect) {
  const currentIdx = DIFFICULTY_ORDER.indexOf(current);
  const idx = currentIdx < 0 ? 0 : currentIdx;
  const nextIdx = isCorrect ? Math.min(idx + 1, 2) : Math.max(idx - 1, 0);
  return DIFFICULTY_ORDER[nextIdx];
}

function streakRatio(flags) {
  if (!flags.length) return 0;
  let max = 0;
  let current = 0;
  for (const v of flags) {
    if (v) {
      current += 1;
      if (current > max) max = current;
    } else {
      current = 0;
    }
  }
  return max / flags.length;
}

function overallPoints(correctCount, totalQuestions, totalTime, correctness) {
  const accuracy = totalQuestions ? correctCount / totalQuestions : 0;
  const avgTime = totalQuestions ? totalTime / totalQuestions : 0;
  const timeFactor = Math.max(0, Math.min(1, 1 - (avgTime / TARGET_TIME)));
  const consistency = streakRatio(correctness);
  return Math.round((70 * accuracy + 20 * timeFactor + 10 * consistency) * 100) / 100;
}

function recommendCourses(store, userId, topic, level, points) {
  const targetDifficulty = levelDifficulty(level);
  const similarUserIds = new Set(
    store.assessments
      .filter((a) => a.userId !== userId && a.finishedAt && Math.abs((a.overallPoints || 0) - points) <= 12)
      .map((a) => a.userId)
  );

  const similarCompleted = new Set(
    store.courseProgress
      .filter((p) => p.status === 'COMPLETED' && similarUserIds.has(p.userId))
      .map((p) => p.courseId)
  );

  const scored = store.courses.map((course) => {
    let score = 0;
    const reasons = [];
    if (course.topic === topic) {
      score += 5;
      reasons.push('Matches your selected topic');
    }
    if (course.difficulty === targetDifficulty) {
      score += 3;
      reasons.push(`Aligned with your current level (${level})`);
    } else if (Math.abs(DIFFICULTY_ORDER.indexOf(course.difficulty) - DIFFICULTY_ORDER.indexOf(targetDifficulty)) === 1) {
      score += 1;
      reasons.push('Slightly above/below your level for progression');
    }
    if (similarCompleted.has(course.id)) {
      score += 2;
      reasons.push('Popular among learners with similar performance');
    }
    return {
      ...course,
      why_recommended: reasons.join('; ') || 'Recommended for your learning profile',
      _score: score,
    };
  });

  scored.sort((a, b) => b._score - a._score);
  return scored.slice(0, 5).map(({ _score, ...rest }) => rest);
}

function findNextQuestion(store, topic, difficulty, askedIds) {
  let candidates = store.questions.filter((q) => q.topic === topic && q.difficulty === difficulty && !askedIds.includes(q.id));
  if (!candidates.length) {
    candidates = store.questions.filter((q) => q.topic === topic && !askedIds.includes(q.id));
  }
  return candidates.length ? pickRandom(candidates) : null;
}

function currentUserOrThrow(store) {
  const user = getSessionUser(store);
  if (!user) normalizeError('Not authenticated.');
  return user;
}

export async function getInterests() {
  return loadStore().interests;
}

export async function registerUser(payload) {
  const store = loadStore();
  const name = (payload.name || '').trim();
  const email = (payload.email || '').trim().toLowerCase();
  const password = payload.password || '';
  const interests = [...new Set(payload.interests || [])];

  if (!name) normalizeError('Name is required.');
  if (!email) normalizeError('Email is required.');
  if (password.length < 6) normalizeError('Password must be at least 6 characters.');
  if (interests.length < 2) normalizeError('Please select at least 2 interests.');
  if (store.users.some((u) => u.email === email)) normalizeError('Email already registered.');
  if (!interests.every((id) => store.interests.some((i) => i.id === id))) normalizeError('One or more selected interests are invalid.');

  const user = {
    id: store.counters.user,
    name,
    email,
    password,
    interestIds: interests,
    currentLevel: 'Beginner',
    createdAt: nowIso(),
  };
  store.counters.user += 1;
  store.users.push(user);
  saveStore(store);
  return { message: 'Registration successful.', user: userPayload(store, user) };
}

export async function loginUser(email, password) {
  const store = loadStore();
  const normalized = (email || '').trim().toLowerCase();
  const user = store.users.find((u) => u.email === normalized && u.password === password);
  if (!user) normalizeError('Invalid email or password.');

  const access = randomToken('access');
  const refresh = randomToken('refresh');
  store.session = { userId: user.id, access, refresh };
  saveStore(store);

  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);

  return { access, refresh, user: userPayload(store, user) };
}

export async function logoutUser() {
  const store = loadStore();
  store.session = null;
  saveStore(store);
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

export async function getCurrentUser() {
  const store = loadStore();
  const user = currentUserOrThrow(store);
  return userPayload(store, user);
}

export async function getDashboardData() {
  const store = loadStore();
  const user = currentUserOrThrow(store);

  const completedProgress = store.courseProgress.filter((p) => p.userId === user.id && p.status === 'COMPLETED');
  const completedCourses = completedProgress.map((p) => {
    const course = store.courses.find((c) => c.id === p.courseId);
    return {
      id: course?.id,
      title: course?.title,
      topic: course?.topic,
      difficulty: course?.difficulty,
      score: p.score,
      completed_at: p.completedAt,
    };
  }).filter((c) => c.id);

  const totalCourses = store.courses.length || 1;
  return {
    current_level: user.currentLevel,
    completed_courses: completedCourses,
    progress_stats: {
      completed_count: completedCourses.length,
      total_courses: totalCourses,
      completion_rate: Math.round((completedCourses.length / totalCourses) * 10000) / 100,
    },
  };
}

export async function startAssessment(interestId) {
  const store = loadStore();
  const user = currentUserOrThrow(store);

  const interest = store.interests.find((i) => i.id === Number(interestId));
  if (!interest) normalizeError('Invalid interest.');
  if (!user.interestIds.includes(interest.id)) normalizeError('Please choose one of your selected interests.');

  const question = findNextQuestion(store, interest.name, 'easy', []);
  if (!question) normalizeError('No questions available for this topic.');

  const attempt = {
    id: store.counters.attempt,
    userId: user.id,
    topic: interest.name,
    startedAt: nowIso(),
    finishedAt: null,
    currentDifficulty: 'easy',
    totalQuestions: TOTAL_QUESTIONS,
    correctCount: 0,
    totalTime: 0,
    overallPoints: 0,
    predictedLevel: user.currentLevel,
    answers: [],
    recommendedCourses: [],
  };
  store.counters.attempt += 1;
  store.assessments.push(attempt);
  saveStore(store);

  return {
    attempt_id: attempt.id,
    question: publicQuestion(question),
    progress: { index: 1, total: attempt.totalQuestions },
    current_level: user.currentLevel,
  };
}

export async function answerAssessment(payload) {
  const store = loadStore();
  const user = currentUserOrThrow(store);
  const attempt = store.assessments.find((a) => a.id === Number(payload.attempt_id) && a.userId === user.id);
  if (!attempt) normalizeError('Attempt not found.');
  if (attempt.finishedAt) normalizeError('Attempt already completed.');

  const question = store.questions.find((q) => q.id === Number(payload.question_id));
  if (!question || question.topic !== attempt.topic) normalizeError('Invalid question.');
  if (attempt.answers.some((a) => a.questionId === question.id)) normalizeError('Question already answered.');

  const selected = String(payload.selected_option || '').toLowerCase();
  if (!['a', 'b', 'c', 'd'].includes(selected)) normalizeError('Invalid selected option.');

  const isCorrect = selected === question.correct_option;
  attempt.answers.push({
    questionId: question.id,
    selectedOption: selected,
    isCorrect,
    timeSpent: Number(payload.time_spent || 0),
  });
  attempt.correctCount += isCorrect ? 1 : 0;
  attempt.totalTime += Number(payload.time_spent || 0);
  attempt.currentDifficulty = nextDifficulty(attempt.currentDifficulty, isCorrect);

  const askedIds = attempt.answers.map((a) => a.questionId);
  const answeredCount = askedIds.length;

  const finalizeAttempt = () => {
    attempt.finishedAt = nowIso();
    const correctness = attempt.answers.map((a) => a.isCorrect);
    attempt.overallPoints = overallPoints(attempt.correctCount, attempt.totalQuestions, attempt.totalTime, correctness);
    attempt.predictedLevel = levelFromPoints(attempt.overallPoints);
    user.currentLevel = attempt.predictedLevel;
    attempt.recommendedCourses = recommendCourses(store, user.id, attempt.topic, attempt.predictedLevel, attempt.overallPoints);
    saveStore(store);
    return {
      done: true,
      overall_points: attempt.overallPoints,
      current_level: attempt.predictedLevel,
      recommended_courses: attempt.recommendedCourses,
    };
  };

  if (answeredCount >= attempt.totalQuestions) {
    return finalizeAttempt();
  }

  const nextQuestion = findNextQuestion(store, attempt.topic, attempt.currentDifficulty, askedIds);
  if (!nextQuestion) {
    attempt.totalQuestions = answeredCount;
    return finalizeAttempt();
  }

  saveStore(store);
  return {
    done: false,
    is_correct: isCorrect,
    new_difficulty: attempt.currentDifficulty,
    next_question: publicQuestion(nextQuestion),
    progress: { index: answeredCount + 1, total: attempt.totalQuestions },
  };
}

export async function getResult(attemptId) {
  const store = loadStore();
  const user = currentUserOrThrow(store);
  const attempt = store.assessments.find((a) => a.id === Number(attemptId) && a.userId === user.id);
  if (!attempt) normalizeError('Result not found.');
  return {
    overall_points: attempt.overallPoints,
    current_level: attempt.predictedLevel,
    recommended_courses: attempt.recommendedCourses,
  };
}

export async function startFinalAssessment(courseId) {
  const store = loadStore();
  const user = currentUserOrThrow(store);
  const course = store.courses.find((c) => c.id === Number(courseId));
  if (!course) normalizeError('Course not found.');

  let questions = store.questions.filter((q) => q.topic === course.topic && q.difficulty === course.difficulty);
  if (questions.length < FINAL_QUESTIONS) {
    const fallback = store.questions.filter((q) => q.topic === course.topic);
    questions = [...questions, ...fallback];
  }

  const dedup = [];
  const seen = new Set();
  for (const q of questions) {
    if (!seen.has(q.id)) {
      seen.add(q.id);
      dedup.push(q);
    }
  }

  while (dedup.length > FINAL_QUESTIONS) {
    dedup.splice(Math.floor(Math.random() * dedup.length), 1);
  }
  if (!dedup.length) normalizeError('No final assessment questions available.');

  let progress = store.courseProgress.find((p) => p.userId === user.id && p.courseId === course.id);
  if (!progress) {
    progress = { userId: user.id, courseId: course.id, status: 'IN_PROGRESS', completedAt: null, score: 0 };
    store.courseProgress.push(progress);
  } else if (progress.status !== 'COMPLETED') {
    progress.status = 'IN_PROGRESS';
  }
  saveStore(store);

  return {
    course: { id: course.id, title: course.title, topic: course.topic, difficulty: course.difficulty },
    questions: dedup.map(publicQuestion),
  };
}

export async function submitFinalAssessment(payload) {
  const store = loadStore();
  const user = currentUserOrThrow(store);
  const course = store.courses.find((c) => c.id === Number(payload.course_id));
  if (!course) normalizeError('Course not found.');
  const answers = Array.isArray(payload.answers) ? payload.answers : [];
  if (!answers.length) normalizeError('Answers are required.');

  const ids = answers.map((a) => Number(a.question_id));
  const uniqueIds = new Set(ids);
  if (ids.length !== uniqueIds.size) normalizeError('Duplicate question IDs are not allowed.');

  const questionMap = new Map(
    store.questions.filter((q) => uniqueIds.has(q.id) && q.topic === course.topic).map((q) => [q.id, q])
  );
  if (questionMap.size !== uniqueIds.size) normalizeError('Invalid submitted questions for selected course.');

  let correct = 0;
  for (const ans of answers) {
    const q = questionMap.get(Number(ans.question_id));
    const selected = String(ans.selected_option || '').toLowerCase();
    if (['a', 'b', 'c', 'd'].includes(selected) && selected === q.correct_option) {
      correct += 1;
    }
  }

  const score = Math.round((correct / answers.length) * 10000) / 100;
  const passed = score >= 60;
  const attemptsCount = store.finalAttempts.filter((a) => a.userId === user.id && a.courseId === course.id).length + 1;
  const finalAttempt = {
    id: store.counters.finalAttempt,
    userId: user.id,
    courseId: course.id,
    score,
    passed,
    attemptsCount,
    createdAt: nowIso(),
  };
  store.counters.finalAttempt += 1;
  store.finalAttempts.push(finalAttempt);

  let progress = store.courseProgress.find((p) => p.userId === user.id && p.courseId === course.id);
  if (!progress) {
    progress = { userId: user.id, courseId: course.id, status: 'IN_PROGRESS', completedAt: null, score: 0 };
    store.courseProgress.push(progress);
  }
  progress.score = score;
  if (passed) {
    progress.status = 'COMPLETED';
    progress.completedAt = nowIso();
  } else {
    progress.status = 'IN_PROGRESS';
  }
  saveStore(store);

  return {
    passed,
    score,
    message: passed ? 'Assessment passed. You can now provide feedback.' : 'Try again. You did not meet the pass threshold.',
    final_attempt_id: finalAttempt.id,
  };
}

export async function getFeedbackQuestions() {
  return loadStore().feedbackQuestions;
}

export async function submitFeedback(payload) {
  const store = loadStore();
  const user = currentUserOrThrow(store);
  const courseId = Number(payload.course_id);
  const latestPass = [...store.finalAttempts]
    .filter((a) => a.userId === user.id && a.courseId === courseId && a.passed)
    .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))[0];

  if (!latestPass) normalizeError('Feedback allowed only after passing final assessment for this course.');
  if (store.feedbackResponses.some((r) => r.userId === user.id && r.finalAttemptId === latestPass.id)) {
    normalizeError('Feedback for this passed final assessment was already submitted.');
  }

  const feedback = {
    id: store.counters.feedback,
    userId: user.id,
    courseId,
    finalAttemptId: latestPass.id,
    responses: payload.responses || {},
    comment: payload.comment || '',
    createdAt: nowIso(),
  };
  store.counters.feedback += 1;
  store.feedbackResponses.push(feedback);
  saveStore(store);
  return { message: 'Feedback submitted successfully.', feedback_id: feedback.id };
}
