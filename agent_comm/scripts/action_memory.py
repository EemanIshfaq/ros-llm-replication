import re
from collections import deque

REPEAT_PATTERNS = [
    r'\brepeat\b', r'\bdo that again\b', r'\bdo it again\b',
    r'\bsame again\b', r'\bone more time\b', r'\bagain\b',
    r'\bredo\b', r'\brerun\b', r'\breplay\b',
    r'\bsame as before\b', r'\bdo the same\b',
]

NAMED_REPEAT_PATTERNS = [
    r'(?:repeat|redo|do|run|execute)\s+(?:the\s+)?(\w+)\s*(?:again)?',
    r'(\w+)\s+again',
]

class ActionMemory:
    def __init__(self, maxlen=10):
        self._history = deque(maxlen=maxlen)
        self._last = None

    def store(self, human_input, action_ndjson):
        if is_repeat_intent(human_input):
            return
        entry = {"label": human_input.strip().lower(), "action": action_ndjson.strip(), "count": 1}
        if self._last and self._last["label"] == entry["label"]:
            self._last["count"] += 1
        else:
            self._history.append(entry)
            self._last = entry
        import rospy
        rospy.loginfo("[Memory] Stored: '%s'  (history: %d)", human_input.strip(), len(self._history))

    def recall(self, human_input):
        import rospy
        h = human_input.strip().lower()
        if not self._history:
            rospy.logwarn("[Memory] No previous action to repeat")
            return None
        if is_repeat_intent(h) and not _extract_task_name(h):
            rospy.loginfo("[Memory] Replaying: '%s'", self._last["label"])
            return self._last["action"]
        task_name = _extract_task_name(h)
        if task_name:
            match = self._find_by_name(task_name)
            if match:
                rospy.loginfo("[Memory] Named recall '%s'", task_name)
                return match["action"]
            rospy.logwarn("[Memory] Task '%s' not in history. Calling LLM.", task_name)
            return None
        return None

    def _find_by_name(self, task_name):
        for entry in reversed(self._history):
            if task_name in entry["label"]:
                return entry
        return None

def is_repeat_intent(text):
    t = text.strip().lower()
    for pattern in REPEAT_PATTERNS:
        if re.search(pattern, t):
            return True
    return False

def _extract_task_name(text):
    t = text.strip().lower()
    if not is_repeat_intent(t):
        return None
    stopwords = {'that','it','this','the','a','an','same','again','last','previous','time'}
    for pattern in NAMED_REPEAT_PATTERNS:
        m = re.search(pattern, t)
        if m:
            candidate = m.group(1)
            if candidate not in stopwords and len(candidate) > 2:
                return candidate
    return None
