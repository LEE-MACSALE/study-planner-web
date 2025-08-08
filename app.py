from flask import Flask, render_template, request
from collections import defaultdict

app = Flask(__name__)
subjects = []

@app.route('/', methods=['GET', 'POST'])
def index():
    global subjects
    schedule = {}

    if request.method == 'POST':
        action = request.form.get('action')

        # 과목 추가 처리
        if action == 'add':
            subject = request.form.get('subject')
            time = request.form.get('time')

            if subject and time:
                try:
                    time = float(time)
                    # 같은 이름 과목이 있으면 덮어쓰기
                    subjects = [(s, t) for s, t in subjects if s != subject]
                    subjects.append((subject, time))
                except ValueError:
                    pass  # 숫자가 아니면 무시

        # 계획 생성 처리
        elif action == 'generate':
            if subjects:
                schedule = generate_schedule(subjects)

    return render_template('index.html', subjects=subjects, schedule=schedule)

def generate_schedule(subjects):
    total_hours = sum(t for _, t in subjects)
    day_names = ['월', '화', '수', '목', '금', '토', '일']
    weights = [0.18, 0.18, 0.18, 0.16, 0.10, 0.10, 0.10]
    daily_targets = [round(total_hours * w, 2) for w in weights]
    daily_remaining = daily_targets[:]
    subject_hours = {name: time for name, time in subjects}
    plan = defaultdict(list)

    index = 0
    while any(v > 0 for v in subject_hours.values()):
        name, remaining = list(subject_hours.items())[index % len(subject_hours)]
        if remaining <= 0:
            index += 1
            continue
        for i in range(7):
            if subject_hours[name] <= 0 or daily_remaining[i] <= 0:
                continue
            alloc = min(subject_hours[name], daily_remaining[i], 2.0)
            plan[day_names[i]].append((name, alloc))
            subject_hours[name] -= alloc
            daily_remaining[i] -= alloc
        index += 1

    return dict(plan)

if __name__ == '__main__':
    app.run(debug=True)
