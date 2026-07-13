def evaluate_step(answer, question_data):
    ans = answer.lower()
    keywords = [k.lower() for k in question_data['keywords']]
    
    # Keyword coverage
    found = [k for k in keywords if k in ans]
    missing = [k for k in question_data['keywords'] if k.lower() not in ans]
    
    # Technical score based on keywords
    tech_score = int((len(found) / len(keywords)) * 100) if keywords else 100
    
    # Comm score based on length and structure
    words = len(ans.split())
    comm_score = min(100, int((words / 30) * 100)) if words > 0 else 0
    
    # Overall confidence
    conf = int((tech_score + comm_score) / 2)
    
    # Insights
    strengths = "Good keyword usage." if tech_score > 60 else "Attempted to answer."
    weaknesses = f"Missed keys: {', '.join(missing)}." if missing else "None detected."
    suggestions = "Review the missing keywords." if missing else "Keep it up."
    
    return {
        "technical_score": tech_score,
        "communication_score": comm_score,
        "overall_confidence": conf,
        "missing_keywords": missing,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions
    }