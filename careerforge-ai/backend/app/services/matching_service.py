import re
from typing import Dict, List, Set, Any

def normalize_text(text: str) -> str:
    """Normalize text for comparison: lowercased, stripped of punctuation."""
    return re.sub(r'[^a-z0-9\s]', '', text.lower()).strip()

def calculate_match_score(resume_data: dict, job_data: dict) -> Dict[str, Any]:
    # Extract sets for matching
    res_skills = set(normalize_text(s) for s in resume_data.get("skills", []) + resume_data.get("programming_languages", []) + resume_data.get("frameworks", []) + resume_data.get("databases", []) + resume_data.get("tools", []))
    
    req_skills = set(normalize_text(s) for s in job_data.get("required_skills", []))
    pref_skills = set(normalize_text(s) for s in job_data.get("preferred_skills", []))
    all_job_skills = req_skills | pref_skills
    
    res_projects_text = " ".join(resume_data.get("projects", []))
    res_projects_norm = normalize_text(res_projects_text)
    
    res_exp_text = " ".join(resume_data.get("experience", []))
    res_exp_norm = normalize_text(res_exp_text)
    
    res_edu_text = " ".join(resume_data.get("education", []))
    res_edu_norm = normalize_text(res_edu_text)
    
    job_techs = set(normalize_text(t) for t in job_data.get("technologies", []))
    job_reqs = set(normalize_text(r) for r in job_data.get("responsibilities", []))
    job_exp = " ".join(job_data.get("experience_requirements", []))
    job_edu = " ".join(job_data.get("education_requirements", []))
    
    # 1. Skill Match (40%)
    matched_skills = []
    missing_skills = []
    partial_matches = []
    
    # Simple strict/partial matching
    for jk in all_job_skills:
        if jk in res_skills:
            matched_skills.append(jk)
        else:
            # Check for partial match (e.g. "react" in "reactjs")
            is_partial = False
            for rs in res_skills:
                if jk in rs or rs in jk:
                    partial_matches.append(jk)
                    is_partial = True
                    break
            if not is_partial:
                missing_skills.append(jk)

    total_target_skills = len(all_job_skills)
    if total_target_skills == 0:
        skill_score = 40.0  # Free pass if no skills required
    else:
        # Full match = 1, Partial = 0.5
        skill_points = len(matched_skills) + (len(partial_matches) * 0.5)
        skill_score = (skill_points / total_target_skills) * 40.0
    
    skill_score = min(skill_score, 40.0)

    # 2. Project Relevance (20%)
    # Check if job tech/skills exist in project descriptions
    project_matches = []
    for tech in list(all_job_skills) + list(job_techs):
        if tech in res_projects_norm:
            project_matches.append(tech)
            
    # Remove duplicates
    project_matches = list(set(project_matches))
    
    target_project_keywords = len(all_job_skills) + len(job_techs)
    if target_project_keywords == 0:
        project_score = 20.0
    else:
        project_score = (len(project_matches) / target_project_keywords) * 20.0
        # Boost score slightly since finding all keywords in projects is rare
        project_score = min(project_score * 2.0, 20.0)
        
    # 3. Experience (15%)
    # Check overlap of required skills in experience text
    exp_matches = 0
    for jk in all_job_skills:
        if jk in res_exp_norm:
            exp_matches += 1
            
    if total_target_skills == 0:
        exp_score = 15.0
    else:
        exp_score = (exp_matches / total_target_skills) * 15.0
        exp_score = min(exp_score * 1.5, 15.0) # Boost
        
    # 4. Education (10%)
    # Very basic: if job requires education, does resume have education?
    edu_score = 0.0
    if not job_data.get("education_requirements"):
        edu_score = 10.0
    elif len(res_edu_text.strip()) > 0:
        # In a real app we'd parse "Bachelor", "Master", but for deterministic we grant 10 if edu section exists
        edu_score = 10.0

    # 5. Keyword Match (15%)
    # Responsibilities keywords overlapping in whole resume
    res_all_norm = res_exp_norm + " " + res_projects_norm + " " + res_edu_norm + " ".join(res_skills)
    kw_hits = 0
    total_kw = 0
    
    # Extract simple words from responsibilities as keywords
    job_req_words = set()
    for req in job_reqs:
        for word in req.split():
            if len(word) > 4: # Ignore stop words loosely
                job_req_words.add(word)
                
    for word in job_req_words:
        if word in res_all_norm:
            kw_hits += 1
            
    if len(job_req_words) == 0:
        kw_score = 15.0
    else:
        kw_score = (kw_hits / len(job_req_words)) * 15.0
        kw_score = min(kw_score * 1.5, 15.0)

    # Final tally
    overall_score = round(skill_score + project_score + exp_score + edu_score + kw_score, 2)
    
    # Recommendations
    recommendations = []
    if missing_skills:
        recommendations.append(f"Consider learning or highlighting these missing skills: {', '.join(missing_skills[:3])}")
    if project_score < 10.0:
        recommendations.append("Add more keywords from the job description into your project descriptions.")
    if exp_score < 7.5:
        recommendations.append("Quantify your experience using terms required by the job.")
        
    if not recommendations and overall_score > 80:
        recommendations.append("Your resume is a strong match for this position!")

    # Format original case for output where possible, but for simplicity we use the normalized
    return {
        "overall_score": overall_score,
        "details": {
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "partial_matches": partial_matches,
            "project_matches": project_matches,
            "recommendations": recommendations
        }
    }
