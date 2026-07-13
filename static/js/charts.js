document.addEventListener('DOMContentLoaded', () => {
    const rawDataScript = document.getElementById('transcript-data');
    if (!rawDataScript) return;

    // Parse transcript from hidden JSON block
    const transcript = JSON.parse(rawDataScript.textContent || "[]");
    if (transcript.length === 0) return;

    // View toggler logic
    const btnToggle = document.getElementById('btn-toggle-transcript');
    const viewDash = document.getElementById('dashboard-view');
    const viewTrans = document.getElementById('transcript-view');
    const reportContent = document.getElementById('report-content');

    btnToggle.addEventListener('click', () => {
        if(viewDash.style.display !== 'none') {
            viewDash.style.display = 'none';
            viewTrans.style.display = 'block';
            btnToggle.innerText = 'Back to Dashboard';
            renderReport();
        } else {
            viewDash.style.display = 'block';
            viewTrans.style.display = 'none';
            btnToggle.innerText = 'View Transcript';
        }
    });

    // Populate dynamic Averages
    let sumTech = 0, sumComm = 0, strengthsCount = 0, weakCount = 0;
    const scoresTech = [], scoresComm = [], labels = [];

    transcript.forEach((t, i) => {
        sumTech += t.technical_score;
        sumComm += t.communication_score;
        scoresTech.push(t.technical_score);
        scoresComm.push(t.communication_score);
        labels.push(`Q${i+1}`);
        if(t.technical_score > 70) strengthsCount++; else weakCount++;
    });

    const avgTech = Math.round(sumTech / transcript.length);
    const avgComm = Math.round(sumComm / transcript.length);
    const overall = Math.round((avgTech + avgComm) / 2);

    document.getElementById('avg-tech').innerText = avgTech + '%';
    document.getElementById('avg-comm').innerText = avgComm + '%';

    // Chart Global Defaults
    Chart.defaults.color = document.body.classList.contains('dark-theme') ? '#f8fafc' : '#1e293b';
    Chart.defaults.font.family = 'Inter';

    // 1. Bar Chart (Progression)
    new Chart(document.getElementById('barChart'), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                { label: 'Technical', data: scoresTech, backgroundColor: 'rgba(59, 130, 246, 0.7)' },
                { label: 'Communication', data: scoresComm, backgroundColor: 'rgba(16, 185, 129, 0.7)' }
            ]
        },
        options: { responsive: true, scales: { y: { beginAtZero: true, max: 100 } } }
    });

    // 2. Radar Chart (Skills)
    new Chart(document.getElementById('radarChart'), {
        type: 'radar',
        data: {
            labels: ['Technical Accuracy', 'Keyword Coverage', 'Communication', 'Completeness', 'Confidence'],
            datasets: [{
                label: 'Candidate Skills',
                data: [avgTech, avgTech - 10, avgComm, (avgTech+avgComm)/2, overall],
                backgroundColor: 'rgba(59, 130, 246, 0.2)',
                borderColor: 'rgba(59, 130, 246, 1)',
                pointBackgroundColor: 'rgba(59, 130, 246, 1)'
            }]
        },
        options: { scales: { r: { beginAtZero: true, max: 100 } } }
    });

    // 3. Gauge Chart (Overall Doughnut)
    new Chart(document.getElementById('gaugeChart'), {
        type: 'doughnut',
        data: {
            labels: ['Score', 'Remaining'],
            datasets: [{
                data: [overall, 100 - overall],
                backgroundColor: ['rgba(16, 185, 129, 0.8)', 'rgba(0,0,0,0.1)'],
                borderWidth: 0
            }]
        },
        options: {
            rotation: -90,
            circumference: 180,
            cutout: '80%',
            responsive: true,
            plugins: { tooltip: { enabled: false } }
        }
    });

    // 4. Pie Chart (Strengths vs Weaknesses)
    new Chart(document.getElementById('pieChart'), {
        type: 'pie',
        data: {
            labels: ['Strong Answers', 'Needs Improvement'],
            datasets: [{
                data: [strengthsCount, weakCount],
                backgroundColor: ['rgba(59, 130, 246, 0.8)', 'rgba(239, 68, 68, 0.8)']
            }]
        }
    });

    // Render detailed report layout
    function renderReport() {
        if(reportContent.innerHTML.trim() !== '') return; // already rendered
        
        let html = '';
        transcript.forEach((t, i) => {
            html += `
                <div class="report-item glass-card" style="margin-bottom: 1.5rem;">
                    <h4>Q${i+1}: ${t.question}</h4>
                    
                    <div class="grid-data">
                        <div class="info-box">
                            <strong>Candidate Answer:</strong>
                            <p style="margin-top:0.5rem; color:var(--text-muted);">${t.answer}</p>
                        </div>
                        <div class="info-box" style="border-left-color: var(--success);">
                            <strong>Ideal Answer / Concept:</strong>
                            <p style="margin-top:0.5rem; color:var(--text-muted);">${t.ideal_answer}</p>
                        </div>
                    </div>
                    
                    <div style="display:flex; gap: 2rem; margin-top: 1.5rem; font-size: 0.9rem;">
                        <div><strong style="color:var(--success);">Strengths:</strong> ${t.strengths}</div>
                        <div><strong style="color:var(--warning);">Weaknesses:</strong> ${t.weaknesses}</div>
                        <div><strong style="color:var(--primary);">Suggestions:</strong> ${t.suggestions}</div>
                    </div>
                    
                    <div style="margin-top: 1rem;">
                        <strong>Scores:</strong> Tech: ${t.technical_score}% | Comm: ${t.communication_score}%
                    </div>
                </div>
            `;
        });
        reportContent.innerHTML = html;
    }
});