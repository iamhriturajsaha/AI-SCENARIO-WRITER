import re
from src.schema import ScenarioOutput
GENERIC_PATTERNS = [
    r"i am (unhappy|disappointed|not happy|not pleased) with",
    r"we need to talk about your (performance|work|attitude)",
    r"this is (unacceptable|not acceptable|not good enough)",
    r"you need to (do better|improve|step up)",
    r"i('m| am) not (satisfied|impressed)",
    r"what('s| is) going on with (you|your work)",
]
def validate_quality(output: ScenarioOutput, icp_type: str, language: str) -> list[str]:
    issues = []
    chip_issues = _check_strategy_diversity(output.strategy_chips)
    issues.extend(chip_issues)
    rubric_issues = _check_rubric_sanity(output.rubric)
    issues.extend(rubric_issues)
    line_issues = _check_antagonist_line(output.antagonist_opening_line, language)
    issues.extend(line_issues)
    icp_issues = _check_icp_consistency(output, icp_type)
    issues.extend(icp_issues)
    philosophy_issues = _check_philosophy_quality(output.strategy_chips)
    issues.extend(philosophy_issues)
    return issues
def _clean_words(text: str) -> set[str]:
    cleaned = re.sub(r"[^\w\s]", "", text)
    return set(cleaned.split())
def _check_strategy_diversity(chips: list) -> list[str]:
    issues = []
    labels = [chip.label.lower() for chip in chips]
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            words_i = _clean_words(labels[i])
            words_j = _clean_words(labels[j])
            stopwords = {
                "the", "a", "an", "and", "or", "to", "in", "for", "of", "with", "on", "at", "it", "is",
                "है", "की", "को", "में", "से", "और", "का", "के", "लिए", "यह", "कि", "एक", "हैं", "करना", 
                "करने", "हो", "पर", "भी", "ही", "तो", "नहीं", "हम", "आप", "मैं", "मुझे", "मेरा", "अपने", "अपनी", "क्या"
            }
            words_i -= stopwords
            words_j -= stopwords
            if words_i and words_j:
                overlap = len(words_i & words_j) / min(len(words_i), len(words_j))
                if overlap > 0.6:
                    issues.append(
                        f"Strategy chips {i+1} and {j+1} have too similar labels: "
                        f"'{chips[i].label}' vs '{chips[j].label}'. "
                        f"Each chip must represent a fundamentally different approach."
                    )
    philosophies = [chip.philosophy.lower() for chip in chips]
    for i in range(len(philosophies)):
        for j in range(i + 1, len(philosophies)):
            words_i = _clean_words(philosophies[i])
            words_j = _clean_words(philosophies[j])
            stopwords = {
                "the", "a", "an", "and", "or", "to", "in", "for", "of", "with", "on", "at", "it", "is", "by", "this", "that",
                "can", "will", "your", "you", "their", "them", "they", "helps", "help", "way", "make", "more",
                "है", "की", "को", "में", "से", "और", "का", "के", "लिए", "यह", "कि", "एक", "हैं", "करना",
                "करने", "हो", "पर", "भी", "ही", "तो", "नहीं", "हम", "आप", "मैं", "मुझे", "मेरा", "अपने", "अपनी", "क्या",
                "आपको", "इससे", "जिससे", "ताकि", "साथ", "करें", "रूप", "बारे", "तरीके", "बेहतर",
                "ढंग", "प्रभावी", "सकते", "सकता", "सकती", "चाहिए", "करके", "होगी", "होता", "होते", "होती",
                "मदद", "मिलेगी", "करता", "करती", "जाता", "जाती", "रहे", "रहा", "रही",
                "अपना", "उनके", "उनकी", "उन्हें", "वाले", "वाली", "कर", "दे", "ले",
                "टीम", "साथियों", "संबंध", "प्रतिष्ठा", "बढ़ेगी", "बनाने", "बना", "पाएंगे", "जिम्मेदारी", "ज़िम्मेदारी",
                "प्रतिबद्ध", "दिखा", "दिखाने", "प्रयास", "दिखाते", "अगर", "हमारे", "उत्पाद", "गुणवत्ता", "क्लाइंट्स", "क्लाइंट", "क्लाइंटों", "ग्राहकों", "ग्राहक",
                "महसूस", "होगा", "आवश्यकता", "आवश्यकताओं", "ज़रूरत", "ज़रूरतों", "वफादारी", "मजबूत", "वैकल्पिक",
                "प्रतिक्रिया", "व्यवहार्य", "संतुष्टि", "कैसे", "क्यों", "कब", "कहाँ", "कहा", "बोला", "बोलने", "बोलते",
                "सुनते", "सुधार", "संतुष्ट"
            }
            words_i -= stopwords
            words_j -= stopwords
            if words_i and words_j:
                overlap = len(words_i & words_j) / min(len(words_i), len(words_j))
                if overlap > 0.6:
                    issues.append(
                        f"Strategy chips {i+1} and {j+1} have too similar philosophies. "
                        f"Each philosophy must explain a fundamentally DIFFERENT principle."
                    )
    return issues
def _check_rubric_sanity(rubric) -> list[str]:
    issues = []
    scores = [rubric.communication, rubric.composure, rubric.clarity, rubric.strategy, rubric.outcome]
    if len(set(scores)) == 1:
        issues.append(
            f"All rubric axes have the same score ({scores[0]}). "
            f"Different scenarios emphasize different skills — vary the scores. "
            f"For example, a conflict scenario should weight composure higher than clarity."
        )
    if all(s == 50 for s in scores):
        issues.append(
            "All rubric axes are set to 50. This is a lazy default. "
            "Set scores that reflect what THIS specific scenario emphasizes."
        )
    avg = sum(scores) / len(scores)
    variance = sum((s - avg) ** 2 for s in scores) / len(scores)
    if variance < 25 and len(set(scores)) > 1:
        issues.append(
            f"Rubric scores have very low variance (scores: {scores}). "
            f"Some axes should be clearly more important than others for this scenario."
        )
    return issues
def _check_antagonist_line(line: str, language: str) -> list[str]:
    issues = []
    if language == "en":
        line_lower = line.lower()
        for pattern in GENERIC_PATTERNS:
            if re.search(pattern, line_lower):
                issues.append(
                    f"antagonist_opening_line matches generic pattern: '{line}'. "
                    f"The line must reference a SPECIFIC situation and create genuine tension. "
                    f"Example: 'Riya, I just showed the client your dashboard and they asked why it looks like a college project.'"
                )
                break
    word_count = len(line.split())
    if word_count < 8:
        issues.append(
            f"antagonist_opening_line is too short ({word_count} words). "
            f"It needs enough detail to create specific, vivid tension. Aim for 15+ words."
        )
    return issues
def _check_icp_consistency(output: ScenarioOutput, icp_type: str) -> list[str]:
    issues = []
    setting_lower = output.scene.setting.lower()
    context_lower = output.scene.context.lower()
    all_text = f"{setting_lower} {context_lower} {output.episode_title.lower()}"
    if icp_type == "high_wage":
        tech_keywords = [
            "office", "meeting", "standup", "sprint", "code", "review", "tech",
            "product", "engineering", "developer", "software", "slack", "jira",
            "deploy", "api", "feature", "release", "retro", "agile", "scrum",
            "laptop", "desk", "conference", "startup", "company", "team",
            "project", "deadline", "client", "presentation", "report"
        ]
        if not any(kw in all_text for kw in tech_keywords):
            issues.append(
                "high_wage scenario should be set in a tech/corporate context but no tech-related "
                "keywords found in setting or context. Use settings like standups, code reviews, "
                "sprint retros, product meetings."
            )
    else:
        heavy_tech = ["code review", "sprint", "deploy", "api", "agile", "scrum", "jira"]
        if any(kw in all_text for kw in heavy_tech):
            issues.append(
                "low_wage scenario should NOT use heavy tech jargon. "
                "Use service/gig work contexts: customer complaints, delivery issues, "
                "shift scheduling, supervisor interactions."
            )
        service_keywords = [
            "customer", "delivery", "shift", "supervisor", "shop", "counter",
            "store", "warehouse", "call", "support", "complaint", "order",
            "restaurant", "office", "desk", "service", "floor", "manager",
            "work", "job", "staff", "training", "schedule", "salary",
            "team", "colleague", "boss", "company", "cabin",
            "ग्राहक", "कस्टमर", "डिलीवरी", "शिफ्ट", "सुपरवाइजर", "दुकान", "काउंटर",
            "स्टोर", "वेयरहाउस", "कॉल", "सपोर्ट", "शिकायत", "ऑर्डर", 
            "रेस्टोरेंट", "ऑफिस", "डेस्क", "सर्विस", "फ्लोर", "मैनेजर",
            "काम", "जॉब", "स्टाफ", "ट्रेनिंग", "शेड्यूल", "सैलरी",
            "टीम", "बॉस", "कंपनी"
        ]
        if not any(kw in all_text for kw in service_keywords):
            issues.append(
                "low_wage scenario should be set in a service/gig work context but no relevant "
                "keywords found in setting or context. Use settings like customer support centers, "
                "delivery hubs, retail shops, offices for entry-level roles."
            )
    return issues
def _check_philosophy_quality(chips: list) -> list[str]:
    issues = []
    for i, chip in enumerate(chips):
        philosophy = chip.philosophy.lower()
        word_count = len(philosophy.split())
        if word_count < 10:
            issues.append(
                f"Strategy chip {i+1} philosophy is too short ({word_count} words): '{chip.philosophy}'. "
                f"The philosophy must explain WHY this strategy works — the underlying principle."
            )
    return issues
