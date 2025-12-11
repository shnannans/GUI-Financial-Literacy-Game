# Financial Friend Quiz Game 🎉💰

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange)
![Pygame](https://img.shields.io/badge/Audio-Pygame-green)
![Status](https://img.shields.io/badge/Status-Completed-success)

## 📋 Project Overview

Interactive financial literacy quiz game built with Python Tkinter, designed to teach money management concepts through gamified learning. Players earn virtual currency, customize avatars, and compete on leaderboards while mastering financial planning skills across 4 difficulty levels.

**Course**: INF1002 Programming Fundamentals  
**Institution**: Singapore Institute of Technology  
**Team**: P14-2  
**Semester**: 2024

---

## 🎮 Game Features

### Core Gameplay
- **4 Difficulty Levels**: Rookie Earners → Savings Strikers → Wealth Champions → All-Star Challenge
- **10 Questions per Quiz**: Time-limited questions (30s each) with scoring based on response speed
- **Dynamic Scoring**: Points formula: `(1 - (response_time / total_time) / 2) × 1000`
- **Random Events**: Surprise scenarios that affect player money mid-quiz
- **Streak Bonuses**: Earn extra $10 for 3+ consecutive correct answers

### Player Progression
- 💰 **Virtual Economy**: Start with $10, earn through correct answers, spend in shop
- 👤 **Character Customization**: Purchase and equip Hats, Outfits, Accessories, Shoes (25 items total)
- 🏆 **Leaderboard System**: Global rankings with top 10 players displayed
- 📊 **Progress Tracking**: View highest scores per difficulty, spending overview, purchase history

### Quality of Life
- ⚙️ **Audio Settings**: Adjustable music/SFX volume, mute options
- 💡 **Hint System**: Eliminate one wrong answer (costs nothing, once per question)
- 🎯 **Game Points**: Separate scoring system tracking quiz performance
- 📈 **Spending Visualization**: Pie charts showing earnings vs. losses

---

## 🛠️ Tech Stack

**GUI Framework**:
- `tkinter` - Main interface and widget management
- `ttk` - Themed widgets (progress bars, treeviews)

**Game Logic & Data**:
- `pygame.mixer` - Background music and sound effects
- `csv` - Quiz questions and random events storage
- `json` - Centralized user data persistence
- `matplotlib` - Spending overview pie charts

**Python Standard Library**:
- `random` - Question shuffling, event selection
- `datetime` - Timestamp tracking for leaderboard
- `os` - File path management

---

## 📁 Project Structure
```
financial-friend-quiz/
├── codes_script.ipynb                          # Main game logic (converted to .py for deployment)
│
├── audio_files/
│   ├── background_music.mp3                    # Upbeat loop music
│   ├── correct.wav                             # Correct answer sound
│   ├── wrong.wav                               # Incorrect answer sound
│   ├── button_click.mp3                        # UI button clicks
│   ├── radio_button_click.mp3                  # Option selection
│   ├── quiz_thinktime.mp3                      # Timer background ambience
│   ├── random_accept.wav                       # Event acceptance
│   └── random_decline.mp3                      # Event rejection
│
├── in_game_files/
│   ├── quiz_data.csv                           # 40+ questions across 4 difficulties
│   └── random_scenario.csv                     # 20+ random financial events
│
├── user_&leaderboard_files/
│   ├── quiz_user_data.json                     # Centralized player profiles
│   └── leaderboard.csv                         # Global rankings
│
├── prohibited_words.txt                        # Username filter list
└── README.md                                   # This file
```

---

## 🎯 Gameplay Mechanics

### Scoring System

**Money System** (💰):
- Start: $10
- Correct Answer: +$10
- Wrong Answer: -$5
- Timeout: -$5
- 3+ Streak Bonus: +$10

**Game Points System** (🎯):
- Speed-based scoring: Faster answers = more points
- Formula: `points = (1 - (time_taken / 30) / 2) × 1000`
- Example: 10s answer = 833 points, 20s answer = 666 points
- High scores tracked per difficulty level

### Difficulty Levels

| Level | Internal Name | Questions | Target Audience |
|-------|---------------|-----------|-----------------|
| 🟢 Rookie Earners | Beginner | 10 | Basic budgeting concepts |
| 🟡 Savings Strikers | Intermediate | 10 | Saving strategies, debt management |
| 🟠 Wealth Champions | Advanced | 10 | Investing, retirement planning |
| 🔴 All-Star Challenge | Master | 10 (random from all) | Mixed difficulty marathon |

### Random Events
- **Trigger Rate**: 30% chance after each question
- **Types**: Job offers, unexpected expenses, investment opportunities
- **Impact**: +/- $5 to $50 depending on choice
- **Examples**:
  - "Accept a freelance gig for $20?" (Accept/Decline)
  - "Your car breaks down! Pay $30 for repairs?" (Yes/No)

---

## 🛒 Shop System

### Item Categories & Prices

**Hats** (🎩):
- Fancy Hat - $20
- Sun Visor - $15
- Wizard's Hat - $40
- Stealth Hood - $35
- Battle Helm - $50

**Outfits** (👔):
- Invisibility Cloak - $60
- Warrior Armor - $80
- Ranger Outfit - $45
- Sorcerer's Robe - $70
- Shadow Suit - $55

**Accessories** (💍):
- Lucky Bracelet - $15
- Strength Amulet - $30
- Mystic Pendant - $40
- Protection Ring - $35
- Speed Band - $25

**Shoes** (👟):
- Golden Shoes - $50
- Winged Boots - $70
- Steel Greaves - $60
- Silent Sneakers - $40
- Flamewalkers - $80

---

## 💻 Installation & Setup

### Prerequisites
```bash
pip install pygame matplotlib
```
Note: `tkinter` is included with Python on most systems.

### Running the Game
```bash
python codes_script.py
```

Or run the Jupyter Notebook:
```bash
jupyter notebook codes_script.ipynb
# Execute all cells
```

---

## 🎮 How to Play

1. **Enter Username**: 3-20 characters, no profanity
2. **Select Difficulty**: Choose your financial knowledge level
3. **Answer Questions**: 
   - Select answer from 4 options
   - Use 💡 Hint to eliminate one wrong answer
   - Submit before 30s timer expires
4. **Handle Random Events**: Accept/decline financial scenarios
5. **View Results**: Check earnings, game points, spending breakdown
6. **Customize Character**: Spend money in shop on cosmetic items
7. **Compete**: Check leaderboard ranking

---

## 📊 Data Persistence

### User Profile (`quiz_user_data.json`)
```json
{
  "PlayerName": {
    "inventory": ["Fancy Hat 🎩", "Golden Shoes 👟"],
    "equipped_items": {
      "hat": "Fancy Hat 🎩",
      "outfit": null,
      "accessory": null,
      "shoes": "Golden Shoes 👟"
    },
    "money": 45,
    "game_points": 7850,
    "last_played": "11/12/2024 14:30",
    "highest_game_points": {
      "Beginner": 8200,
      "Intermediate": 7850
    }
  }
}
```

### Leaderboard (`leaderboard.csv`)
- Columns: Datetime Captured, Username, Game Points, Difficulty Level, Current Rank
- Sorted by Game Points (descending)
- Top 10 displayed in-game

---

## 🎵 Audio Credits

| Sound | Author | License |
|-------|--------|---------|
| Background Music | yummie | CC BY 4.0 |
| Correct Answer | StavSounds | CC0 |
| Wrong Answer | Beetlemuse | CC BY 4.0 |
| UI Sounds | lucadialessandro, Universefield | Pixabay Content Licensed |
| Quiz Think Time | N/A | Pixabay Content Licensed |

All audio sourced from Freesound.org and Pixabay.

---

## 🏆 Key Features Implemented

✅ **Multi-User Support**: Separate profiles with persistent data  
✅ **Hint System**: Strategic gameplay element (1 per question)  
✅ **Timer Visuals**: Progress bar + countdown for urgency  
✅ **Responsive UI**: Scrollable content for all screen sizes  
✅ **Username Validation**: Profanity filter + character limits  
✅ **High Score Tracking**: Per-difficulty leaderboards  
✅ **Audio Controls**: Master volume, music/SFX toggles  
✅ **Spending Analytics**: Matplotlib pie chart visualization  
✅ **Shop System**: 25 purchasable items with equip/unequip  
✅ **Profile Management**: View stats, delete account option  

---

## 🚀 Future Enhancements

- [ ] Multiplayer mode (head-to-head quiz battles)
- [ ] Daily challenges with bonus rewards
- [ ] Achievement system with badges
- [ ] Difficulty-based question pools (100+ questions per level)
- [ ] Mobile app version (Kivy/BeeWare port)
- [ ] Cloud save sync (Firebase integration)
- [ ] In-game currency doubler power-ups
- [ ] Animated character sprites
- [ ] Social sharing (share scores to Twitter/Discord)

---

## 📚 Learning Outcomes

- ✅ **Data Structures**: Dictionaries, lists for inventory/leaderboard management
- ✅ **File Handling**: CSV parsing, JSON serialization
- ✅ **Event-Driven Programming**: Tkinter event loops, button callbacks
- ✅ **Audio Programming**: Pygame mixer for sound effects
- ✅ **Algorithm Design**: Timer logic, scoring formulas, randomization
- ✅ **User Experience**: Settings persistence, intuitive navigation

---

*Developed with 🎮 at Singapore Institute of Technology | 2024*