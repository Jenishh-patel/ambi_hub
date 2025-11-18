/**
 * Celebration animations for achievements, level ups, and milestones
 */

// Show celebration animation
function showCelebration(type, data) {
    const celebration = document.createElement('div');
    celebration.className = 'celebration';
    celebration.id = `celebration-${Date.now()}`;
    
    let content = '';
    let icon = '🎉';
    
    switch (type) {
        case 'level_up':
            icon = '⭐';
            content = `
                <div class="celebration-content">
                    <div class="celebration-icon">${icon}</div>
                    <h2>Level Up!</h2>
                    <p>You've reached Level ${data}!</p>
                </div>
            `;
            break;
            
        case 'badge':
            icon = data.icon || '🏅';
            content = `
                <div class="celebration-content">
                    <div class="celebration-icon">${icon}</div>
                    <h2>Badge Earned!</h2>
                    <p>${data.name}</p>
                    <p class="celebration-rarity rarity-${data.rarity}">${data.rarity}</p>
                </div>
            `;
            break;
            
        case 'milestone':
            icon = '🎖️';
            content = `
                <div class="celebration-content">
                    <div class="celebration-icon">${icon}</div>
                    <h2>Milestone Achieved!</h2>
                    <p>${data.message || data.name}</p>
                </div>
            `;
            break;
            
        default:
            icon = '🎉';
            content = `
                <div class="celebration-content">
                    <div class="celebration-icon">${icon}</div>
                    <h2>Congratulations!</h2>
                    <p>Keep up the great work!</p>
                </div>
            `;
    }
    
    celebration.innerHTML = content;
    document.body.appendChild(celebration);
    
    // Trigger animation
    setTimeout(() => {
        celebration.classList.add('show');
    }, 10);
    
    // Remove after animation
    setTimeout(() => {
        celebration.classList.remove('show');
        setTimeout(() => {
            celebration.remove();
        }, 500);
    }, 3000);
}

// Confetti effect (simple version)
function createConfetti() {
    const colors = ['#00d4ff', '#10b981', '#3b82f6', '#8b5cf6', '#f59e0b'];
    const confettiCount = 50;
    
    for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.left = Math.random() * 100 + '%';
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.animationDelay = Math.random() * 0.5 + 's';
        confetti.style.animationDuration = (Math.random() * 2 + 2) + 's';
        document.body.appendChild(confetti);
        
        setTimeout(() => {
            confetti.remove();
        }, 4000);
    }
}

// Add celebration styles if not already present
if (!document.getElementById('celebration-styles')) {
    const style = document.createElement('style');
    style.id = 'celebration-styles';
    style.textContent = `
        .celebration {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0);
            z-index: 10000;
            background: var(--card-bg);
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            text-align: center;
            transition: transform 0.5s ease;
            pointer-events: none;
        }
        
        .celebration.show {
            transform: translate(-50%, -50%) scale(1);
        }
        
        .celebration-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
            animation: bounce 0.5s ease infinite;
        }
        
        .celebration-content h2 {
            margin-bottom: 0.5rem;
            color: var(--primary);
        }
        
        .confetti {
            position: fixed;
            width: 10px;
            height: 10px;
            top: -10px;
            animation: confetti-fall linear forwards;
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }
        
        @keyframes confetti-fall {
            to {
                transform: translateY(100vh) rotate(360deg);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// Export for use in other scripts
if (typeof window !== 'undefined') {
    window.showCelebration = showCelebration;
    window.createConfetti = createConfetti;
}

