import re

with open('page_course.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Pattern for createServerReference
matches = list(re.finditer(r'createServerReference\)\("([^"]+)",[^,]+,[^,]+,[^,]+,"([^"]+)"\)', code))
print(f"Total server actions found in course page: {len(matches)}")
for m in matches:
    action_id = m.group(1)
    func_name = m.group(2)
    print(f"  Function: {func_name:<25} | ID: {action_id}")
