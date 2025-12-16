"""
Custom CSS styles for the Streamlit application
Professional modern design with indigo/green/amber color scheme
"""

import streamlit as st


def apply_custom_styles():
    """Apply all custom CSS styles to the Streamlit app"""
    st.markdown("""
<style>
    /* ============================================
       PROFESSIONAL COLOR PALETTE & VARIABLES
       ============================================ */
    :root {
        --primary: #4F46E5;
        --primary-light: #6366F1;
        --primary-dark: #4338CA;
        --secondary: #10B981;
        --secondary-light: #34D399;
        --accent: #F59E0B;
        --accent-light: #FBBF24;
        --dark: #0F172A;
        --dark-light: #1E293B;
        --dark-lighter: #334155;
        --text-primary: #F1F5F9;
        --text-secondary: #CBD5E1;
        --text-muted: #94A3B8;
        --border: rgba(148, 163, 184, 0.2);
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
    }
    
    /* ============================================
       GLOBAL ANIMATIONS
       ============================================ */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 5px var(--hotel-glow); }
        50% { box-shadow: 0 0 20px var(--hotel-glow), 0 0 30px var(--hotel-glow); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* ============================================
       MAIN CONTAINER & BACKGROUND
       ============================================ */
    .main {
        background: linear-gradient(135deg, var(--dark) 0%, var(--dark-light) 100%);
        background-attachment: fixed;
        min-height: 100vh;
    }
    
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 50%, rgba(79, 70, 229, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(16, 185, 129, 0.05) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }
    
    .block-container {
        max-width: 100%;
        padding: 1.5rem 1rem;
        transition: all 0.3s ease;
    }
    
    /* Adjust container based on sidebar state */
    .main .block-container {
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* When sidebar is collapsed, use full width */
    [data-testid="collapsedControl"] ~ div .main .block-container {
        max-width: 1600px !important;
    }
    
    @media (min-width: 768px) {
        .block-container {
            padding: 1.75rem 1.5rem;
        }
    }
    
    @media (min-width: 1024px) {
        .block-container {
            padding: 2rem 2rem;
        }
    }
    
    @media (min-width: 1440px) {
        .block-container {
            padding: 2.5rem 2rem;
        }
    }
    
    /* ============================================
       CHAT MESSAGES - MODERN CARDS
       ============================================ */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.04);
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-sm);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeIn 0.4s ease-out;
        backdrop-filter: blur(8px);
    }
    
    .stChatMessage:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(148, 163, 184, 0.3);
    }
    
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, 
            rgba(79, 70, 229, 0.1) 0%, 
            rgba(79, 70, 229, 0.05) 100%);
        border-left: 3px solid var(--primary);
        animation: slideInLeft 0.4s ease-out;
    }
    
    .stChatMessage[data-testid="user-message"]:hover {
        background: linear-gradient(135deg, 
            rgba(79, 70, 229, 0.15) 0%, 
            rgba(79, 70, 229, 0.08) 100%);
        box-shadow: 0 4px 16px rgba(79, 70, 229, 0.2);
    }
    
    .stChatMessage[data-testid="assistant-message"] {
        background: linear-gradient(135deg, 
            rgba(16, 185, 129, 0.1) 0%, 
            rgba(16, 185, 129, 0.05) 100%);
        border-left: 3px solid var(--secondary);
        animation: slideInRight 0.4s ease-out;
    }
    
    .stChatMessage[data-testid="assistant-message"]:hover {
        background: linear-gradient(135deg, 
            rgba(16, 185, 129, 0.15) 0%, 
            rgba(16, 185, 129, 0.08) 100%);
        box-shadow: 0 4px 16px rgba(16, 185, 129, 0.2);
    }
    
    /* ============================================
       SIDEBAR - MODERN PROFESSIONAL & RESPONSIVE
       ============================================ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, 
            var(--dark) 0%, 
            var(--dark-light) 100%) !important;
        border-right: 1px solid var(--border);
        box-shadow: var(--shadow-lg);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    [data-testid="stSidebar"] > div {
        padding: 1.5rem 1rem;
    }
    
    /* Sidebar collapse button styling */
    [data-testid="collapsedControl"] {
        background: linear-gradient(135deg, var(--primary) 0%, #6366F1 100%) !important;
        color: white !important;
        border-radius: 0 8px 8px 0 !important;
        padding: 0.75rem 0.5rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(79, 70, 229, 0.3) !important;
    }
    
    [data-testid="collapsedControl"]:hover {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.5) !important;
    }
    
    @media (min-width: 768px) {
        [data-testid="stSidebar"] > div {
            padding: 2rem 1.5rem;
        }
    }
    
    @media (max-width: 1024px) {
        [data-testid="stSidebar"] {
            width: 280px !important;
        }
    }
    
    /* ============================================
       PROFESSIONAL TYPOGRAPHY
       ============================================ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    
    h1 {
        font-size: clamp(2rem, 5vw, 2.5rem) !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        font-size: clamp(1.5rem, 4vw, 2rem) !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }
    
    h3 {
        font-size: clamp(1.25rem, 3vw, 1.5rem) !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
        font-weight: 600 !important;
    }
    
    h4 {
        font-size: clamp(1.1rem, 2.5vw, 1.25rem) !important;
        font-weight: 600 !important;
    }
    
    p, .stMarkdown {
        color: var(--text-secondary);
        line-height: 1.7;
        font-size: clamp(0.9rem, 2vw, 1rem);
        font-weight: 400;
    }
    
    @media (max-width: 768px) {
        h1 { font-size: 1.75rem !important; }
        h2 { font-size: 1.5rem !important; }
        h3 { font-size: 1.25rem !important; }
    }
    
    /* ============================================
       BUTTONS - MODERN DESIGN SYSTEM
       ============================================ */
    .stButton>button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        font-weight: 600;
        font-size: 0.9rem;
        border-radius: 8px;
        border: none;
        padding: 0.65rem 1.5rem;
        transition: all 0.2s ease;
        box-shadow: var(--shadow-sm);
        text-transform: none;
        letter-spacing: 0;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        background: linear-gradient(135deg, var(--primary-light) 0%, var(--primary) 100%);
    }
    
    .stButton>button:active {
        transform: translateY(0);
        box-shadow: var(--shadow-sm);
    }
    
    .stButton>button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid var(--border);
        color: var(--text-primary);
    }
    
    .stButton>button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(148, 163, 184, 0.3);
    }
    
    /* Responsive button sizing */
    @media (max-width: 768px) {
        .stButton>button {
            padding: 0.5rem 1.25rem;
            font-size: 0.85rem;
        }
    }
    
    @media (max-width: 640px) {
        .stButton>button {
            padding: 0.5rem 1rem;
            font-size: 0.8rem;
        }
    }
    
    /* ============================================
       SELECT BOXES & INPUTS
       ============================================ */
    .stSelectbox>div>div {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        color: white;
        border: 1px solid rgba(255, 215, 0, 0.2);
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    .stSelectbox>div>div:hover {
        background: rgba(255, 255, 255, 0.12);
        border-color: rgba(79, 70, 229, 0.4);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15);
    }
    
    .stSelectbox>div>div:focus-within {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
    }
    
    .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.08);
        color: white;
        border-radius: 12px;
        border: 1px solid rgba(255, 215, 0, 0.2);
        padding: 0.75rem 1rem;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    .stTextInput>div>div>input:hover {
        background: rgba(255, 255, 255, 0.12);
        border-color: rgba(79, 70, 229, 0.4);
    }
    
    .stTextInput>div>div>input:focus {
        background: rgba(255, 255, 255, 0.12);
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
        outline: none;
    }
    
    /* ============================================
       EXPANDERS
       ============================================ */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, 
            rgba(79, 70, 229, 0.1) 0%, 
            rgba(79, 70, 229, 0.05) 100%);
        border-radius: 12px;
        color: var(--primary);
        font-weight: 600;
        padding: 1rem 1.25rem;
        border: 1px solid rgba(79, 70, 229, 0.2);
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, 
            rgba(79, 70, 229, 0.15) 0%, 
            rgba(255, 215, 0, 0.08) 100%);
        box-shadow: 0 4px 12px rgba(255, 215, 0, 0.15);
        transform: translateY(-1px);
    }
    
    .streamlit-expanderContent {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 0 0 12px 12px;
        padding: 1.25rem;
        border: 1px solid rgba(255, 215, 0, 0.1);
        border-top: none;
        margin-top: -1px;
    }
    
    /* ============================================
       METRICS
       ============================================ */
    .stMetric {
        background: linear-gradient(135deg, 
            rgba(79, 70, 229, 0.08) 0%, 
            rgba(16, 185, 129, 0.05) 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
        animation: fadeIn 0.5s ease-out;
    }
    
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        border-color: rgba(79, 70, 229, 0.3);
    }
    
    .stMetric label {
        color: var(--text-secondary);
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: var(--primary);
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    /* ============================================
       CHAT INPUT - PROFESSIONAL TEXT INPUT DESIGN
       ============================================ */
    .stChatFloatingInputContainer {
        background: linear-gradient(180deg, 
            transparent 0%, 
            rgba(15, 23, 42, 0.4) 30%, 
            rgba(15, 23, 42, 0.8) 100%) !important;
        backdrop-filter: blur(10px) !important;
        padding: 1rem 0 !important;
        border: none !important;
        border-top: 1px solid rgba(148, 163, 184, 0.1) !important;
        box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.3) !important;
        position: sticky !important;
        bottom: 0 !important;
        z-index: 100 !important;
    }
    
    .stChatInput {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        box-shadow: none !important;
        max-width: 1800px !important;
        margin: 0 auto !important;
    }
    
    .stChatInput > div {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        gap: 0.75rem !important;
    }
    
    /* Chat input wrapper - creates the input box look */
    .stChatInput > div > div:first-child {
        flex: 1 !important;
        position: relative !important;
        background: linear-gradient(135deg, 
            rgba(255, 255, 255, 0.1) 0%, 
            rgba(255, 255, 255, 0.05) 100%) !important;
        border: 2px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 14px !important;
        box-shadow: 
            0 4px 12px rgba(0, 0, 0, 0.2),
            inset 0 1px 2px rgba(255, 255, 255, 0.1) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        overflow: hidden !important;
    }
    
    .stChatInput > div > div:first-child:hover {
        background: linear-gradient(135deg, 
            rgba(255, 255, 255, 0.12) 0%, 
            rgba(255, 255, 255, 0.06) 100%) !important;
        border-color: rgba(79, 70, 229, 0.4) !important;
        box-shadow: 
            0 4px 16px rgba(79, 70, 229, 0.2),
            inset 0 1px 2px rgba(255, 255, 255, 0.15) !important;
    }
    
    .stChatInput > div > div:first-child:focus-within {
        background: linear-gradient(135deg, 
            rgba(255, 255, 255, 0.14) 0%, 
            rgba(255, 255, 255, 0.08) 100%) !important;
        border-color: var(--primary) !important;
        box-shadow: 
            0 0 0 4px rgba(79, 70, 229, 0.15),
            0 6px 20px rgba(79, 70, 229, 0.3),
            inset 0 1px 3px rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Chat input textarea - clean text field */
    .stChatInput textarea {
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        color: #F8FAFC !important;
        padding: 1.375rem 1.75rem !important;
        font-size: 1.1rem !important;
        line-height: 1.5 !important;
        transition: all 0.2s ease !important;
        box-shadow: none !important;
        min-height: 70px !important;
        max-height: 70px !important;
        height: 70px !important;
        resize: none !important;
        overflow-y: hidden !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 400 !important;
    }
    
    .stChatInput textarea::placeholder {
        color: rgba(203, 213, 225, 0.5) !important;
        font-weight: 400 !important;
    }
    
    .stChatInput textarea:focus {
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* Scrollbar for textarea */
    .stChatInput textarea::-webkit-scrollbar {
        width: 4px !important;
    }
    
    .stChatInput textarea::-webkit-scrollbar-track {
        background: transparent !important;
    }
    
    .stChatInput textarea::-webkit-scrollbar-thumb {
        background: rgba(148, 163, 184, 0.3) !important;
        border-radius: 2px !important;
    }
    
    /* Send button styling - modern and prominent */
    .stChatInput button[kind="primary"],
    .stChatInput button[type="submit"] {
        background: linear-gradient(135deg, 
            var(--primary) 0%, 
            #6366F1 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0 2.25rem !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        min-height: 70px !important;
        height: 70px !important;
        cursor: pointer !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 
            0 4px 12px rgba(79, 70, 229, 0.4),
            inset 0 1px 2px rgba(255, 255, 255, 0.2) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0.5rem !important;
        text-transform: none !important;
        letter-spacing: 0.01em !important;
    }
    
    .stChatInput button[kind="primary"]:hover,
    .stChatInput button[type="submit"]:hover {
        background: linear-gradient(135deg, 
            #6366F1 0%, 
            #8B5CF6 100%) !important;
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 
            0 6px 20px rgba(79, 70, 229, 0.5),
            inset 0 1px 2px rgba(255, 255, 255, 0.3) !important;
    }
    
    .stChatInput button[kind="primary"]:active,
    .stChatInput button[type="submit"]:active {
        transform: translateY(0px) scale(1) !important;
        box-shadow: 
            0 2px 8px rgba(79, 70, 229, 0.4),
            inset 0 1px 2px rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Send button icon */
    .stChatInput button svg {
        width: 18px !important;
        height: 18px !important;
        fill: currentColor !important;
        filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.2)) !important;
    }
    
    /* ============================================
       ALERTS & NOTIFICATIONS
       ============================================ */
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: var(--shadow-sm);
        animation: fadeIn 0.4s ease-out;
    }
    
    [data-testid="stNotificationContentInfo"] {
        background: linear-gradient(135deg, 
            rgba(79, 70, 229, 0.15) 0%, 
            rgba(79, 70, 229, 0.08) 100%);
        border-left: 3px solid var(--primary);
    }
    
    [data-testid="stNotificationContentSuccess"] {
        background: linear-gradient(135deg, 
            rgba(16, 185, 129, 0.15) 0%, 
            rgba(16, 185, 129, 0.08) 100%);
        border-left: 3px solid var(--secondary);
    }
    
    [data-testid="stNotificationContentError"] {
        background: linear-gradient(135deg, 
            rgba(239, 68, 68, 0.15) 0%, 
            rgba(239, 68, 68, 0.08) 100%);
        border-left: 3px solid #EF4444;
    }
    
    [data-testid="stNotificationContentWarning"] {
        background: linear-gradient(135deg, 
            rgba(251, 191, 36, 0.15) 0%, 
            rgba(251, 191, 36, 0.08) 100%);
        border-left: 3px solid var(--accent);
    }
    
    /* ============================================
       HOTEL CARDS - MODERN DESIGN
       ============================================ */
    .hotel-card {
        background: linear-gradient(135deg, 
            rgba(30, 41, 59, 0.95) 0%, 
            rgba(15, 23, 42, 0.95) 100%);
        border: 2px solid rgba(79, 70, 229, 0.3);
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeIn 0.5s ease-out;
        box-shadow: 
            0 8px 24px rgba(0, 0, 0, 0.4),
            inset 0 1px 2px rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(12px);
        position: relative;
        overflow: hidden;
    }
    
    .hotel-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, 
            var(--primary) 0%, 
            var(--secondary) 50%, 
            var(--accent) 100%);
    }
    
    .hotel-card:hover {
        transform: translateY(-6px);
        box-shadow: 
            0 12px 32px rgba(79, 70, 229, 0.4),
            inset 0 1px 3px rgba(255, 255, 255, 0.15);
        border-color: rgba(79, 70, 229, 0.6);
        background: linear-gradient(135deg, 
            rgba(30, 41, 59, 1) 0%, 
            rgba(15, 23, 42, 1) 100%);
    }
    
    .hotel-card-header {
        display: flex;
        justify-content: space-between;
        align-items: start;
        margin-bottom: 1.5rem;
        gap: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.15);
    }
    
    .hotel-card-title {
        color: var(--text-primary);
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
        line-height: 1.3;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .hotel-card-rating {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        background: linear-gradient(135deg, 
            var(--accent) 0%, 
            var(--accent-light) 100%);
        padding: 0.5rem 1.1rem;
        border-radius: 24px;
        font-weight: 700;
        font-size: 1rem;
        color: var(--dark);
        box-shadow: 
            0 4px 12px rgba(245, 158, 11, 0.4),
            inset 0 1px 2px rgba(255, 255, 255, 0.3);
        white-space: nowrap;
    }
    
    .hotel-card-location {
        color: var(--text-secondary);
        font-size: 1.05rem;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.65rem;
        font-weight: 500;
    }
    
    .hotel-card-description {
        color: var(--text-secondary);
        font-size: 0.95rem;
        line-height: 1.7;
        margin: 1.25rem 0;
        padding: 1.25rem;
        background: rgba(79, 70, 229, 0.08);
        border-radius: 10px;
        border-left: 4px solid var(--primary);
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
    }
    
    .hotel-card-amenities {
        display: flex;
        flex-wrap: wrap;
        gap: 0.65rem;
        margin: 1.25rem 0;
        padding: 1rem;
        background: rgba(0, 0, 0, 0.15);
        border-radius: 10px;
    }
    
    .amenity-tag {
        background: rgba(16, 185, 129, 0.15);
        border: 1.5px solid rgba(16, 185, 129, 0.4);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        color: var(--secondary);
        font-weight: 600;
        transition: all 0.2s ease;
        box-shadow: 0 2px 6px rgba(16, 185, 129, 0.2);
    }
    
    .amenity-tag:hover {
        background: rgba(16, 185, 129, 0.25);
        transform: scale(1.05);
        border-color: rgba(16, 185, 129, 0.6);
        box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3);
    }
    
    .hotel-card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(148, 163, 184, 0.15);
    }
    
    .hotel-card-price {
        color: var(--secondary);
        font-size: 1.75rem;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
    }
    
    .hotel-card-price-label {
        color: var(--text-muted);
        font-size: 0.85rem;
        margin-left: 0.35rem;
        font-weight: 500;
    }
    
    .hotel-cards-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
        gap: 1.5rem;
        margin: 1.5rem 0;
    }
    
    @media (max-width: 768px) {
        .hotel-cards-grid {
            grid-template-columns: 1fr;
        }
        .hotel-card-header {
            flex-direction: column;
        }
    }
    
    /* ============================================
       DEVELOPER CONSOLE
       ============================================ */
    .dev-console-container {
        position: sticky;
        top: 100px;
        height: calc(100vh - 200px);
        background: linear-gradient(135deg, 
            rgba(15, 20, 30, 0.95) 0%, 
            rgba(20, 25, 35, 0.95) 100%);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        box-shadow: var(--shadow-lg);
        backdrop-filter: blur(8px);
        animation: slideInRight 0.5s ease-out;
    }
    
    .dev-console-header {
        padding: 1rem 1.25rem;
        background: linear-gradient(135deg, 
            rgba(79, 70, 229, 0.12) 0%, 
            rgba(16, 185, 129, 0.08) 100%);
        border-bottom: 2px solid var(--primary);
        font-weight: 600;
        font-size: 0.95rem;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .dev-console-logs {
        flex: 1;
        overflow-y: auto;
        padding: 1.25rem;
        font-family: 'SF Mono', 'Consolas', 'Monaco', monospace;
        font-size: 0.85rem;
        line-height: 1.6;
        background: rgba(0, 0, 0, 0.2);
    }
    
    .dev-log-entry {
        margin: 0.5rem 0;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        border-left: 4px solid;
        transition: all 0.2s ease;
        animation: fadeIn 0.3s ease-out;
    }
    
    .dev-log-entry:hover {
        transform: translateX(4px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    
    .log-user { 
        border-left-color: var(--primary); 
        background: linear-gradient(90deg, 
            rgba(79, 70, 229, 0.08) 0%, 
            rgba(79, 70, 229, 0.02) 100%);
        color: var(--primary-light);
    }
    
    .log-system { 
        border-left-color: var(--secondary); 
        background: linear-gradient(90deg, 
            rgba(16, 185, 129, 0.08) 0%, 
            rgba(16, 185, 129, 0.02) 100%);
        color: #10B981;
    }
    
    .log-success { 
        border-left-color: var(--secondary); 
        background: linear-gradient(90deg, 
            rgba(16, 185, 129, 0.08) 0%, 
            rgba(16, 185, 129, 0.02) 100%);
        color: #10B981;
    }
    
    .log-error { 
        border-left-color: #EF4444; 
        background: linear-gradient(90deg, 
            rgba(239, 68, 68, 0.08) 0%, 
            rgba(239, 68, 68, 0.02) 100%);
        color: #F87171;
    }
    
    .log-output { 
        border-left-color: var(--text-tertiary); 
        background: linear-gradient(90deg, 
            rgba(148, 163, 184, 0.08) 0%, 
            rgba(148, 163, 184, 0.02) 100%);
        color: var(--text-secondary);
    }
    
    .log-terminal {
        border-left: none;
        background: rgba(0, 0, 0, 0.3);
        color: #ECF0F1;
        padding: 1rem;
        margin: 0.5rem 0;
        white-space: pre-wrap;
        font-family: 'SF Mono', 'Consolas', 'Monaco', monospace;
        font-size: 0.8rem;
        line-height: 1.6;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .dev-console-logs::-webkit-scrollbar {
        width: 8px;
    }
    
    .dev-console-logs::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 4px;
    }
    
    .dev-console-logs::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, 
            rgba(79, 70, 229, 0.5) 0%, 
            rgba(79, 70, 229, 0.3) 100%);
        border-radius: 4px;
        transition: all 0.3s ease;
    }
    
    .dev-console-logs::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, 
            rgba(79, 70, 229, 0.7) 0%, 
            rgba(79, 70, 229, 0.5) 100%);
    }
    
    /* ============================================
       MISC
       ============================================ */
    .chat-area-marker {
        display: none;
    }
    
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, 
            transparent 0%, 
            var(--border) 50%, 
            transparent 100%);
        margin: 1.5rem 0;
        animation: fadeIn 0.5s ease-out;
    }
    
    .stSpinner > div {
        border-color: var(--primary) transparent transparent transparent !important;
        animation: spin 1s linear infinite, pulse 2s ease-in-out infinite !important;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* ============================================
       RESPONSIVE DESIGN IMPROVEMENTS
       ============================================ */
    
    /* Tablet and below */
    @media (max-width: 1024px) {
        .block-container {
            max-width: 100% !important;
        }
        
        .stChatInput {
            max-width: 100% !important;
            padding: 0 1rem !important;
        }
    }
    
    /* Mobile landscape and below */
    @media (max-width: 768px) {
        .block-container {
            padding: 1rem 0.75rem;
        }
        
        [data-testid="stSidebar"] {
            width: 260px !important;
        }
        
        /* Stack columns on mobile */
        [data-testid="column"] {
            width: 100% !important;
            min-width: 100% !important;
            flex: 100% !important;
        }
        
        /* Adjust toolbar tabs for mobile */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.35rem !important;
            flex-wrap: nowrap;
            overflow-x: auto;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0 1rem !important;
            font-size: 0.85rem !important;
            white-space: nowrap;
            min-width: auto !important;
        }
        
        /* Make chat input smaller on mobile */
        .stChatInput textarea {
            min-height: 50px !important;
            max-height: 50px !important;
            height: 50px !important;
            font-size: 0.95rem !important;
        }
        
        .stChatInput button {
            min-height: 50px !important;
            height: 50px !important;
            padding: 0 1.25rem !important;
        }
    }
    
    /* Mobile portrait */
    @media (max-width: 640px) {
        h1 {
            font-size: 1.5rem !important;
        }
        
        h2 {
            font-size: 1.25rem !important;
        }
        
        h3 {
            font-size: 1.1rem !important;
        }
        
        .stMetric {
            padding: 0.75rem;
        }
        
        .stMetric [data-testid="stMetricValue"] {
            font-size: 1.25rem;
        }
        
        /* Further reduce tab sizes on small screens */
        .stTabs [data-baseweb="tab"] {
            padding: 0 0.75rem !important;
            font-size: 0.8rem !important;
            height: 42px !important;
        }
        
        /* Hide sidebar by default on mobile */
        [data-testid="stSidebar"] {
            width: 240px !important;
        }
        
        /* Make feature cards stack on mobile */
        [data-testid="column"] {
            margin-bottom: 1rem;
        }
    }
    
    /* Large desktop - utilize full width when sidebar is collapsed */
    @media (min-width: 1440px) {
        /* When sidebar is open */
        .main .block-container {
            max-width: 1500px;
        }
        
        /* When sidebar is collapsed */
        [data-testid="collapsedControl"] ~ div .main .block-container {
            max-width: 1800px !important;
        }
    }
    
    @media (min-width: 1920px) {
        /* Ultra-wide monitors */
        [data-testid="collapsedControl"] ~ div .main .block-container {
            max-width: 2000px !important;
        }
    }
</style>
""", unsafe_allow_html=True)
