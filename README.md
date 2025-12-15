# Logistics Twin

![Python](https://img.shields.io/badge/python-3.11-blue)
![Flask](https://img.shields.io/badge/flask-3.0-green)
![Version](https://img.shields.io/badge/version-5.6.1-orange)
![License](https://img.shields.io/badge/license-MIT-blue)
![Tests](https://img.shields.io/badge/tests-8%20passed-brightgreen)

**Multi-Agent Reinforcement Learning System for Logistics Route Optimization**

> Production-ready Flask application simulating 5 competing AI agents (Q-Learning, SARSA, Monte Carlo, TD-Lambda, Dyna-Q) optimizing delivery routes across Java's industrial supply chain with real-time disaster simulation.

🔗 **[Live Demo](#)** | 📚 **[Documentation](./README.md)** | 🐛 **[Report Issues](https://github.com/loxleyftsck/logistics-twin/issues)**

---

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/loxleyftsck/logistics-twin.git
cd logistics-twin

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

Visit: **http://localhost:5000**

---

## ✨ Features

### 🤖 Multi-Agent Learning
- **5 RL Algorithms:** Q-Learning, SARSA, Monte Carlo, TD-Lambda, Dyna-Q
- Real-time competition & performance comparison
- Interactive decision explanation system

### 🗺️ Interactive Simulation
- **25 Industrial Nodes** across Java island
- Live route visualization with Leaflet.js
- OSRM-powered realistic routing

### 🌪️ Dynamic Disaster System
- 3 severity levels (L1-L3)
- Moving storms, decaying floods
- Real-time physics updates

### 💰 Economic Modeling
- Fleet management (Diesel, Hybrid, EV, LNG)
- Profit/loss calculation
- CO₂ emissions tracking

---

## 🛠️ Tech Stack

**Backend:**
- Flask 3.0 + Python 3.11
- Reinforcement Learning (custom agents)
- NumPy for matrix operations

**Frontend:**
- Vanilla JavaScript
- Leaflet.js for mapping
- Bootstrap 5 for UI

**Infrastructure:**
- Docker multi-stage build
- CORS-enabled API
- Rate limiting protection

---

## 📊 Project Status

**Version:** V5.6.1 Production Ready  
**Compliance Score:** 7.0/10  
**Test Coverage:** 26% (8/8 core tests passing)  
**Security:** Rate-limited, CORS-enabled, non-root Docker

---

## 📖 Documentation

- [CHANGELOG](./CHANGELOG.md) - Version history
- [Security Audit](./SECURITY_AUDIT.md) - Security assessment
- [Development Log](./LOGBOOK.md) - Development notes
- [API Documentation](#) - API endpoints reference

---

## 🐳 Docker Deployment

```bash
# Build image
docker-compose up -d

# Access via
http://localhost:5000
```

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest -v

# With coverage
python -m pytest --cov
```

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'feat: add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](./LICENSE) file.

---

## 🙏 Acknowledgments

- OSRM for routing API
- Flask community
- Bootstrap team

---

## 📧 Contact

**GitHub:** [@loxleyftsck](https://github.com/loxleyftsck)  
**Project Link:** https://github.com/loxleyftsck/logistics-twin

---

<p align="center">Made with ❤️ for logistics optimization</p>
