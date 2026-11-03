
ROADMAP_GENERATION_PROMPT = """
You are an expert AI Career Mentor and Technical Roadmap Planner.

Create a personalized learning roadmap for the candidate.

TARGET JOB ROLE:
{target_role}

CURRENT SKILLS:
{current_skills}

EXPERIENCE LEVEL:
{experience_level}

ROADMAP DURATION:
{duration_weeks} weeks

DAILY STUDY HOURS:
{daily_study_hours}

GENERATION RULES:

1. Create a practical and personalized roadmap.
2. Consider the candidate's existing skills.
3. Focus on technologies required for the target job role.
4. Arrange topics from beginner to advanced.
5. Divide the roadmap into weekly learning phases.
6. Include practical exercises and assignments.
7. Include relevant hands-on projects.
8. Provide realistic weekly learning goals.
9. Avoid unnecessary repetition of known skills.
10. Consider the candidate's available study hours.

WEEKLY PLAN:

For every week, provide:
- Week number.
- Main learning focus.
- Topics to study.
- Practical tasks and exercises.
- Project or assignment.
- Expected learning outcome.

ADDITIONAL REQUIREMENTS:

- Recommend relevant projects.
- Include important technical skills required for the target role.
- Suggest useful development tools and technologies.
- Add measurable learning milestones.
- Keep the roadmap realistic and actionable.
- Do not invent candidate experience or qualifications.

OUTPUT REQUIREMENTS:

Return structured data containing:

1. roadmap_title
2. target_role
3. duration_weeks
4. summary
5. skills_to_learn
6. weekly_plan
7. recommended_projects
8. milestones
9. final_goal

Generate an actionable roadmap that helps the candidate
prepare for the target job role.
"""
