import streamlit as st
import json
import os
from datetime import datetime, timedelta
import base64
from pathlib import Path
import shutil

# ============================================
# PAGE CONFIG & SETUP
# ============================================
st.set_page_config(
    page_title="My Colony - Community App",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main { padding-top: 1rem; }
    .stMetric { background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; }
    .donation-card { background-color: #fff3cd; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #ffc107; }
    .notice-card { background-color: #e7f3ff; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #0066cc; }
    .success-card { background-color: #d4edda; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #28a745; }
    .warning-card { background-color: #fff3cd; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #ffc107; }
    .header-title { color: #1f77b4; font-weight: bold; font-size: 2rem; }
</style>
""", unsafe_allow_html=True)

# ============================================
# DATA STORAGE SETUP
# ============================================
DATA_DIR = Path("colony_data")
DATA_DIR.mkdir(exist_ok=True)

# File paths
RESIDENTS_FILE = DATA_DIR / "residents.json"
DONATIONS_FILE = DATA_DIR / "donations.json"
GUARDS_FILE = DATA_DIR / "guards.json"
NOTICES_FILE = DATA_DIR / "notices.json"
SUNDARKAND_FILE = DATA_DIR / "sundarkand.json"
COMPLAINTS_FILE = DATA_DIR / "complaints.json"
LOST_FOUND_FILE = DATA_DIR / "lost_found.json"
FESTIVALS_FILE = DATA_DIR / "festivals.json"
EMERGENCY_FILE = DATA_DIR / "emergency.json"
UPLOADS_DIR = DATA_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

# ============================================
# UTILITY FUNCTIONS
# ============================================

def load_json(filepath, default=None):
    """Load JSON file, return default if not exists"""
    if default is None:
        default = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

def save_json(filepath, data):
    """Save JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def auto_delete_old_data():
    """Delete data older than 2 months"""
    cutoff_date = datetime.now() - timedelta(days=60)
    
    # Clean donations older than 2 months
    donations = load_json(DONATIONS_FILE)
    donations = [d for d in donations if datetime.strptime(d['date'], '%Y-%m-%d %H:%M:%S') > cutoff_date]
    save_json(DONATIONS_FILE, donations)
    
    # Clean complaints older than 2 months
    complaints = load_json(COMPLAINTS_FILE)
    complaints = [c for c in complaints if datetime.strptime(c['date'], '%Y-%m-%d %H:%M:%S') > cutoff_date]
    save_json(COMPLAINTS_FILE, complaints)
    
    # Clean lost & found older than 2 months
    lost_found = load_json(LOST_FOUND_FILE)
    lost_found = [lf for lf in lost_found if datetime.strptime(lf['date'], '%Y-%m-%d %H:%M:%S') > cutoff_date]
    save_json(LOST_FOUND_FILE, lost_found)

def get_all_residents():
    """Get list of all residents"""
    return load_json(RESIDENTS_FILE)

def get_resident_by_id(resident_id):
    """Get single resident by ID"""
    residents = get_all_residents()
    for r in residents:
        if r.get('id') == resident_id:
            return r
    return None

def format_phone(phone):
    """Format phone number"""
    phone = str(phone).strip()
    if len(phone) == 10:
        return f"+91-{phone}"
    return phone

# ============================================
# SIDEBAR - MAIN NAVIGATION
# ============================================

st.sidebar.markdown("# 🏘️ MY COLONY")
st.sidebar.markdown("---")

# Session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = "Home"

page = st.sidebar.radio(
    "Navigate",
    [
        "Home",
        "💰 Mandir Donation",
        "👥 Residents Directory",
        "🚔 Guard Details",
        "📢 Notices",
        "🕉️ Sundarkand (Saturday)",
        "⚠️ Complaints",
        "🔍 Lost & Found",
        "📅 Festival Calendar",
        "🆘 Emergency Contacts",
        "⚙️ Admin Panel"
    ]
)

# Password for admin panel
ADMIN_PASSWORD = "mycolony2024"

# ============================================
# PAGE 1: HOME
# ============================================

if page == "Home":
    st.markdown('<h1 class="header-title">🏘️ Welcome to My Colony</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        donations = load_json(DONATIONS_FILE)
        recent_donations = [d for d in donations if (datetime.now() - datetime.strptime(d['date'], '%Y-%m-%d %H:%M:%S')).days <= 30]
        total = sum(d['amount'] for d in recent_donations)
        st.metric("💰 This Month", f"₹{total:,.0f}", f"{len(recent_donations)} donations")
    
    with col2:
        residents = get_all_residents()
        st.metric("👥 Members", len(residents), "households")
    
    with col3:
        guards = load_json(GUARDS_FILE)
        st.metric("🚔 Guards", len(guards), "on duty")
    
    with col4:
        notices = load_json(NOTICES_FILE)
        recent_notices = [n for n in notices if (datetime.now() - datetime.strptime(n['date'], '%Y-%m-%d %H:%M:%S')).days <= 7]
        st.metric("📢 New Notices", len(recent_notices), "this week")
    
    st.markdown("---")
    st.markdown("### 📌 Quick Links")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💰 Donate to Mandir", use_container_width=True):
            st.session_state.page = "💰 Mandir Donation"
            st.rerun()
    
    with col2:
        if st.button("👥 View Directory", use_container_width=True):
            st.session_state.page = "👥 Residents Directory"
            st.rerun()
    
    with col3:
        if st.button("📢 Notices", use_container_width=True):
            st.session_state.page = "📢 Notices"
            st.rerun()
    
    with col4:
        if st.button("🕉️ Sundarkand", use_container_width=True):
            st.session_state.page = "🕉️ Sundarkand (Saturday)"
            st.rerun()
    
    st.markdown("---")
    
    # Latest notices
    st.markdown("### 📬 Latest Notices")
    notices = load_json(NOTICES_FILE)
    if notices:
        for notice in sorted(notices, key=lambda x: x['date'], reverse=True)[:3]:
            with st.container():
                st.markdown(f"""
                <div class="notice-card">
                <b>{notice['title']}</b><br>
                <small>{notice['date']}</small><br>
                {notice['content']}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No notices yet. Check back soon!")

# ============================================
# PAGE 2: MANDIR DONATION
# ============================================

elif page == "💰 Mandir Donation":
    st.markdown("# 💰 Mandir Donation (Chanda)")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["Donate", "View History", "Monthly Summary"])
    
    with tab1:
        st.markdown("### Donate to Mandir Pooja")
        
        col1, col2 = st.columns(2)
        
        with col1:
            residents = get_all_residents()
            resident_names = [f"{r['name']} - House {r['house_no']}" for r in residents]
            
            if resident_names:
                selected_resident = st.selectbox("Select Your Name", resident_names)
                resident_id = residents[resident_names.index(selected_resident)]['id']
            else:
                st.error("⚠️ No residents found. Ask admin to add you first.")
                resident_id = None
        
        with col2:
            donation_month = st.selectbox("Month", 
                [f"{(datetime.now() - timedelta(days=30*i)).strftime('%B %Y')}" for i in range(12)])
        
        col1, col2 = st.columns(2)
        
        with col1:
            amount = st.number_input("Amount (₹)", min_value=0, value=500, step=100)
        
        with col2:
            payment_method = st.selectbox("Payment Method", ["UPI", "Bank Transfer", "Cash", "Other"])
        
        st.markdown("### Upload Transaction Screenshot")
        uploaded_file = st.file_uploader("Upload payment proof (JPG, PNG, PDF)", type=['jpg', 'jpeg', 'png', 'pdf'])
        
        notes = st.text_area("Additional notes (optional)", placeholder="E.g., Transaction reference number...")
        
        if st.button("✅ Submit Donation", use_container_width=True, type="primary"):
            if resident_id and amount > 0 and uploaded_file:
                # Save file
                file_ext = uploaded_file.name.split('.')[-1]
                filename = f"donation_{resident_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_ext}"
                filepath = UPLOADS_DIR / filename
                with open(filepath, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                
                # Save donation record
                donations = load_json(DONATIONS_FILE)
                donations.append({
                    'id': len(donations) + 1,
                    'resident_id': resident_id,
                    'resident_name': selected_resident.split(' - ')[0],
                    'amount': amount,
                    'month': donation_month,
                    'payment_method': payment_method,
                    'screenshot': filename,
                    'notes': notes,
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'status': 'pending'  # Admin will verify
                })
                save_json(DONATIONS_FILE, donations)
                st.success(f"✅ Donation of ₹{amount} submitted! Admin will verify shortly.")
            else:
                st.error("❌ Please fill all required fields")
    
    with tab2:
        st.markdown("### Donation History")
        donations = load_json(DONATIONS_FILE)
        
        if donations:
            # Filter for current user if in donor view
            filtered = sorted(donations, key=lambda x: x['date'], reverse=True)
            
            for donation in filtered[:20]:
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.markdown(f"**{donation['resident_name']}** • House {donation.get('house_no', 'N/A')}")
                    st.caption(f"{donation['date']} • {donation['month']}")
                
                with col2:
                    st.markdown(f"**₹{donation['amount']}** • {donation['payment_method']}")
                    status_color = "🟢" if donation['status'] == 'verified' else "🟡"
                    st.caption(f"{status_color} {donation['status'].upper()}")
                
                with col3:
                    if st.button("View Screenshot", key=f"view_{donation['id']}"):
                        st.session_state[f"show_ss_{donation['id']}"] = True
                
                if st.session_state.get(f"show_ss_{donation['id']}", False):
                    file_path = UPLOADS_DIR / donation['screenshot']
                    if file_path.exists():
                        st.image(str(file_path), use_container_width=True)
                
                st.divider()
        else:
            st.info("No donations yet.")
    
    with tab3:
        st.markdown("### Monthly Summary")
        donations = load_json(DONATIONS_FILE)
        
        if donations:
            # Group by month
            months_data = {}
            for d in donations:
                month = d['month']
                if month not in months_data:
                    months_data[month] = {'total': 0, 'count': 0, 'verified': 0}
                months_data[month]['total'] += d['amount']
                months_data[month]['count'] += 1
                if d['status'] == 'verified':
                    months_data[month]['verified'] += 1
            
            for month in sorted(months_data.keys(), reverse=True):
                data = months_data[month]
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(month, f"₹{data['total']:,.0f}")
                with col2:
                    st.metric("Count", data['count'])
                with col3:
                    st.metric("Verified", data['verified'])
                st.divider()
        else:
            st.info("No donation data yet.")

# ============================================
# PAGE 3: RESIDENTS DIRECTORY
# ============================================

elif page == "👥 Residents Directory":
    st.markdown("# 👥 Residents Directory")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["View Directory", "My Profile"])
    
    with tab1:
        st.markdown("### All Colony Members")
        
        col1, col2 = st.columns(2)
        
        with col1:
            search_name = st.text_input("🔍 Search by name or house number")
        
        with col2:
            sort_by = st.selectbox("Sort by", ["House Number", "Name", "WiFi Provider", "Milk Supplier"])
        
        residents = get_all_residents()
        
        # Search and filter
        if search_name:
            residents = [r for r in residents if 
                        search_name.lower() in r['name'].lower() or 
                        search_name.lower() in str(r['house_no']).lower()]
        
        # Sort
        if sort_by == "Name":
            residents = sorted(residents, key=lambda x: x['name'])
        elif sort_by == "House Number":
            residents = sorted(residents, key=lambda x: int(x['house_no']))
        elif sort_by == "WiFi Provider":
            residents = sorted(residents, key=lambda x: x.get('wifi_provider', 'Unknown'))
        else:
            residents = sorted(residents, key=lambda x: x.get('milk_supplier', 'Unknown'))
        
        if residents:
            st.markdown(f"**Total Members: {len(residents)}**")
            
            for resident in residents:
                with st.container():
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown(f"**House {resident['house_no']}**")
                        st.markdown(f"{resident['name']}")
                    
                    with col2:
                        st.markdown("📱 **Phone**")
                        st.markdown(f"{format_phone(resident['phone'])}")
                    
                    with col3:
                        st.markdown("📡 **WiFi**")
                        st.markdown(f"{resident.get('wifi_provider', 'N/A')}")
                    
                    with col4:
                        st.markdown("🥛 **Milk**")
                        st.markdown(f"{resident.get('milk_supplier', 'N/A')}")
                
                st.divider()
        else:
            st.info("No residents found.")
    
    with tab2:
        st.markdown("### Update Your Profile")
        
        residents = get_all_residents()
        if not residents:
            st.warning("⚠️ No resident profile found. Contact admin to create one.")
        else:
            resident_names = [f"{r['name']} - House {r['house_no']}" for r in residents]
            selected = st.selectbox("Select your profile", resident_names, key="profile_select")
            selected_resident = residents[resident_names.index(selected)]
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_phone = st.text_input("Phone Number", value=selected_resident['phone'])
            
            with col2:
                new_wifi = st.text_input("WiFi Provider", value=selected_resident.get('wifi_provider', ''))
            
            new_milk = st.text_input("Milk Supplier", value=selected_resident.get('milk_supplier', ''))
            
            if st.button("💾 Update Profile", use_container_width=True, type="primary"):
                # Update in residents list
                for r in residents:
                    if r['id'] == selected_resident['id']:
                        r['phone'] = new_phone
                        r['wifi_provider'] = new_wifi
                        r['milk_supplier'] = new_milk
                
                save_json(RESIDENTS_FILE, residents)
                st.success("✅ Profile updated successfully!")

# ============================================
# PAGE 4: GUARD DETAILS
# ============================================

elif page == "🚔 Guard Details":
    st.markdown("# 🚔 Guard Details")
    st.markdown("---")
    
    guards = load_json(GUARDS_FILE)
    
    if guards:
        st.markdown("### Current Security Staff")
        
        for guard in guards:
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.markdown(f"**👮 {guard['name']}**")
                    st.caption(f"Shift: {guard['shift']}")
                
                with col2:
                    st.markdown("📞 Contact")
                    st.markdown(f"**{format_phone(guard['phone'])}**")
                
                with col3:
                    st.markdown("ID")
                    st.caption(guard.get('id_number', 'N/A'))
                
                if guard.get('notes'):
                    st.caption(f"📝 {guard['notes']}")
            
            st.divider()
    else:
        st.info("ℹ️ No guard details added yet. Contact admin.")

# ============================================
# PAGE 5: NOTICES
# ============================================

elif page == "📢 Notices":
    st.markdown("# 📢 Notices & Announcements")
    st.markdown("---")
    
    notices = load_json(NOTICES_FILE)
    
    if notices:
        for notice in sorted(notices, key=lambda x: x['date'], reverse=True):
            with st.container():
                st.markdown(f"### 📌 {notice['title']}")
                st.caption(f"Posted on {notice['date']}")
                st.markdown(notice['content'])
                
                if notice.get('category'):
                    col1, col2 = st.columns([4, 1])
                    with col2:
                        st.caption(f"Category: {notice['category']}")
            
            st.divider()
    else:
        st.info("No notices yet.")

# ============================================
# PAGE 6: SUNDARKAND (SATURDAY)
# ============================================

elif page == "🕉️ Sundarkand (Saturday)":
    st.markdown("# 🕉️ Sundarkand - Saturday Volunteers")
    st.markdown("*Every Saturday at Colony Mandir*")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Register to Host", "Schedule"])
    
    with tab1:
        st.markdown("### Volunteer to Host This Saturday's Sundarkand")
        
        residents = get_all_residents()
        
        if residents:
            resident_names = [f"{r['name']} - House {r['house_no']}" for r in residents]
            selected = st.selectbox("Your Name", resident_names)
            selected_resident = residents[resident_names.index(selected)]
            
            host_date = st.date_input("Date", value=None)
            
            phone = st.text_input("Phone Number", value=selected_resident.get('phone', ''))
            
            notes = st.text_area("Anything special? (optional)", placeholder="Will host prasad, kirtan details, etc.")
            
            if st.button("✅ Register as Host", use_container_width=True, type="primary"):
                if host_date:
                    sundarkand = load_json(SUNDARKAND_FILE)
                    
                    # Check if already registered
                    existing = [s for s in sundarkand if s['date'] == str(host_date)]
                    if existing:
                        st.warning("⚠️ Someone already registered for this date!")
                    else:
                        sundarkand.append({
                            'id': len(sundarkand) + 1,
                            'date': str(host_date),
                            'resident_id': selected_resident['id'],
                            'name': selected_resident['name'],
                            'house_no': selected_resident['house_no'],
                            'phone': phone,
                            'notes': notes,
                            'registered_on': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                        save_json(SUNDARKAND_FILE, sundarkand)
                        st.success(f"✅ You've registered to host Sundarkand on {host_date}!")
        else:
            st.error("No residents found.")
    
    with tab2:
        st.markdown("### Upcoming Sundarkand Schedule")
        
        sundarkand = load_json(SUNDARKAND_FILE)
        
        if sundarkand:
            for event in sorted(sundarkand, key=lambda x: x['date'], reverse=True):
                with st.container():
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.markdown(f"📅 **{event['date']}**")
                        st.caption(f"House {event['house_no']}")
                    
                    with col2:
                        st.markdown(f"**{event['name']}**")
                        st.caption(f"📞 {format_phone(event['phone'])}")
                    
                    with col3:
                        st.caption("Confirmed ✅")
                    
                    if event.get('notes'):
                        st.caption(f"📝 {event['notes']}")
                
                st.divider()
        else:
            st.info("ℹ️ No Sundarkand registered yet for upcoming Saturdays.")
            st.warning("📢 If no one registers by Thursday, Sundarkand will be held at Colony Mandir.")

# ============================================
# PAGE 7: COMPLAINTS
# ============================================

elif page == "⚠️ Complaints":
    st.markdown("# ⚠️ Complaints & Maintenance")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["File Complaint", "View All"])
    
    with tab1:
        st.markdown("### File a Complaint")
        
        residents = get_all_residents()
        
        if residents:
            resident_names = [f"{r['name']} - House {r['house_no']}" for r in residents]
            selected = st.selectbox("Your Name", resident_names, key="complaint_resident")
            selected_resident = residents[resident_names.index(selected)]
            
            category = st.selectbox("Complaint Category", [
                "Streetlight",
                "Water Supply",
                "Garbage Collection",
                "Road/Pavement",
                "Pest Control",
                "Noise",
                "Security",
                "Maintenance",
                "Other"
            ])
            
            title = st.text_input("Complaint Title")
            
            description = st.text_area("Detailed Description", height=150)
            
            urgency = st.selectbox("Urgency", ["Low", "Medium", "High"])
            
            location = st.text_input("Location in Colony (e.g., Gate Area, Block A)")
            
            if st.button("📤 Submit Complaint", use_container_width=True, type="primary"):
                if title and description:
                    complaints = load_json(COMPLAINTS_FILE)
                    complaints.append({
                        'id': len(complaints) + 1,
                        'resident_id': selected_resident['id'],
                        'name': selected_resident['name'],
                        'house_no': selected_resident['house_no'],
                        'category': category,
                        'title': title,
                        'description': description,
                        'urgency': urgency,
                        'location': location,
                        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'status': 'open'
                    })
                    save_json(COMPLAINTS_FILE, complaints)
                    st.success("✅ Complaint filed successfully!")
                else:
                    st.error("Please fill all required fields")
        else:
            st.error("No residents found.")
    
    with tab2:
        st.markdown("### All Complaints")
        
        complaints = load_json(COMPLAINTS_FILE)
        
        if complaints:
            status_filter = st.selectbox("Filter by Status", ["All", "Open", "In Progress", "Resolved"])
            
            if status_filter != "All":
                complaints = [c for c in complaints if c['status'] == status_filter.lower()]
            
            for complaint in sorted(complaints, key=lambda x: x['date'], reverse=True):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{complaint['title']}**")
                        st.caption(f"{complaint['name']} - House {complaint['house_no']}")
                        st.caption(f"{complaint['category']} • {complaint['date']}")
                    
                    with col2:
                        color = "🔴" if complaint['urgency'] == "High" else "🟡" if complaint['urgency'] == "Medium" else "🟢"
                        st.markdown(f"{color} {complaint['urgency']}")
                    
                    st.markdown(complaint['description'])
                    st.caption(f"📍 Location: {complaint['location']}")
                
                st.divider()
        else:
            st.info("No complaints yet.")

# ============================================
# PAGE 8: LOST & FOUND
# ============================================

elif page == "🔍 Lost & Found":
    st.markdown("# 🔍 Lost & Found")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Post Item", "Browse"])
    
    with tab1:
        st.markdown("### Post Lost or Found Item")
        
        residents = get_all_residents()
        
        if residents:
            resident_names = [f"{r['name']} - House {r['house_no']}" for r in residents]
            selected = st.selectbox("Your Name", resident_names, key="lostandfound_resident")
            selected_resident = residents[resident_names.index(selected)]
            
            item_type = st.selectbox("Type", ["Lost", "Found"])
            
            category = st.selectbox("Category", [
                "Pet",
                "Keys",
                "Phone/Electronics",
                "Wallet/Money",
                "Cycle/Vehicle",
                "Clothing",
                "Documents",
                "Jewelry",
                "Other"
            ])
            
            description = st.text_area("Item Description", height=100)
            
            location = st.text_input("Location/Area")
            
            date_occurred = st.date_input("Date of incident")
            
            contact = st.text_input("Contact Number", value=selected_resident.get('phone', ''))
            
            reward = st.text_input("Reward (if any)", placeholder="e.g., ₹500 reward for lost keys")
            
            if st.button("📤 Post Item", use_container_width=True, type="primary"):
                if description and location:
                    lost_found = load_json(LOST_FOUND_FILE)
                    lost_found.append({
                        'id': len(lost_found) + 1,
                        'type': item_type,
                        'category': category,
                        'description': description,
                        'location': location,
                        'date': str(date_occurred),
                        'posted_on': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'resident_name': selected_resident['name'],
                        'house_no': selected_resident['house_no'],
                        'contact': contact,
                        'reward': reward,
                        'status': 'active'
                    })
                    save_json(LOST_FOUND_FILE, lost_found)
                    st.success("✅ Item posted successfully!")
                else:
                    st.error("Please fill all required fields")
        else:
            st.error("No residents found.")
    
    with tab2:
        st.markdown("### Browse Items")
        
        lost_found = load_json(LOST_FOUND_FILE)
        
        if lost_found:
            col1, col2 = st.columns(2)
            
            with col1:
                type_filter = st.selectbox("Type", ["All", "Lost", "Found"])
            
            with col2:
                category_filter = st.selectbox("Category", ["All"] + list(set(lf['category'] for lf in lost_found)))
            
            if type_filter != "All":
                lost_found = [lf for lf in lost_found if lf['type'] == type_filter]
            
            if category_filter != "All":
                lost_found = [lf for lf in lost_found if lf['category'] == category_filter]
            
            for item in sorted(lost_found, key=lambda x: x['posted_on'], reverse=True):
                with st.container():
                    emoji = "❌" if item['type'] == "Lost" else "✅"
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{emoji} {item['type']} - {item['category']}**")
                        st.markdown(item['description'])
                        st.caption(f"{item['resident_name']} (House {item['house_no']}) • {item['date']}")
                    
                    with col2:
                        st.markdown("📍 **Location**")
                        st.caption(item['location'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.caption(f"📱 {format_phone(item['contact'])}")
                    with col2:
                        if item.get('reward'):
                            st.caption(f"💰 {item['reward']}")
                
                st.divider()
        else:
            st.info("No items posted yet.")

# ============================================
# PAGE 9: FESTIVAL CALENDAR
# ============================================

elif page == "📅 Festival Calendar":
    st.markdown("# 📅 Festival Calendar & Events")
    st.markdown("---")
    
    festivals = load_json(FESTIVALS_FILE)
    
    if festivals:
        # Group by month
        months_events = {}
        for fest in festivals:
            month = datetime.strptime(fest['date'], '%Y-%m-%d').strftime('%B %Y')
            if month not in months_events:
                months_events[month] = []
            months_events[month].append(fest)
        
        for month in sorted(months_events.keys()):
            st.markdown(f"### 📌 {month}")
            
            for fest in sorted(months_events[month], key=lambda x: x['date']):
                with st.container():
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**🎉 {fest['name']}**")
                        st.markdown(f"{fest['description']}")
                        st.caption(f"📅 {fest['date']}")
                    
                    with col2:
                        st.caption(f"Category: {fest.get('category', 'Festival')}")
                    
                    if fest.get('details'):
                        st.caption(f"📝 {fest['details']}")
                
                st.divider()
    else:
        st.info("No events scheduled yet.")

# ============================================
# PAGE 10: EMERGENCY CONTACTS
# ============================================

elif page == "🆘 Emergency Contacts":
    st.markdown("# 🆘 Emergency Contacts & Quick Reference")
    st.markdown("---")
    
    emergency_contacts = load_json(EMERGENCY_FILE)
    
    if emergency_contacts:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Medical")
            for contact in emergency_contacts:
                if contact.get('category') == 'Medical':
                    st.markdown(f"""
                    **{contact['name']}**
                    📞 {format_phone(contact['phone'])}
                    """)
        
        with col2:
            st.markdown("### Police & Security")
            for contact in emergency_contacts:
                if contact.get('category') == 'Police':
                    st.markdown(f"""
                    **{contact['name']}**
                    📞 {format_phone(contact['phone'])}
                    """)
        
        st.divider()
        
        st.markdown("### Utilities & Services")
        for contact in emergency_contacts:
            if contact.get('category') not in ['Medical', 'Police']:
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.markdown(f"**{contact['name']}**")
                
                with col2:
                    st.markdown(f"📞 {format_phone(contact['phone'])}")
                
                with col3:
                    st.caption(contact.get('category', 'Service'))
                
                st.divider()
    else:
        st.info("No emergency contacts added yet.")

# ============================================
# PAGE 11: ADMIN PANEL
# ============================================

elif page == "⚙️ Admin Panel":
    st.markdown("# ⚙️ Admin Panel")
    st.markdown("---")
    
    # Admin login
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False
    
    if not st.session_state.admin_logged_in:
        st.warning("🔐 Admin access required")
        
        password = st.text_input("Enter Admin Password", type="password")
        
        if st.button("🔓 Login"):
            if password == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.success("✅ Admin logged in!")
                st.rerun()
            else:
                st.error("❌ Wrong password")
    else:
        st.success("✅ Admin logged in")
        
        if st.button("🔓 Logout"):
            st.session_state.admin_logged_in = False
            st.rerun()
        
        st.markdown("---")
        
        admin_tab1, admin_tab2, admin_tab3, admin_tab4, admin_tab5 = st.tabs([
            "👥 Residents",
            "💰 Donations",
            "🚔 Guards",
            "📢 Notices",
            "⚡ Settings"
        ])
        
        # ============ RESIDENTS TAB ============
        with admin_tab1:
            st.markdown("### Manage Residents")
            
            sub_tab1, sub_tab2 = st.tabs(["Add Resident", "Edit/Delete"])
            
            with sub_tab1:
                st.markdown("#### Add New Resident")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Full Name")
                    house_no = st.number_input("House Number", min_value=1)
                
                with col2:
                    phone = st.text_input("Phone Number")
                    wifi = st.text_input("WiFi Provider")
                
                milk = st.text_input("Milk Supplier")
                
                if st.button("➕ Add Resident"):
                    if name and house_no:
                        residents = get_all_residents()
                        residents.append({
                            'id': len(residents) + 1,
                            'name': name,
                            'house_no': house_no,
                            'phone': phone,
                            'wifi_provider': wifi,
                            'milk_supplier': milk
                        })
                        save_json(RESIDENTS_FILE, residents)
                        st.success(f"✅ Added {name}")
                    else:
                        st.error("Name and House No required")
            
            with sub_tab2:
                residents = get_all_residents()
                
                if residents:
                    selected = st.selectbox("Select Resident", 
                        [f"{r['name']} - House {r['house_no']}" for r in residents])
                    
                    resident = residents[[f"{r['name']} - House {r['house_no']}" for r in residents].index(selected)]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("❌ Delete", use_container_width=True):
                            residents = [r for r in residents if r['id'] != resident['id']]
                            save_json(RESIDENTS_FILE, residents)
                            st.success("✅ Resident deleted")
        
        # ============ DONATIONS TAB ============
        with admin_tab2:
            st.markdown("### Verify Donations")
            
            donations = load_json(DONATIONS_FILE)
            pending = [d for d in donations if d['status'] == 'pending']
            
            if pending:
                st.markdown(f"**Pending: {len(pending)}**")
                
                for donation in pending:
                    with st.container():
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.markdown(f"**{donation['resident_name']}** - ₹{donation['amount']}")
                            st.caption(f"{donation['date']}")
                        
                        with col2:
                            if st.button("✅ Verify", key=f"verify_{donation['id']}"):
                                donation['status'] = 'verified'
                                save_json(DONATIONS_FILE, donations)
                                st.success("✅ Verified!")
                        
                        with col3:
                            if st.button("❌ Reject", key=f"reject_{donation['id']}"):
                                donation['status'] = 'rejected'
                                save_json(DONATIONS_FILE, donations)
                                st.error("❌ Rejected")
                        
                        # Show screenshot
                        if st.button("View Screenshot", key=f"admin_view_{donation['id']}"):
                            file_path = UPLOADS_DIR / donation['screenshot']
                            if file_path.exists():
                                st.image(str(file_path), use_container_width=True)
                    
                    st.divider()
            else:
                st.success("✅ All donations verified!")
        
        # ============ GUARDS TAB ============
        with admin_tab3:
            st.markdown("### Manage Guard Details")
            
            sub_tab1, sub_tab2 = st.tabs(["Add Guard", "Edit/Delete"])
            
            with sub_tab1:
                st.markdown("#### Add Guard")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    guard_name = st.text_input("Guard Name")
                    guard_phone = st.text_input("Phone Number")
                
                with col2:
                    guard_shift = st.selectbox("Shift", ["Day (6AM-2PM)", "Night (2PM-10PM)", "Full Time"])
                    guard_id = st.text_input("ID Number")
                
                guard_notes = st.text_area("Notes (optional)")
                
                if st.button("➕ Add Guard"):
                    if guard_name and guard_phone:
                        guards = load_json(GUARDS_FILE)
                        guards.append({
                            'id': len(guards) + 1,
                            'name': guard_name,
                            'phone': guard_phone,
                            'shift': guard_shift,
                            'id_number': guard_id,
                            'notes': guard_notes
                        })
                        save_json(GUARDS_FILE, guards)
                        st.success("✅ Guard added")
            
            with sub_tab2:
                guards = load_json(GUARDS_FILE)
                
                if guards:
                    for guard in guards:
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**{guard['name']}** - {guard['shift']}")
                        
                        with col2:
                            if st.button("🗑️ Delete", key=f"del_guard_{guard['id']}"):
                                guards = [g for g in guards if g['id'] != guard['id']]
                                save_json(GUARDS_FILE, guards)
                                st.success("✅ Deleted")
        
        # ============ NOTICES TAB ============
        with admin_tab4:
            st.markdown("### Post Notice")
            
            notice_title = st.text_input("Notice Title")
            
            notice_content = st.text_area("Content", height=150)
            
            notice_category = st.selectbox("Category", [
                "General",
                "Water Supply",
                "Maintenance",
                "Festival",
                "Security",
                "Meeting",
                "Other"
            ])
            
            if st.button("📤 Post Notice", use_container_width=True, type="primary"):
                if notice_title and notice_content:
                    notices = load_json(NOTICES_FILE)
                    notices.append({
                        'id': len(notices) + 1,
                        'title': notice_title,
                        'content': notice_content,
                        'category': notice_category,
                        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    save_json(NOTICES_FILE, notices)
                    st.success("✅ Notice posted!")
        
        # ============ SETTINGS TAB ============
        with admin_tab5:
            st.markdown("### Settings")
            
            if st.button("🗑️ Auto-Delete Old Data (2+ months)", use_container_width=True):
                auto_delete_old_data()
                st.success("✅ Old data deleted!")
            
            st.markdown("---")
            
            if st.button("📊 View Statistics"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    residents = get_all_residents()
                    st.metric("Residents", len(residents))
                
                with col2:
                    donations = load_json(DONATIONS_FILE)
                    st.metric("Donations", len(donations))
                
                with col3:
                    complaints = load_json(COMPLAINTS_FILE)
                    st.metric("Complaints", len(complaints))
            
            st.markdown("---")
            
            st.markdown("### Add Festival Events")
            
            fest_name = st.text_input("Festival/Event Name")
            fest_date = st.date_input("Date")
            fest_desc = st.text_area("Description")
            fest_category = st.selectbox("Category", ["Festival", "Cleaning Drive", "Meeting", "Social", "Other"])
            
            if st.button("📅 Add Festival"):
                if fest_name and fest_date:
                    festivals = load_json(FESTIVALS_FILE)
                    festivals.append({
                        'id': len(festivals) + 1,
                        'name': fest_name,
                        'date': str(fest_date),
                        'description': fest_desc,
                        'category': fest_category
                    })
                    save_json(FESTIVALS_FILE, festivals)
                    st.success("✅ Festival added!")
            
            st.markdown("---")
            
            st.markdown("### Add Emergency Contact")
            
            emg_name = st.text_input("Name/Service")
            emg_phone = st.text_input("Phone Number")
            emg_category = st.selectbox("Category", ["Medical", "Police", "Utilities", "Other"])
            
            if st.button("🆘 Add Contact"):
                if emg_name and emg_phone:
                    emergency = load_json(EMERGENCY_FILE)
                    emergency.append({
                        'id': len(emergency) + 1,
                        'name': emg_name,
                        'phone': emg_phone,
                        'category': emg_category
                    })
                    save_json(EMERGENCY_FILE, emergency)
                    st.success("✅ Contact added!")

# ============================================
# AUTO-CLEANUP ON LOAD
# ============================================

auto_delete_old_data()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; font-size: 0.85rem;'>
    <p>🏘️ My Colony | Built for your community</p>
    <p>Data is automatically deleted after 2 months | All transactions verified by admin</p>
</div>
""", unsafe_allow_html=True)
