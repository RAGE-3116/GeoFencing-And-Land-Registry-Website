# 🏠 Digital Land Registry & Geofencing Web Application

A modern, full-stack web application for managing land ownership with polygon-based geofencing, real-time auctions, and cloud backups.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-lightblue.svg)](https://www.sqlite.org/)
[![Cloudinary](https://img.shields.io/badge/Cloud-Cloudinary-orange.svg)](https://cloudinary.com/)

---

## 📸 Features

### Core Functionality
- 🗺️ **Interactive Geofencing** - Define property boundaries with polygon coordinates
- 👤 **Owner Name Labels** - Hovering owner names on map properties
- 🔍 **Username Search** - Filter properties by owner
- ✅ **Property Verification** - Secure verification with hidden admin mode
- 🔨 **Live Auctions** - Real-time bidding with countdown timers
- 🏆 **Automatic Transfer** - Property ownership transfers to auction winners
- ☁️ **Cloud Backup** - Automatic Cloudinary backups

### Technical Highlights
- ⚡ **Fast Performance** - SQLite for instant local operations
- 🛡️ **Data Integrity** - ACID transactions prevent corruption
- 📱 **Mobile Responsive** - Works on all devices
- 🌐 **Production Ready** - Deploy to Render in minutes
- 🔐 **Secure** - Environment-based configuration

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip (Python package manager)
- Git

### Installation

```bash
# 1. Clone/Download the repository
cd land-registry-app

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python app.py
```

### Access the App
Open your browser: **http://localhost:5000**

✅ That's it! The app is running!

---

## 📁 Project Structure

```
land-registry-app/
│
├── app.py                    # Flask backend (SQLite + Cloudinary)
├── requirements.txt          # Python dependencies
├── runtime.txt              # Python version (for Render)
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
│
├── static/                  # Frontend files
│   ├── index.html           # Landing page
│   ├── login.html           # Authentication
│   ├── map.html             # Interactive map
│   ├── profile.html         # User dashboard
│   ├── auctions.html        # Auction system
│   ├── verify.html          # Verification page
│   ├── about.html           # About page
│   └── css/
│       └── style.css        # Styles
│
└── docs/                    # Detailed guides
    ├── EXECUTION_GUIDE.md   # Complete execution steps
    ├── SETUP_CLOUDINARY.md  # Cloudinary configuration
    └── SETUP_RENDER.md      # Deployment guide
```

---

## 📚 Documentation

| Guide | Description | Time |
|-------|-------------|------|
| **[EXECUTION_GUIDE.md](EXECUTION_GUIDE.md)** | Complete setup and testing | 15 min |
| **[SETUP_CLOUDINARY.md](SETUP_CLOUDINARY.md)** | Cloud backup configuration | 5 min |
| **[SETUP_RENDER.md](SETUP_RENDER.md)** | Deploy to the internet | 10 min |

---

## 🎯 Usage

### 1. Create Account
- Navigate to Login page
- Click "Sign Up"
- Enter username and password

### 2. Add Property
- Go to Profile page
- Enter property name
- Add coordinates in JSON format:
  ```json
  [[28.5355, 77.3910], [28.5365, 77.3910], [28.5365, 77.3920], [28.5355, 77.3920]]
  ```

### 3. Verify Property
- Go to Verify page
- Type `iamadmin` anywhere on page
- Click "Verify" button on property

### 4. View on Map
- Navigate to Map page
- See property with owner name hovering
- Click polygon for details
- Use search to filter by username

### 5. Create Auction
- Profile → "Create Auction" on verified property
- Set starting bid, duration, description
- Click "Create Auction"

### 6. Place Bids
- Go to Auctions page
- See live countdown timer
- Click "Place Bid"
- Enter amount higher than current bid

### 7. Property Transfer
- When auction ends, highest bidder wins
- Property ownership transfers automatically
- Map updates with new owner name

---

## 🛠️ Technology Stack

### Frontend
- HTML5, CSS3, JavaScript (Vanilla)
- Bootstrap 5 (UI Components)
- Leaflet.js (Interactive Maps)

### Backend
- Python 3.11
- Flask 3.0 (Web Framework)
- SQLite (Database)
- Gunicorn (Production Server)

### Cloud Services
- Cloudinary (Backup & Media Storage)
- Render (Deployment Platform)

---

## ☁️ Optional: Cloudinary Setup

Cloudinary provides automatic cloud backups.

### Quick Setup

1. Create free account: https://cloudinary.com/users/register/free
2. Get credentials from dashboard
3. Create `.env` file from `.env.example`
4. Add your credentials
5. Restart server

**Detailed guide:** See [SETUP_CLOUDINARY.md](SETUP_CLOUDINARY.md)

**Without Cloudinary:** App works perfectly - data saved to SQLite locally.

---

## 🌐 Deployment to Render

Make your app accessible on the internet!

### Quick Deploy

1. Push code to GitHub
2. Create Render account: https://render.com
3. Connect GitHub repository
4. Add environment variables
5. Deploy!

**Your URL:** `https://your-app-name.onrender.com`

**Detailed guide:** See [SETUP_RENDER.md](SETUP_RENDER.md)

---

## 🗄️ Database Schema

### Tables

**users**
- id (PRIMARY KEY)
- username (UNIQUE)
- password
- created_at

**properties**
- id (PRIMARY KEY)
- owner (FOREIGN KEY → users)
- property_name
- coords (JSON)
- verified (0/1)
- cloudinary_url
- created_at

**auctions**
- id (PRIMARY KEY)
- property_id (FOREIGN KEY → properties)
- property_name
- owner
- starting_bid, current_bid
- description
- start_time, end_time
- status (active/ended)
- winner
- cloudinary_backup_url

**bids**
- id (PRIMARY KEY)
- auction_id (FOREIGN KEY → auctions)
- bidder
- amount
- timestamp

---

## 🎓 For College Project

### Features to Highlight

1. **Modern Architecture**
   - Hybrid SQLite + Cloud storage
   - RESTful API design
   - Real-time updates

2. **Advanced Features**
   - Live countdown timers
   - Automatic property transfer
   - Geospatial visualization
   - Username-based filtering

3. **Professional Practices**
   - Environment-based configuration
   - Git version control
   - Cloud deployment
   - Security best practices

### Viva Questions

**Q: Why SQLite + Cloudinary?**
- Fast local operations + cloud redundancy

**Q: How does auction timer work?**
- JavaScript setInterval updates every second
- Backend validates on each API call

**Q: How is property transferred?**
- Backend checks expired auctions
- Finds highest bidder
- Updates property owner atomically

---

## 🐛 Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Port already in use"
Edit `app.py`, change port:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

### "Database locked"
- Close any DB browser
- Restart server

### More issues?
See [EXECUTION_GUIDE.md](EXECUTION_GUIDE.md) → Troubleshooting section

---

## 🔐 Security Notes

**Current (Demo):**
- Plain text passwords
- No CSRF protection
- Frontend-only admin mode

**For Production, Add:**
- Password hashing (bcrypt)
- JWT authentication
- CSRF tokens
- Rate limiting
- Input validation

---

## 📈 Scaling Path

**Current:** SQLite + Cloudinary  
**Phase 2:** PostgreSQL + Cloudinary  
**Phase 3:** PostgreSQL + Redis + Cloudinary + Load Balancer

---

## 🤝 Contributing

This is a college project, but suggestions welcome!

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open pull request

---

## 📄 License

This project is for educational purposes.

---

## 👨‍💻 Author

**Your Name**
- Portfolio: [your-portfolio.com]
- GitHub: [@your-username]
- LinkedIn: [your-linkedin]

---

## 🙏 Acknowledgments

- Bootstrap team for UI components
- Leaflet.js for mapping library
- Cloudinary for cloud storage
- Render for hosting platform
- OpenStreetMap contributors

---

## 📞 Support

For questions or issues:
- Check documentation in `/docs`
- Review [EXECUTION_GUIDE.md](EXECUTION_GUIDE.md)
- Open an issue on GitHub

---

**Made with ❤️ for college project**

⭐ Star this repository if you found it helpful!

🔗 **Live Demo:** [your-render-url.onrender.com]
