import streamlit as st
import hashlib
import os
import datetime
import json
import base64
from io import BytesIO
import qrcode
import time
from PIL import Image, ImageDraw, ImageFont
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
from pyzbar import pyzbar
import numpy as np
import cv2

# Set page configuration with dark theme
st.set_page_config(
    page_title="CredX | Verification System",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling with navbar
st.markdown("""
<style>
    /* Main theme */
    .main {
        background-color: #121212;
        color: #e0e0e0;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #00ffff !important;
        font-family: 'Courier New', monospace;
        text-shadow: 0 0 5px #00ffff80;
    }
    
    /* Navbar styling */
    .navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #1a1a1a;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.2);
    }
    
    .navbar-brand {
        font-family: 'Courier New', monospace;
        font-size: 25px;
        font-weight: bold;
        color: #00ffff;
        text-shadow: 0 0 10px #00ffff;
        margin-right: 20px;
    }
    
    .navbar-links {
        display: flex;
        gap: 10px;
    }
    
    .navbar-link {
        background-color: #121212;
        color: #00ffff;
        border: 1px solid #00ffff;
        border-radius: 5px;
        padding: 5px 10px;
        text-decoration: none;
        font-family: 'Courier New', monospace;
        transition: all 0.3s;
        cursor: pointer;
    }
    
    .navbar-link:hover, .navbar-link.active {
        background-color: #00ffff;
        color: #121212;
        box-shadow: 0 0 10px #00ffff;
    }
    
    .navbar-user {
        color: #00ffff;
        font-family: 'Courier New', monospace;
    }
    # Find this section in your code around line 80-90 (after all the other CSS styles)
    /* Hide hamburger menu */
    [data-testid="collapsedControl"] {
        display: none
    }
    
    /* Dashboard specific styles - ADD THESE HERE */
    .dashboard-card {
        background-color: #1a1a1a;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid #333;
        box-shadow: 0 4px 6px rgba(0, 255, 255, 0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .dashboard-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0, 255, 255, 0.2);
    }
    .dashboard-stat {
        text-align: center;
        padding: 15px;
        background-color: #1a1a1a;
        border-radius: 5px;
        border: 1px solid #333;
    }
    .dashboard-stat-value {
        font-size: 24px;
        font-weight: bold;
        color: #00ffff;
        text-shadow: 0 0 5px rgba(0, 255, 255, 0.5);
    }
    .dashboard-stat-label {
        font-size: 14px;
        color: #ccc;
        margin-top: 5px;
    }
    /* Certificate cards */
    .certificate-card {
        background-color: #1a1a1a;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid #333;
        transition: all 0.3s;
    }
    .certificate-card:hover {
        border-color: #00ffff;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
    }
    .certificate-card h4{
        color: #00ffff;
        margin-top: 0;
    }
    /* Search and filter section */
    .search-box {
        background-color: #1a1a1a;
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid #333;
    }
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1a1a;
        border-radius: 5px 5px 0 0;
        padding: 10px 20px;
        border: 1px solid #333;
        border-bottom: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2a2a2a;
        border-color: #00ffff;
        color: #00ffff;
    }
    /* Pagination styling */
    .pagination {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 20px 0;
    }
    .pagination-btn {
        background-color: #1a1a1a;
        color: #00ffff;
        border: 1px solid #00ffff;
        border-radius: 5px;
        padding: 5px 15px;
        margin: 0 5px;
        cursor: pointer;
        transition: all 0.3s;
    }
    .pagination-btn:hover:not(.disabled) {
        background-color: #00ffff;
        color: #121212;
    }
    .pagination-btn.disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    /* Progress bar styling */
    .progress-container {
        width: 100%;
        background-color: #2a2a2a;
        border-radius: 5px;
        margin: 10px 0;
    }
    .progress-bar {
        height: 10px;
        background-color: #00ffff;
        border-radius: 5px;
        transition: width 0.5s;
    }

    /* Buttons */
    .stButton button {
        background-color: #121212;
        color: #00ffff;
        border: 1px solid #00ffff;
        border-radius: 5px;
        box-shadow: 0 0 5px #00ffff;
        transition: all 0.3s;
        font-family: 'Courier New', monospace;
    }
    
    .stButton button:hover {
        background-color: #00ffff;
        color: #121212;
        box-shadow: 0 0 15px #00ffff;
    }
    
    /* Text inputs */
    .stTextInput input, .stTextArea textarea {
        background-color: #2a2a2a;
        color: #e0e0e0;
        border: 1px solid #444;
        border-radius: 5px;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border: 1px solid #00ffff;
        box-shadow: 0 0 5px #00ffff;
    }
    
    /* Card effect for sections */
    .card {
        background-color: #1a1a1a;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid #333;
        box-shadow: 0 4px 6px rgba(0, 255, 255, 0.1);
    }
    
    /* Certificate frame */
    .certificate-frame {
        border: 2px solid #00ffff;
        border-radius: 10px;
        box-shadow: 0 0 10px #00ffff40;
        padding: 10px;
    }
    
    /* Logo styling */
    .logo-text {
        font-family: 'Courier New', monospace;
        font-size: 28px;
        font-weight: bold;
        color: #00ffff;
        text-shadow: 0 0 10px #00ffff;
        letter-spacing: 2px;
        text-align: center;
    }
    
    /* Hide hamburger menu */
    [data-testid="collapsedControl"] {
        display: none
    }
    /* General text elements */
body, .main, .card, .dashboard-card, .certificate-card {
    font-size: 18px;  /* Base size increased */
}

/* Headings */
h1 {
    font-size: 48px !important;
}
h2 {
    font-size: 42px !important;
}
h3 {
    font-size: 36px !important;
}
h4 {
    font-size: 30px !important;
}
h5 {
    font-size: 26px !important;
}
h6 {
    font-size: 22px !important;
}

/* Navbar brand */
.navbar-brand {
    font-size: 32px; /* Increased from 25px */
}

/* Navbar links */
.navbar-link {
    font-size: 18px;
    padding: 8px 15px;
}

/* Dashboard stat numbers */
.dashboard-stat-value {
    font-size: 32px;
}

/* Dashboard stat label */
.dashboard-stat-label {
    font-size: 16px;
}

/* Certificate card heading */
.certificate-card h4 {
    font-size: 24px;
}

/* Buttons */
.stButton button {
    font-size: 18px;
}

/* Text inputs */
.stTextInput input,
.stTextArea textarea {
    font-size: 16px;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    font-size: 16px;
}

/* Pagination buttons */
.pagination-btn {
    font-size: 16px;
}
</style>

""", unsafe_allow_html=True)

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'active_page' not in st.session_state:
    st.session_state.active_page = "home"
if 'qr_scan_result' not in st.session_state:
    st.session_state.qr_scan_result = ""
if 'qr_scanned' not in st.session_state:
    st.session_state.qr_scanned = False
if 'users' not in st.session_state:
    st.session_state.users = {'admin': {'password': 'admin', 'is_admin': True, 'email': 'admin@example.com'}}
if 'certificates' not in st.session_state:
    st.session_state.certificates = {}

# Ensure directories exist
os.makedirs('static/qrcode', exist_ok=True)
os.makedirs('static/certificates', exist_ok=True)

# Mock blockchain functions
def generate_digital_signature(data):
    """Generate a digital signature for the certificate data"""
    return hashlib.sha256(data.encode()).hexdigest()

def save_to_blockchain(certificate_data):
    """Mock function to save certificate data to blockchain"""
    cert_id = certificate_data['certificate_id']
    # In a real app, this would connect to a blockchain
    st.session_state.certificates[cert_id] = certificate_data
    return True

def verify_certificate_in_blockchain(certificate_id):
    """Mock function to verify certificate in blockchain"""
    return certificate_id in st.session_state.certificates

# QR Code scanning
# QR Code scanning
# QR Code scanning
class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.result = None

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        # Add a border around the frame for better visualization
        h, w = img.shape[:2]
        cv2.rectangle(img, (0, 0), (w, h), (0, 255, 255), 2)
        
        # Process the image to detect QR codes
        try:
            decoded_objs = pyzbar.decode(img)
            
            for obj in decoded_objs:
                # Draw a rectangle around detected QR code
                points = obj.polygon
                if len(points) > 4:
                    hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                    cv2.polylines(img, [hull], True, (0, 255, 0), 3)
                else:
                    pts = np.array(points, dtype=np.int32)
                    cv2.polylines(img, [pts], True, (0, 255, 0), 3)
                
                # Decode the QR code
                qr_data = obj.data.decode("utf-8")
                self.result = qr_data
                
                # Display the result on the image
                cv2.putText(img, qr_data, (obj.rect.left, obj.rect.top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Update session state
                st.session_state.qr_scan_result = qr_data
                st.session_state.qr_scanned = True
                
                break  # stop after first QR detected
        except Exception as e:
            # Just log the error and continue
            pass
        
        # Show scanning status
        status_text = "Scanning for QR code..."
        if self.result:
            status_text = f"Detected: {self.result}"
        
        cv2.putText(img, status_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return img
from PIL import Image, ImageDraw, ImageFont
import qrcode
import datetime
import os
from PIL import Image, ImageDraw, ImageFont
import qrcode
import datetime
import os
def generate_certificate(cert_id, student_name, course, contact, address):
    # Create base image
    img = Image.new('RGB', (1000, 700), color=(15, 25, 45))  # Dark blue
    d = ImageDraw.Draw(img)

    # Borders
    d.rectangle([(20, 20), (980, 680)], outline=(240, 200, 80), width=3)
    d.rectangle([(40, 40), (960, 660)], outline=(240, 200, 80), width=2)

    # Corner marks
    for x, y in [(40, 40), (40, 660), (960, 40), (960, 660)]:
        d.line([(x-15, y), (x+15, y)], fill=(240, 200, 80), width=2)
        d.line([(x, y-15), (x, y+15)], fill=(240, 200, 80), width=2)

    # Try to use calligraphy fonts for decorative text
    try:
        # Try multiple potential calligraphy fonts
        calligraphy_fonts = ['Brush Script MT', 'Comic Sans MS', 'Segoe Script', 'Times New Roman']
        
        # Find first available calligraphy font
        title_font = None
        for font in calligraphy_fonts:
            try:
                title_font = ImageFont.truetype(f"{font}.ttf", 110)
                break
            except IOError:
                continue
        
        # If no calligraphy font found, use Arial
        if not title_font:
            title_font = ImageFont.truetype("arial.ttf", 110)
        
        # Other fonts with increased sizes
        calligraphy_content = ImageFont.truetype(font if title_font else "arial.ttf", 85)
        calligraphy_small = ImageFont.truetype(font if title_font else "arial.ttf", 65)
        name_font = ImageFont.truetype("arial.ttf", 95)  # Regular font for name
        course_font = ImageFont.truetype("arial.ttf", 80)  # Regular font for course
    except IOError:
        # Fallback to default fonts
        title_font = ImageFont.load_default()
        calligraphy_content = ImageFont.load_default()
        calligraphy_small = ImageFont.load_default()
        name_font = ImageFont.load_default()
        course_font = ImageFont.load_default()

    # Title with calligraphy font
    title_text = "CERTIFICATE OF ACHIEVEMENT"
    title_width = d.textlength(title_text, font=title_font)
    d.text(((img.width - title_width) / 2, 40), title_text, fill=(240, 200, 80), font=title_font)

    # Date and ID at TOP (after title) - MOVED FROM BOTTOM
    issue_date = datetime.datetime.now().strftime("%B %d, %Y")
    date_y = 150  # Just below the title
    
    # Decorative line below title
    d.line([(150, date_y - 15), (850, date_y - 15)], fill=(240, 200, 80), width=2)
    
    # Date and ID text at top with calligraphy-style font
    d.text((180, date_y), f"Date: {issue_date}", fill=(200, 200, 220), font=calligraphy_small, anchor="lm")
    d.text((820, date_y), f"ID: {cert_id}", fill=(200, 200, 220), font=calligraphy_small, anchor="rm")

    # Main Text with calligraphy-style font
    d.text((img.width // 2, 220), "This is to certify that", fill=(200, 200, 220), font=calligraphy_content, anchor="mm")
    
    # Student name with standard font (for readability)
    d.text((img.width // 2, 300), f"{student_name}", fill=(240, 200, 80), font=name_font, anchor="mm")
    
    # More text with calligraphy-style font
    d.text((img.width // 2, 380), "has successfully completed the course", fill=(200, 200, 220), font=calligraphy_content, anchor="mm")
    
    # Course Name with standard font (for readability)
    course_y = 460
    if len(course) > 30:
        words = course.split()
        lines = []
        current = ""
        for word in words:
            test = current + " " + word if current else word
            if d.textlength(test, font=course_font) < 800:
                current = test
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        for i, line in enumerate(lines):
            d.text((img.width // 2, course_y + i * 70), line, fill=(240, 200, 80), font=course_font, anchor="mm")
        qr_y = course_y + len(lines) * 70 + 50
    else:
        d.text((img.width // 2, course_y), course, fill=(240, 200, 80), font=course_font, anchor="mm")
        qr_y = course_y + 100

    # QR Code - positioned at bottom
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=5, border=2)
    qr.add_data(cert_id)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="white", back_color=(15, 25, 45)).convert('RGB')
    qr_img = qr_img.resize((160, 160))
    
    # Fix QR code position to ensure it's always at bottom
    qr_y = min(qr_y, 520)  # Don't let it go below 520 to keep it visible
    img.paste(qr_img, ((img.width - 160) // 2, qr_y))

    # Save certificate
    os.makedirs("static/certificates", exist_ok=True)
    cert_path = f"static/certificates/{cert_id}.png"
    img.save(cert_path)

    # Return paths and signatures
    signature = f"sig_{cert_id[-6:]}"
    ipfs_url = f"https://ipfs.io/ipfs/{cert_id[:10]}"

    return cert_path, signature, ipfs_url
    # Rest of the function remains the same...
    
    # Rest of the function remains the same... # None for IPFS URL in this simplified version  # None for IPFS URL in this simplified version
# Navbar function
def render_navbar():
    st.markdown("""
    <div class="navbar">
        <div class="navbar-brand">🔐 CredX</div>
        <div class="navbar-links">
    """, unsafe_allow_html=True)
    
    # Create columns for navbar items - updated to include dashboard
    cols = st.columns([1, 1, 1, 1, 1, 1, 3])  # Added one more column
    
    # Home button
    with cols[0]:
        if st.button("🏠 Home", key="nav_home"):
            st.session_state.active_page = "home"
            st.experimental_rerun()
    
    # Login/Generate button
    with cols[1]:
        if st.session_state.logged_in:
            if st.button("🎓 Generate", key="nav_generate"):
                st.session_state.active_page = "generate"
                st.experimental_rerun()
        else:
            if st.button("🔑 Login", key="nav_login"):
                st.session_state.active_page = "login"
                st.experimental_rerun()
    
    # Dashboard button - only show if logged in
    with cols[2]:
        if st.session_state.logged_in:
            if st.button("📊 Dashboard", key="nav_dashboard"):
                st.session_state.active_page = "dashboard"
                st.experimental_rerun()
    
    # Verify button
    with cols[3]:
        if st.button("🔍 Verify", key="nav_verify"):
            st.session_state.active_page = "verify"
            st.experimental_rerun()
    
    # Scan QR button
    with cols[4]:
        if st.button("📱 Scan QR", key="nav_scan"):
            st.session_state.active_page = "scan_qr_code"
            st.experimental_rerun()
    
    # Register or Logout button
    with cols[5]:
        if st.session_state.logged_in:
            if st.button("🚪 Logout", key="nav_logout"):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.is_admin = False
                st.session_state.active_page = "home"
                st.experimental_rerun()
        else:
            if st.button("📝 Register", key="nav_register"):
                st.session_state.active_page = "register"
                st.experimental_rerun()
    
    # User info
    with cols[6]:  # Updated column index
        if st.session_state.logged_in:
            st.markdown(f"""
            <div style="text-align: right;">
                <span class="navbar-user">Welcome, {st.session_state.username} ({'Admin' if st.session_state.is_admin else 'User'})</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)
# Page functions
def home_page():
    st.markdown("""
    <div class="card">
        <h2>⛓ Welcome to CredX</h2>
        <p>A decentralized certificate verification system powered by blockchain technology</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card">
            <h3>🔍 About This System</h3>
            <p style="font-family: 'Courier New', monospace;">
            CredX uses blockchain technology to create tamper-proof digital certificates that can be instantly verified from anywhere in the world.
            </p>
            <ul style="font-family: 'Courier New', monospace;">
                <li>Generate secure, tamper-proof certificates</li>
                <li>Store certificate data on immutable blockchain</li>
                <li>Instant verification with QR code scanning</li>
                <li>Full credential management system</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Stats with icons
        st.markdown("""
        <div style="display: flex; justify-content: space-between; margin-top: 20px;">
            <div style="text-align: center; padding: 15px; background-color: #1a1a1a; border-radius: 5px; width: 30%;">
                <div style="font-size: 24px;">🔗</div>
                <div style="color: #00ffff;">100%</div>
                <div style="font-size: 12px; opacity: 0.7;">Tamper-proof</div>
            </div>
            <div style="text-align: center; padding: 15px; background-color: #1a1a1a; border-radius: 5px; width: 30%;">
                <div style="font-size: 24px;">🛡</div>
                <div style="color: #00ffff;">Secure</div>
                <div style="font-size: 12px; opacity: 0.7;">SHA-256 Encryption</div>
            </div>
            <div style="text-align: center; padding: 15px; background-color: #1a1a1a; border-radius: 5px; width: 30%;">
                <div style="font-size: 24px;">📊</div>
                <div style="color: #00ffff;">Instant</div>
                <div style="font-size: 12px; opacity: 0.7;">Verification</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3>🔍 Get Started</h3>
            <p>Select an option below to begin:</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.logged_in:
            login_col, register_col = st.columns(2)
            with login_col:
                if st.button("🔑 Login to Generate Certificates", key="home_login_btn"):
                    st.session_state.active_page = "login"
                    st.experimental_rerun()
            with register_col:
                if st.button("📝 Register Your Organization", key="home_register_btn"):
                    st.session_state.active_page = "register"
                    st.experimental_rerun()
        else:
            if st.button("🎓 Generate New Certificate", key="home_generate_btn"):
                st.session_state.active_page = "generate"
                st.experimental_rerun()
        
        verify_col, scan_col = st.columns(2)
        with verify_col:
            if st.button("🔍 Verify a Certificate", key="home_verify_btn"):
                st.session_state.active_page = "verify"
                st.experimental_rerun()
        with scan_col:
            if st.button("📱 Scan QR Code", key="home_scan_btn"):
                st.session_state.active_page = "scan_qr_code"
                st.experimental_rerun()

def login_page():
    st.markdown("""
    <div class="card">
        <h2>🔑 Login</h2>
        <p>Access your dashboard to generate and manage certificates</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submit_button = st.form_submit_button("🔑 Login")
            
            if submit_button:
                if username in st.session_state.users and st.session_state.users[username]['password'] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.is_admin = st.session_state.users[username]['is_admin']
                    st.session_state.active_page = "home"
                    st.success(f"Welcome {username}")
                    st.experimental_rerun()
                else:
                    st.error("Invalid username or password")
    
        st.markdown("""
        <div style="margin-top: 20px;">
            <p>Don't have an account?</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📝 Register Instead", key="login_register_btn"):
            st.session_state.active_page = "register"
            st.experimental_rerun()
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3>🔐 Demo Accounts</h3>
            <p>For testing purposes:</p>
            <ul>
                <li><strong>Admin:</strong> username: admin, password: admin</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def register_page():
    st.markdown("""
    <div class="card">
        <h2>📝 Register Your Organization</h2>
        <p>Fill out the form below to create an account and start issuing secure blockchain certificates.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.form(key='registration_form'):
            username = st.text_input("👤 Username")  # Added username field
            org_name = st.text_input("🏢 Organization Name")
            email = st.text_input("📧 Email Address")
            password = st.text_input("🔒 Password", type="password")
            confirm_password = st.text_input("🔁 Confirm Password", type="password")

            submitted = st.form_submit_button("✅ Register")

            if submitted:
                if not all([username, org_name, email, password, confirm_password]):  # Check username too
                    st.warning("Please fill in all the fields.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                elif username in st.session_state.users:  # Check username instead of org_name
                    st.error("Username already exists.")
                else:
                    # Save the new user with the username as the key
                    st.session_state.users[username] = {
                        'password': password,
                        'is_admin': False,
                        'email': email,
                        'organization': org_name  # Store org_name as part of user data
                    }
                    st.success(f"🎉 {username} has been registered successfully!")
                    st.session_state.active_page = "login"
                    st.experimental_rerun()
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3>🔒 Benefits of Registration</h3>
            <ul>
                <li>Generate blockchain-secured certificates</li>
                <li>Manage issued credentials</li>
                <li>Track certificate verification</li>
                <li>Establish trust and credibility</li>
            </ul>
            <p style="margin-top: 15px;">Already have an account?</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔑 Login Instead", key="register_login_btn"):
            st.session_state.active_page = "login"
            st.experimental_rerun()

def generate_page():
    if not st.session_state.logged_in:
        st.warning("Please login to generate certificates.")
        if st.button("🔑 Go to Login", key="gen_to_login"):
            st.session_state.active_page = "login"
            st.experimental_rerun()
        return
        
    st.markdown("""
    <div class="card">
        <h2>🎓 Generate Certificate</h2>
        <p>Fill in the student and course details below to generate a blockchain-secured certificate.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.form("generate_form"):
            cert_id = st.text_input("🎫 Certificate ID", 
                                   value=f"CERT{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
            student_name = st.text_input("👤 Student Name")
            course = st.text_input("📚 Course Name")
            contact = st.text_input("📞 Contact")
            address = st.text_input("🏠 Address")

            submitted = st.form_submit_button("Generate Certificate")

        if submitted:
            if not all([cert_id, student_name, course]):
                st.warning("Please fill in all required fields.")
            else:
                with st.spinner("Generating certificate..."):
                    cert_path, signature, ipfs_url = generate_certificate(cert_id, student_name, course, contact, address)

                    if cert_path:
                        st.success("✅ Certificate generated successfully!")
                        st.session_state.active_page = "view_certificate"
                        st.session_state.current_certificate = {
                            'path': cert_path,
                            'id': cert_id,
                            'name': student_name,
                            'course': course,
                            'signature': signature
                        }
                        st.experimental_rerun()
                    else:
                        st.error("Failed to generate certificate.")
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3>✨ Certificate Information</h3>
            <p>The generated certificate will include:</p>
            <ul>
                <li>Unique certificate ID</li>
                <li>Student name and course details</li>
                <li>QR code for easy verification</li>
                <li>Digital signature stored on blockchain</li>
                <li>Tamper-proof security features</li>
            </ul>
            <p style="margin-top: 15px;">All certificates are permanently stored on the blockchain for verification.</p>
        </div>
        """, unsafe_allow_html=True)

def view_certificate():
    if 'current_certificate' not in st.session_state:
        st.session_state.active_page = "home"
        st.experimental_rerun()
        return
        
    cert = st.session_state.current_certificate
    
    st.markdown(f"""
    <div class="card">
        <h2>🎓 Certificate Generated</h2>
        <p>Certificate for {cert['name']} has been successfully generated and stored on the blockchain.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.image(cert['path'], caption="Generated Certificate", use_column_width=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3>📋 Certificate Details</h3>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <ul>
                <li><strong>Certificate ID:</strong> {cert['id']}</li>
                <li><strong>Student Name:</strong> {cert['name']}</li>
                <li><strong>Course:</strong> {cert['course']}</li>
                <li><strong>Date Issued:</strong> {datetime.datetime.now().strftime('%Y-%m-%d')}</li>
                <li><strong>Issuer:</strong> {st.session_state.username}</li>
            </ul>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <h4>🔒 Digital Signature</h4>
        """, unsafe_allow_html=True)
        
        st.code(cert['signature'], language="plaintext")
        
        st.markdown("""
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🏠 Return to Home"):
            st.session_state.active_page = "home"
            st.experimental_rerun()
        
        if st.button("🎓 Generate Another Certificate"):
            st.session_state.active_page = "generate"
            st.experimental_rerun()

def verify_page():
    st.markdown("""
    <div class="card">
        <h2>🔍 Verify Certificate</h2>
        <p>Upload a certificate image or enter a certificate ID to verify its authenticity on the blockchain.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("<h3>Option 1: Upload Certificate</h3>", unsafe_allow_html=True)
        certificate_file = st.file_uploader("Upload Certificate Image", type=["png", "jpg", "jpeg"])
        
        if certificate_file:
            # In a real app, you would extract the certificate ID from the image
            # For this demo, we'll just show a verification message
            st.success("⌛ Processing certificate...")
            st.info("In a real app, this would extract the certificate ID from the image and verify it on the blockchain.")
            st.warning("For demo purposes, please use Option 2 to verify by ID.")
    
    with col2:
        st.markdown("<h3>Option 2: Enter Certificate ID</h3>", unsafe_allow_html=True)
        cert_id = st.text_input("Certificate ID")
        
        if st.button("Verify Certificate", key="verify_btn"):
            if cert_id:
                if verify_certificate_in_blockchain(cert_id):
                    cert_data = st.session_state.certificates[cert_id]
                    
                    st.success("✅ Certificate Verified")
                    st.markdown(f"""
                    <div style="background-color: #1a1a1a; padding: 15px; border-radius: 5px; margin-top: 15px;">
                        <h4 style="color: #00ff00;">Certificate Details</h4>
                        <ul style="list-style-type: none; padding-left: 0;">
                            <li><b>Certificate ID:</b> {cert_data['certificate_id']}</li>
                            <li><b>Student Name:</b> {cert_data['student_name']}</li>
                            <li><b>Course:</b> {cert_data['course']}</li>
                            <li><b>Issue Date:</b> {cert_data['issue_date']}</li>
                            <li><b>Status:</b> Valid</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("❌ Certificate could not be verified. It may be tampered or not on the blockchain.")
            else:
                st.warning("Please enter a certificate ID.")

def scan_qr_code_page():
    st.markdown("""
    <div class="card">
        <h2>📱 Scan QR Code</h2>
        <p>Use your camera to scan a certificate QR code for instant verification.</p>
    </div>
    """, unsafe_allow_html=True)
    
    rtc_configuration = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
    
    st.markdown("📸 Point your camera at a certificate QR code:")
    
    # Use a fixed key for the webrtc_streamer
    webrtc_ctx = webrtc_streamer(
        key="qr-scanner",
        video_processor_factory=VideoProcessor,
        rtc_configuration=rtc_configuration,
        media_stream_constraints={"video": True, "audio": False},
    )
    
    # Create a manual verification button as a fallback
    cert_id = st.text_input("Or enter Certificate ID manually:", key="manual_cert_id")
    if st.button("Verify Certificate ID"):
        st.session_state.qr_scanned = True
        st.session_state.qr_scan_result = cert_id
        st.experimental_rerun()
    
    # Display results if QR code was scanned
    if st.session_state.qr_scanned and st.session_state.qr_scan_result:
        qr_data = st.session_state.qr_scan_result
        st.success(f"QR Code Detected: {qr_data}")
        
        if verify_certificate_in_blockchain(qr_data):
            cert_data = st.session_state.certificates[qr_data]
            
            st.markdown(f"""
            <div style="background-color: #1a1a1a; padding: 15px; border-radius: 5px; margin-top: 15px;">
                <h4 style="color: #00ff00;">Certificate Details</h4>
                <ul style="list-style-type: none; padding-left: 0;">
                    <li><b>Certificate ID:</b> {cert_data['certificate_id']}</li>
                    <li><b>Student Name:</b> {cert_data['student_name']}</li>
                    <li><b>Course:</b> {cert_data['course']}</li>
                    <li><b>Issue Date:</b> {cert_data['issue_date']}</li>
                    <li><b>Status:</b> Valid</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ Certificate could not be verified. It may be tampered or not on the blockchain.")
        
        # Reset button
        if st.button("Scan Another QR Code"):
            st.session_state.qr_scanned = False
            st.session_state.qr_scan_result = ""
            st.experimental_rerun()
    
    st.markdown("""
    <div class="card" style="margin-top: 20px;">
        <h3>📱 How to Scan</h3>
        <ol>
            <li>Allow camera access when prompted</li>
            <li>Point your camera at a certificate QR code</li>
            <li>Hold steady until the code is detected</li>
            <li>View verification results instantly</li>
        </ol>
        <p><i>Note: If scanning doesn't work, you can enter the Certificate ID manually.</i></p>
    </div>
    """, unsafe_allow_html=True)
            
def certificate_management():
    if not st.session_state.logged_in:
        st.warning("Please login to access certificate management.")
        return
        
    st.markdown("""
    <div class="card">
        <h2>🔍 Certificate Management</h2>
        <p>View and manage all certificates issued by your organization.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filter certificates issued by the current user
    if st.session_state.is_admin:
        user_certificates = st.session_state.certificates
    else:
        # In real app, you'd filter by organization
        user_certificates = st.session_state.certificates
    
    if not user_certificates:
        st.info("No certificates have been issued yet.")
    else:
        st.markdown(f"### 📜 Total Certificates: {len(user_certificates)}")
        
        # Create a table of certificates
        cert_data = []
        for cert_id, cert in user_certificates.items():
            cert_data.append({
                "ID": cert_id,
                "Student": cert["student_name"],
                "Course": cert["course"],
                "Date Issued": cert["issue_date"]
            })
        
        st.table(cert_data)
        
        # Export options
        if st.button("📊 Export Certificate Data"):
            # In a real app, this would generate a CSV or JSON export
            st.success("Export functionality would go here.")
def dashboard_page():
    if not st.session_state.logged_in:
        st.warning("Please login to access the dashboard.")
        if st.button("🔑 Go to Login", key="dash_to_login"):
            st.session_state.active_page = "login"
            st.experimental_rerun()
        return
        
    st.markdown("""
    <div class="card">
        <h2>📊 Dashboard</h2>
        <p>View and manage your certificate statistics and activities.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filter certificates issued by the current user or organization
    if st.session_state.is_admin:
        user_certificates = st.session_state.certificates
    else:
        # In real app, you'd filter by organization
        user_certificates = st.session_state.certificates
    
    # Stats row
    st.markdown("<h3>📈 Statistics</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="dashboard-stat">
            <div class="dashboard-stat-value">{}</div>
            <div class="dashboard-stat-label">Certificates Issued</div>
        </div>
        """.format(len(user_certificates)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="dashboard-stat">
            <div class="dashboard-stat-value">0</div>
            <div class="dashboard-stat-label">Verification Requests</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="dashboard-stat">
            <div class="dashboard-stat-value">100%</div>
            <div class="dashboard-stat-label">Verification Success</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent Certificates
    st.markdown("<h3>🎓 Recent Certificates</h3>", unsafe_allow_html=True)
    
    if not user_certificates:
        st.info("No certificates have been issued yet.")
    else:
        # Display recent certificates using the new certificate-card style
        for cert_id, cert in list(user_certificates.items())[:3]:  # Show top 3
            st.markdown(f"""
            <div class="certificate-card">
                <h4>{cert['student_name']}</h4>
                <p><strong>Course:</strong> {cert['course']}</p>
                <p><strong>Date:</strong> {cert['issue_date']}</p>
                <p><strong>ID:</strong> {cert_id}</p>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("View All Certificates"):
            st.session_state.active_page = "certificate_management"
            st.experimental_rerun()
    
    # Certificate Generation
    st.markdown("<h3>🔧 Quick Actions</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("➕ Generate New Certificate", key="dashboard_gen"):
            st.session_state.active_page = "generate"
            st.experimental_rerun()
    
    with col2:
        if st.button("🔍 Verify Certificate", key="dashboard_verify"):
            st.session_state.active_page = "verify"
            st.experimental_rerun()

# Main layout
def main():
    # Render navbar
    render_navbar()
    
    # Main content area
    if st.session_state.active_page == "home":
        home_page()
    elif st.session_state.active_page == "login":
        login_page()
    elif st.session_state.active_page == "register":
        register_page()
    elif st.session_state.active_page == "generate":
        generate_page()
    elif st.session_state.active_page == "view_certificate":
        view_certificate()
    elif st.session_state.active_page == "verify":
        verify_page()
    elif st.session_state.active_page == "scan_qr_code":
        scan_qr_code_page()
    elif st.session_state.active_page == "certificate_management":
        certificate_management()
    elif st.session_state.active_page == "dashboard":  # Add this case
        dashboard_page()
    
    # Footer
    st.markdown("""
    <div style="margin-top: 50px; text-align: center; opacity: 0.7;">
        <p>🔐 CredX Blockchain Certificate System | Developed with Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()