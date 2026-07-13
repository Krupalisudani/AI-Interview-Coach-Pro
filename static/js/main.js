document.addEventListener('DOMContentLoaded', () => {
    
    // Index Page Form Handling
    const setupForm = document.getElementById('setup-form');
    if (setupForm) {
        setupForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const name = document.getElementById('candidate-name').value;
            const role = document.getElementById('interview-role').value;
            
            sessionStorage.setItem('interview_name', name);
            sessionStorage.setItem('interview_role', role);
            
            window.location.href = '/interview';
        });
    }

    // Interview Page Logic
    const interviewContainer = document.querySelector('.interview-layout');
    if (interviewContainer) {
        let questions = [];
        let currentIndex = 0;
        let transcript = [];
        let timerInterval;
        let secondsElapsed = 0;

        const role = sessionStorage.getItem('interview_role');
        const name = sessionStorage.getItem('interview_name');

        if (!role || !name) {
            window.location.href = '/'; // redirect if accessed directly
            return;
        }

        // DOM Elements
        const elQCounter = document.getElementById('question-counter');
        const elQCategory = document.getElementById('question-category');
        const elQText = document.getElementById('question-text');
        const elAnswer = document.getElementById('answer-input');
        const elProgress = document.getElementById('progress-fill');
        const elTimer = document.getElementById('timer');
        
        const btnPrev = document.getElementById('btn-prev');
        const btnEval = document.getElementById('btn-eval');
        const btnNext = document.getElementById('btn-next');
        const btnFinish = document.getElementById('btn-finish');

        // Sidebar Elements
        const elTechScore = document.getElementById('tech-score');
        const elCommScore = document.getElementById('comm-score');
        const elStrengths = document.getElementById('eval-strengths');
        const elWeaknesses = document.getElementById('eval-weaknesses');
        const elSuggestions = document.getElementById('eval-suggestions');
        const elKeywords = document.getElementById('eval-keywords');

        // Fetch Questions
        fetch(`/api/get_questions?role=${encodeURIComponent(role)}`)
            .then(res => res.json())
            .then(data => {
                questions = data.questions;
                renderQuestion();
                startTimer();
            });

        function formatTime(sec) {
            const m = Math.floor(sec / 60).toString().padStart(2, '0');
            const s = (sec % 60).toString().padStart(2, '0');
            return `${m}:${s}`;
        }

        function startTimer() {
            timerInterval = setInterval(() => {
                secondsElapsed++;
                elTimer.innerText = formatTime(secondsElapsed);
            }, 1000);
        }

        function renderQuestion() {
            const q = questions[currentIndex];
            elQCounter.innerText = `Question ${currentIndex + 1} / ${questions.length}`;
            elQCategory.innerText = q.category;
            
            elQCategory.className = 'badge';
            if(q.category === 'Easy') elQCategory.classList.add('badge-easy');
            else if(q.category === 'Medium') elQCategory.classList.add('badge-medium');
            else elQCategory.classList.add('badge-hard');

            elQText.innerText = q.question;
            elProgress.style.width = `${((currentIndex) / questions.length) * 100}%`;

            // Reset UI for new or cached answer
            if (transcript[currentIndex]) {
                elAnswer.value = transcript[currentIndex].answer;
                updateSidebar(transcript[currentIndex]);
                btnEval.style.display = 'none';
                if(currentIndex === questions.length - 1) {
                    btnFinish.style.display = 'inline-block';
                    btnNext.style.display = 'none';
                } else {
                    btnNext.style.display = 'inline-block';
                    btnFinish.style.display = 'none';
                }
            } else {
                elAnswer.value = '';
                resetSidebar();
                btnEval.style.display = 'inline-block';
                btnNext.style.display = 'none';
                btnFinish.style.display = 'none';
            }

            btnPrev.disabled = currentIndex === 0;
        }

        function resetSidebar() {
            elTechScore.innerText = '--';
            elCommScore.innerText = '--';
            elStrengths.innerText = 'Awaiting evaluation...';
            elWeaknesses.innerText = 'Awaiting evaluation...';
            elSuggestions.innerText = 'Awaiting evaluation...';
            elKeywords.innerHTML = '<span class="tag placeholder">None yet</span>';
        }

        function updateSidebar(data) {
            elTechScore.innerText = data.technical_score;
            elCommScore.innerText = data.communication_score;
            elStrengths.innerText = data.strengths;
            elWeaknesses.innerText = data.weaknesses;
            elSuggestions.innerText = data.suggestions;
            
            elKeywords.innerHTML = '';
            if (data.missing_keywords && data.missing_keywords.length > 0) {
                data.missing_keywords.forEach(kw => {
                    const span = document.createElement('span');
                    span.className = 'tag';
                    span.innerText = kw;
                    elKeywords.appendChild(span);
                });
            } else {
                elKeywords.innerHTML = '<span class="tag">All covered!</span>';
            }
        }

        btnEval.addEventListener('click', () => {
            const answer = elAnswer.value.trim();
            if(!answer) return alert("Please provide an answer first.");

            const q = questions[currentIndex];
            const payload = {
                answer: answer,
                question_id: q.id,
                role: role
            };

            btnEval.innerText = "Evaluating...";
            btnEval.disabled = true;

            fetch('/api/evaluate_step', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                // Save to transcript
                transcript[currentIndex] = {
                    question: q.question,
                    ideal_answer: q.ideal_answer,
                    answer: answer,
                    ...data
                };
                
                updateSidebar(data);
                
                btnEval.style.display = 'none';
                btnEval.innerText = "Evaluate Answer";
                btnEval.disabled = false;

                if (currentIndex === questions.length - 1) {
                    btnFinish.style.display = 'inline-block';
                } else {
                    btnNext.style.display = 'inline-block';
                }
            });
        });

        btnPrev.addEventListener('click', () => {
            if (currentIndex > 0) {
                currentIndex--;
                renderQuestion();
            }
        });

        btnNext.addEventListener('click', () => {
            if (currentIndex < questions.length - 1) {
                currentIndex++;
                renderQuestion();
            }
        });

        btnFinish.addEventListener('click', () => {
            clearInterval(timerInterval);
            
            // Calculate overall average
            let total = 0;
            transcript.forEach(t => total += t.overall_confidence);
            const overall = Math.round(total / questions.length);

            const payload = {
                name: name,
                role: role,
                overall_score: overall,
                transcript: transcript
            };

            btnFinish.innerText = "Submitting...";
            btnFinish.disabled = true;

            fetch('/api/submit_interview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                if(data.success) {
                    window.location.href = `/dashboard/${data.id}`;
                }
            });
        });
    }
});