# Security Audit Report - API Endpoints

## Audit Date: 2025-12-14
## Auditor: Protocol Compliance Review

---

## Executive Summary

**Scope:** Flask API endpoints security review  
**Method:** Static code analysis + threat modeling  
**Overall Score:** 6.5/10 ⚠️ (Moderate Risk)

### Critical Findings
- ⚠️ **1 High Risk** - JSON parsing without size limit
- ⚠️ **2 Medium Risk** - Missing rate limiting, no OSRM timeout
- ✅ **5 Good Practices** - Input validation, thread safety, DoS prevention

---

## Threat Analysis by Endpoint

### 1. `/api/disaster` (POST) - Create Disaster
**Risk Level: MEDIUM** 🟡

**Current Security:**
- ✅ DoS prevention (DISASTER_LIMIT = 10)
- ✅ Input validation (lat/lon, severity, radius)
- ✅ Thread-safe (Lock)
- ✅ Type checking (ValueError, TypeError)

**Vulnerabilities:**
```python
# ⚠️ No rate limiting - dapat spam disaster
# Recommendation: @limiter.limit("10 per minute")

# ⚠️ Radius tidak ada max limit di sisi server
# Current: client controls max=100, tapi POST bisa override
# Recommendation: Server-side validation
if radius > 100:
    return jsonify({"error": "Max radius 100km"}), 400
```

**Security Score: 7/10**

---

### 2. `/api/load_brain` (POST) - Load Q-table
**Risk Level: HIGH** 🔴

**Current Security:**
- ✅ City count validation
- ✅ Epsilon range checking
- ✅ Error handling

**Critical Vulnerability:**
```python
# 🔴 NO FILE SIZE LIMIT
data = request.json  # Unlimited size!

# Attack Vector:
# Attacker uploads 1GB JSON → Server OOM crash

# Recommendation:
@app.before_request
def check_content_length():
    if request.content_length and request.content_length > 10 * 1024 * 1024:  # 10MB
        abort(413, "Payload too large")
```

**Security Score: 4/10** ⚠️

---

### 3. `/api/update_config` (POST) - Update Cities
**Risk Level: MEDIUM** 🟡

**Vulnerabilities:**
```python
# ⚠️ Arbitrary data injection
cleaned_cities = {}
for k, v in new_data.items():
    cleaned_cities[int(k)] = {
        'name': v['name'],     # ⚠️ No sanitization
        'lat': float(v['lat']),
        'lon': float(v['lon'])
    }

# Attack: Inject malicious city names (XSS)
{"name": "<script>alert('XSS')</script>", "lat": 0, "lon": 0}

# Recommendation: Sanitize inputs
import html
cleaned_cities[int(k)] = {
    'name': html.escape(v['name'][:50]),  # Max 50 chars
    'lat': max(-90, min(90, float(v['lat']))),
    'lon': max(-180, min(180, float(v['lon'])))
}
```

**Security Score: 5/10**

---

### 4. External API - OSRM Routing
**Risk Level: MEDIUM** 🟡

```python
# Current code: fetchAndDrawRoute() in frontend
fetch(`https://router.project-osrm.org/route/v1/driving/${coords}?...`)

# ⚠️ No timeout → hanging requests
# ⚠️ No retry logic → fail on network blip
# ⚠️ CORS exposure (external API)

# Recommendation: Backend proxy with timeout
@app.route('/api/route', methods=['POST'])
def get_route():
    coords = request.json.get('coords')
    try:
        response = requests.get(
            f"https://router.project-osrm.org/route/v1/driving/{coords}",
            timeout=5  # ✅ 5 second timeout
        )
        return jsonify(response.json())
    except requests.Timeout:
        return jsonify({"error": "Route service timeout"}), 504
```

**Security Score: 6/10**

---

## Positive Security Practices ✅

1. **Thread Safety**
   ```python
   lock = Lock()  # Prevents race conditions
   ```

2. **Environment Variables**
   ```python
   debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
   # ✅ Production-safe defaults
   ```

3. **Input Validation**
   ```python
   if severity not in SEVERITY_LEVELS:
       return jsonify({"error": "Invalid severity"}), 400
   ```

4. **DoS Prevention**
   ```python
   if len(active_disasters) >= DISASTER_LIMIT:
       return jsonify({"error": "Limit reached"}), 429
   ```

5. **Error Handling**
   ```python
   except (ValueError, TypeError) as e:
       return jsonify({"error": str(e)}), 400
   ```

---

## Recommendations Priority

### P0 (Critical - Fix Before V5.6)
1. ✅ Add request size limit
   ```python
   app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB
   ```

2. ✅ Rate limiting
   ```bash
   pip install flask-limiter
   ```
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app, key_func=lambda: request.remote_addr)
   
   @app.route('/api/train')
   @limiter.limit("10 per minute")
   def train():
       ...
   ```

### P1 (High - V5.6)
3. ⚠️ Input sanitization for city names
4. ⚠️ OSRM proxy endpoint with timeout
5. ⚠️ CORS headers configuration

### P2 (Medium - V5.7)
6. ⚠️ API versioning (`/api/v1/`)
7. ⚠️ Request logging & monitoring
8. ⚠️ Authentication tokens (if public)

---

## Final Score Breakdown

| Category | Score | Notes |
|----------|-------|-------|
| Input Validation | 8/10 | Good, but missing sanitization |
| DoS Protection | 6/10 | Disaster limit OK, no rate limit |
| Error Handling | 8/10 | Comprehensive try-catch |
| External APIs | 5/10 | No timeout, no retry |
| Data Injection | 5/10 | XSS possible in city names |
| Thread Safety | 9/10 | Lock implemented correctly |
| **OVERALL** | **6.5/10** | **Moderate Risk** ⚠️ |

---

## Conclusion

**Ready for Production?** ⚠️ **With Conditions**

**Must Fix (P0):**
- Request size limit
- Rate limiting on `/api/train` and `/api/disaster`

**Should Fix (P1):**
- Input sanitization
- OSRM timeout

**Nice to Have (P2):**
- API versioning
- Monitoring

**Estimated Fix Time:** 2-3 hours
