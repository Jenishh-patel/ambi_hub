/**
 * Workout module JavaScript for Ambitious Hub
 */

let workoutCharts = {};
let currentSets = [];
let modalSets = [];

// Tab switching
function showTab(tabName, eventElement) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
        tab.classList.remove('active');
    });
    
    if (eventElement) {
        eventElement.classList.add('active');
    } else if (event && event.target) {
        event.target.classList.add('active');
    }
    
    const tab = document.getElementById(`${tabName}-tab`);
    if (tab) {
        tab.style.display = 'block';
        tab.classList.add('active');
    }
    
    if (tabName === 'analytics') {
        loadAnalytics();
    }
}

// Exercise Library
async function loadExercises() {
    try {
        const response = await fetch('/api/workout/exercises/');
        const data = await response.json();
        
        const exercisesGrid = document.getElementById('exercises-grid');
        exercisesGrid.innerHTML = '';
        
        if (data.exercises.length === 0) {
            exercisesGrid.innerHTML = '<p class="empty-state">No exercises found. Add your first exercise!</p>';
            return;
        }
        
        // Group by category
        const byCategory = {};
        data.exercises.forEach(ex => {
            if (!byCategory[ex.category]) {
                byCategory[ex.category] = [];
            }
            byCategory[ex.category].push(ex);
        });
        
        Object.keys(byCategory).forEach(category => {
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'exercise-category';
            categoryDiv.innerHTML = `<h3>${category.charAt(0).toUpperCase() + category.slice(1)}</h3>`;
            
            const exercisesList = document.createElement('div');
            exercisesList.className = 'exercises-list';
            
            byCategory[category].forEach(ex => {
                const exCard = document.createElement('div');
                exCard.className = 'exercise-card';
                exCard.innerHTML = `
                    <div class="exercise-name">${ex.name}</div>
                    ${!ex.is_default ? `
                        <button class="btn btn-danger btn-sm" onclick="deleteExercise(${ex.id})">Delete</button>
                    ` : ''}
                `;
                exercisesList.appendChild(exCard);
            });
            
            categoryDiv.appendChild(exercisesList);
            exercisesGrid.appendChild(categoryDiv);
        });
        
        // Populate exercise select for analytics
        const analyticsSelect = document.getElementById('analytics-exercise');
        analyticsSelect.innerHTML = '<option value="">All Exercises</option>';
        data.exercises.forEach(ex => {
            const option = document.createElement('option');
            option.value = ex.name;
            option.textContent = ex.name;
            analyticsSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading exercises:', error);
    }
}

function filterExercises() {
    const category = document.getElementById('category-filter').value;
    const cards = document.querySelectorAll('.exercise-category');
    
    cards.forEach(card => {
        if (!category || card.querySelector('h3').textContent.toLowerCase() === category) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

function showAddExerciseModal() {
    document.getElementById('add-exercise-modal').style.display = 'block';
}

function closeAddExerciseModal() {
    document.getElementById('add-exercise-modal').style.display = 'none';
    document.getElementById('add-exercise-form').reset();
}

async function addExercise(event) {
    event.preventDefault();
    
    const exerciseData = {
        name: document.getElementById('exercise-name').value,
        category: document.getElementById('exercise-category').value,
    };
    
    try {
        const response = await fetch('/api/workout/exercises/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(exerciseData),
        });
        
        if (response.ok) {
            closeAddExerciseModal();
            loadExercises();
        } else {
            alert('Error creating exercise');
        }
    } catch (error) {
        console.error('Error adding exercise:', error);
        alert('Error creating exercise');
    }
}

async function deleteExercise(exerciseId) {
    if (!confirm('Are you sure you want to delete this exercise?')) return;
    
    try {
        const response = await fetch(`/api/workout/exercises/${exerciseId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        });
        
        if (response.ok) {
            loadExercises();
        }
    } catch (error) {
        console.error('Error deleting exercise:', error);
    }
}

// Workout Session Logging - New Category-Based Flow
let selectedCategory = null;
let selectedExerciseId = null;
let workoutSetsCount = 1;

function loadCategoryExercises() {
    const category = document.getElementById('workout-category').value;
    if (!category) {
        document.getElementById('step-2').style.display = 'none';
        document.getElementById('step-3').style.display = 'none';
        document.getElementById('step-4').style.display = 'none';
        return;
    }
    
    selectedCategory = category;
    
    // Load exercises for this category
    fetch('/api/workout/exercises/')
        .then(response => response.json())
        .then(data => {
            const exerciseSelect = document.getElementById('workout-exercise');
            exerciseSelect.innerHTML = '<option value="">Select Exercise</option>';
            
            const categoryExercises = data.exercises.filter(ex => ex.category === category);
            categoryExercises.forEach(ex => {
                const option = document.createElement('option');
                option.value = ex.id;
                option.textContent = ex.name;
                exerciseSelect.appendChild(option);
            });
            
            document.getElementById('step-2').style.display = 'block';
        });
}

function showSetInputs() {
    const exerciseId = document.getElementById('workout-exercise').value;
    if (!exerciseId) {
        document.getElementById('step-3').style.display = 'none';
        document.getElementById('step-4').style.display = 'none';
        return;
    }
    
    selectedExerciseId = parseInt(exerciseId);
    document.getElementById('step-3').style.display = 'block';
}

function generateSetRows() {
    const setsCount = parseInt(document.getElementById('workout-sets-count').value) || 1;
    workoutSetsCount = setsCount;
    
    const setsList = document.getElementById('workout-sets-list');
    setsList.innerHTML = '';
    
    for (let i = 1; i <= setsCount; i++) {
        const setRow = document.createElement('div');
        setRow.className = 'set-row';
        setRow.innerHTML = `
            <label>Set ${i}</label>
            <input type="number" class="set-reps" placeholder="Reps" min="1" id="set-${i}-reps" required>
            <input type="number" class="set-weight" placeholder="Weight (kg)" step="0.5" min="0" id="set-${i}-weight" required>
            <input type="number" class="set-rpe" placeholder="RPE (1-10)" min="1" max="10" id="set-${i}-rpe">
        `;
        setsList.appendChild(setRow);
    }
    
    document.getElementById('step-4').style.display = 'block';
    document.getElementById('save-workout-btn').style.display = 'block';
}

function showLogSessionModal() {
    document.getElementById('log-session-modal').style.display = 'block';
    modalSets = [];
    updateModalSetsList();
}

function closeLogSessionModal() {
    document.getElementById('log-session-modal').style.display = 'none';
    modalSets = [];
    updateModalSetsList();
}

function addModalSetRow() {
    modalSets.push({
        exercise_id: null,
        reps: 0,
        weight: 0,
        rpe: null,
        set_number: modalSets.length + 1
    });
    updateModalSetsList();
}

async function updateSetsList() {
    const setsList = document.getElementById('sets-list');
    setsList.innerHTML = '';
    
    // Load exercises for dropdown
    const exercisesResponse = await fetch('/api/workout/exercises/');
    const exercisesData = await exercisesResponse.json();
    
    currentSets.forEach((set, index) => {
        const setRow = document.createElement('div');
        setRow.className = 'set-row';
        setRow.innerHTML = `
            <select class="set-exercise" onchange="updateSet(${index}, 'exercise_id', this.value)">
                <option value="">Select Exercise</option>
                ${exercisesData.exercises.map(ex => 
                    `<option value="${ex.id}" ${set.exercise_id == ex.id ? 'selected' : ''}>${ex.name}</option>`
                ).join('')}
            </select>
            <input type="number" class="set-reps" placeholder="Reps" value="${set.reps}" 
                   onchange="updateSet(${index}, 'reps', this.value)" min="1">
            <input type="number" class="set-weight" placeholder="Weight (kg)" value="${set.weight}" 
                   step="0.5" onchange="updateSet(${index}, 'weight', this.value)" min="0">
            <input type="number" class="set-rpe" placeholder="RPE (1-10)" value="${set.rpe || ''}" 
                   onchange="updateSet(${index}, 'rpe', this.value)" min="1" max="10">
            <button class="btn btn-danger btn-sm" onclick="removeSet(${index})">Remove</button>
        `;
        setsList.appendChild(setRow);
    });
}

async function updateModalSetsList() {
    const setsList = document.getElementById('modal-sets-list');
    setsList.innerHTML = '';
    
    // Load exercises for dropdown
    const exercisesResponse = await fetch('/api/workout/exercises/');
    const exercisesData = await exercisesResponse.json();
    
    modalSets.forEach((set, index) => {
        const setRow = document.createElement('div');
        setRow.className = 'set-row';
        setRow.innerHTML = `
            <select class="set-exercise" onchange="updateModalSet(${index}, 'exercise_id', this.value)">
                <option value="">Select Exercise</option>
                ${exercisesData.exercises.map(ex => 
                    `<option value="${ex.id}" ${set.exercise_id == ex.id ? 'selected' : ''}>${ex.name}</option>`
                ).join('')}
            </select>
            <input type="number" class="set-reps" placeholder="Reps" value="${set.reps}" 
                   onchange="updateModalSet(${index}, 'reps', this.value)" min="1">
            <input type="number" class="set-weight" placeholder="Weight (kg)" value="${set.weight}" 
                   step="0.5" onchange="updateModalSet(${index}, 'weight', this.value)" min="0">
            <input type="number" class="set-rpe" placeholder="RPE (1-10)" value="${set.rpe || ''}" 
                   onchange="updateModalSet(${index}, 'rpe', this.value)" min="1" max="10">
            <button class="btn btn-danger btn-sm" onclick="removeModalSet(${index})">Remove</button>
        `;
        setsList.appendChild(setRow);
    });
}

function updateSet(index, field, value) {
    if (field === 'exercise_id') {
        currentSets[index].exercise_id = parseInt(value);
    } else if (field === 'reps') {
        currentSets[index].reps = parseInt(value);
    } else if (field === 'weight') {
        currentSets[index].weight = parseFloat(value);
    } else if (field === 'rpe') {
        currentSets[index].rpe = value ? parseInt(value) : null;
    }
}

function updateModalSet(index, field, value) {
    if (field === 'exercise_id') {
        modalSets[index].exercise_id = parseInt(value);
    } else if (field === 'reps') {
        modalSets[index].reps = parseInt(value);
    } else if (field === 'weight') {
        modalSets[index].weight = parseFloat(value);
    } else if (field === 'rpe') {
        modalSets[index].rpe = value ? parseInt(value) : null;
    }
}

function removeSet(index) {
    currentSets.splice(index, 1);
    currentSets.forEach((set, idx) => set.set_number = idx + 1);
    updateSetsList();
}

function removeModalSet(index) {
    modalSets.splice(index, 1);
    modalSets.forEach((set, idx) => set.set_number = idx + 1);
    updateModalSetsList();
}

async function saveWorkoutSession() {
    const date = document.getElementById('session-date').value;
    const notes = document.getElementById('session-notes').value;
    
    if (!selectedExerciseId) {
        alert('Please select an exercise');
        return;
    }
    
    // Collect sets data
    const sets = [];
    for (let i = 1; i <= workoutSetsCount; i++) {
        const reps = document.getElementById(`set-${i}-reps`)?.value;
        const weight = document.getElementById(`set-${i}-weight`)?.value;
        const rpe = document.getElementById(`set-${i}-rpe`)?.value;
        
        if (reps && weight) {
            sets.push({
                exercise_id: selectedExerciseId,
                reps: parseInt(reps),
                weight: parseFloat(weight),
                rpe: rpe ? parseInt(rpe) : null,
                set_number: i
            });
        }
    }
    
    if (sets.length === 0) {
        alert('Please add at least one valid set');
        return;
    }
    
    const sessionData = {
        date: date,
        notes: notes,
        sets: sets
    };
    
    try {
        const response = await fetch('/api/workout/log-session/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(sessionData),
        });
        
        if (response.ok) {
            const data = await response.json();
            alert(`Workout saved! Total volume: ${data.session.total_volume.toFixed(2)} kg`);
            
            // Reset form
            document.getElementById('workout-category').value = '';
            document.getElementById('workout-exercise').value = '';
            document.getElementById('workout-sets-count').value = '1';
            document.getElementById('session-notes').value = '';
            document.getElementById('workout-sets-list').innerHTML = '';
            document.getElementById('step-2').style.display = 'none';
            document.getElementById('step-3').style.display = 'none';
            document.getElementById('step-4').style.display = 'none';
            document.getElementById('save-workout-btn').style.display = 'none';
            selectedCategory = null;
            selectedExerciseId = null;
            
            loadAnalytics();
            loadPersonalRecords();
        } else {
            alert('Error saving workout');
        }
    } catch (error) {
        console.error('Error saving workout:', error);
        alert('Error saving workout');
    }
}

async function saveModalWorkoutSession() {
    const date = document.getElementById('modal-session-date').value;
    const notes = document.getElementById('modal-session-notes').value;
    
    const validSets = modalSets.filter(s => s.exercise_id && s.reps > 0 && s.weight > 0);
    
    if (validSets.length === 0) {
        alert('Please add at least one valid set');
        return;
    }
    
    const sessionData = {
        date: date,
        notes: notes,
        sets: validSets
    };
    
    try {
        const response = await fetch('/api/workout/log-session/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(sessionData),
        });
        
        if (response.ok) {
            const data = await response.json();
            alert(`Workout saved! Total volume: ${data.session.total_volume.toFixed(2)} kg`);
            closeLogSessionModal();
            loadAnalytics();
            loadPersonalRecords();
        } else {
            alert('Error saving workout');
        }
    } catch (error) {
        console.error('Error saving workout:', error);
        alert('Error saving workout');
    }
}

// Analytics
async function loadAnalytics() {
    const days = document.getElementById('analytics-days')?.value || 30;
    const exerciseFilter = document.getElementById('analytics-exercise')?.value || '';
    
    try {
        const response = await fetch(`/api/workout/analytics/?days=${days}`);
        const data = await response.json();
        
        // Weight Progression Chart
        renderWeightProgressionChart(data.weight_progression, exerciseFilter);
        
        // Volume Progression Chart
        renderVolumeProgressionChart(data.volume_progression, exerciseFilter);
        
        // Weekly Load Chart
        renderWeeklyLoadChart(data.weekly_load);
        
        // Heatmap Chart
        renderHeatmapChart(data.heatmap_data);
        
        // Weekly Summary
        updateWeeklySummary(data);
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

function renderWeightProgressionChart(weightData, exerciseFilter) {
    const ctx = document.getElementById('weight-chart');
    if (!ctx) return;
    
    if (workoutCharts.weight) {
        workoutCharts.weight.destroy();
    }
    
    const datasets = [];
    Object.keys(weightData).forEach(exercise => {
        if (exerciseFilter && exercise !== exerciseFilter) return;
        
        const dates = Object.keys(weightData[exercise]).sort();
        const weights = dates.map(date => weightData[exercise][date]);
        
        datasets.push({
            label: exercise,
            data: weights,
            borderColor: getRandomColor(),
            tension: 0.4,
            fill: false
        });
    });
    
    workoutCharts.weight = new Chart(ctx, {
        type: 'line',
        data: {
            labels: getUniqueDates(weightData),
            datasets: datasets
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: true }
            },
            scales: {
                y: { beginAtZero: true, title: { display: true, text: 'Weight (kg)' } }
            }
        }
    });
}

function renderVolumeProgressionChart(volumeData, exerciseFilter) {
    const ctx = document.getElementById('volume-chart');
    if (!ctx) return;
    
    if (workoutCharts.volume) {
        workoutCharts.volume.destroy();
    }
    
    const datasets = [];
    Object.keys(volumeData).forEach(exercise => {
        if (exerciseFilter && exercise !== exerciseFilter) return;
        
        const dates = Object.keys(volumeData[exercise]).sort();
        const volumes = dates.map(date => volumeData[exercise][date]);
        
        datasets.push({
            label: exercise,
            data: volumes,
            backgroundColor: getRandomColor(),
        });
    });
    
    workoutCharts.volume = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: getUniqueDates(volumeData),
            datasets: datasets
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: true }
            },
            scales: {
                y: { beginAtZero: true, title: { display: true, text: 'Volume (kg)' } }
            }
        }
    });
}

function renderWeeklyLoadChart(weeklyLoad) {
    const ctx = document.getElementById('weekly-load-chart');
    if (!ctx) return;
    
    if (workoutCharts.weeklyLoad) {
        workoutCharts.weeklyLoad.destroy();
    }
    
    const weeks = Object.keys(weeklyLoad).sort();
    const volumes = weeks.map(week => weeklyLoad[week]);
    
    workoutCharts.weeklyLoad = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: weeks,
            datasets: [{
                label: 'Weekly Volume (kg)',
                data: volumes,
                backgroundColor: '#3B82F6',
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true, title: { display: true, text: 'Volume (kg)' } }
            }
        }
    });
}

function renderHeatmapChart(heatmapData) {
    const ctx = document.getElementById('heatmap-chart');
    if (!ctx) return;
    
    if (workoutCharts.heatmap) {
        workoutCharts.heatmap.destroy();
    }
    
    const dates = Object.keys(heatmapData).sort();
    const frequencies = dates.map(date => heatmapData[date]);
    
    workoutCharts.heatmap = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: dates,
            datasets: [{
                label: 'Training Days',
                data: frequencies,
                backgroundColor: frequencies.map(f => f > 0 ? '#10B981' : '#E5E7EB'),
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true, title: { display: true, text: 'Sessions' } }
            }
        }
    });
}

function getUniqueDates(data) {
    const allDates = new Set();
    Object.values(data).forEach(exerciseData => {
        Object.keys(exerciseData).forEach(date => allDates.add(date));
    });
    return Array.from(allDates).sort();
}

function getRandomColor() {
    const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'];
    return colors[Math.floor(Math.random() * colors.length)];
}

function updateWeeklySummary(data) {
    const summaryContent = document.getElementById('weekly-summary-content');
    if (!summaryContent) return;
    
    // Calculate weekly totals
    const weeklyTotals = {};
    Object.keys(data.weekly_load).forEach(week => {
        weeklyTotals[week] = data.weekly_load[week];
    });
    
    const latestWeek = Object.keys(weeklyTotals).sort().pop();
    const totalVolume = latestWeek ? weeklyTotals[latestWeek] : 0;
    
    // Find strongest lift
    const strongestPR = data.personal_records.reduce((max, pr) => 
        pr.max_weight > (max?.max_weight || 0) ? pr : max, null
    );
    
    summaryContent.innerHTML = `
        <div class="summary-card">
            <h4>Total Volume (Latest Week)</h4>
            <p class="summary-value">${totalVolume.toFixed(2)} kg</p>
        </div>
        <div class="summary-card">
            <h4>Strongest Lift</h4>
            <p class="summary-value">${strongestPR ? `${strongestPR.exercise}: ${strongestPR.max_weight} kg` : 'N/A'}</p>
        </div>
        <div class="summary-card">
            <h4>Personal Records</h4>
            <p class="summary-value">${data.personal_records.length}</p>
        </div>
    `;
}

// Personal Records
async function loadPersonalRecords() {
    try {
        const response = await fetch('/api/workout/personal-records/');
        const data = await response.json();
        
        const prList = document.getElementById('pr-list');
        prList.innerHTML = '';
        
        if (data.personal_records.length === 0) {
            prList.innerHTML = '<p class="empty-state">No personal records yet. Start logging workouts!</p>';
            return;
        }
        
        data.personal_records.forEach(pr => {
            const prCard = document.createElement('div');
            prCard.className = 'pr-card';
            prCard.innerHTML = `
                <div class="pr-exercise">${pr.exercise.name}</div>
                <div class="pr-weight">${pr.max_weight} kg</div>
                <div class="pr-date">Achieved: ${new Date(pr.date_achieved).toLocaleDateString()}</div>
            `;
            prList.appendChild(prCard);
        });
    } catch (error) {
        console.error('Error loading personal records:', error);
    }
}

// Export Report
async function exportMonthlyReport() {
    const today = new Date();
    const month = today.getMonth() + 1;
    const year = today.getFullYear();
    
    try {
        const response = await fetch(`/api/workout/export-report/?month=${month}&year=${year}`);
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `workout_report_${year}_${month.toString().padStart(2, '0')}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            alert('Error exporting report');
        }
    } catch (error) {
        console.error('Error exporting report:', error);
        alert('Error exporting report');
    }
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

