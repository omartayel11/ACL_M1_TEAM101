"""
Developer console UI component
"""

import streamlit as st


def render_developer_console():
    """Render developer console with logs - terminal style"""
    if not st.session_state.dev_logs:
        st.info("👨‍💻 Developer Console\n\nNo logs yet. Start chatting to see system activity!")
    else:
        # Build terminal-style log HTML
        log_html = '<div class="dev-console-container">'
        log_html += '<div class="dev-console-header">👨‍💻 Developer Console</div>'
        log_html += '<div class="dev-console-logs">'
        
        # Show last 50 logs in reverse order (newest first)
        for log in reversed(st.session_state.dev_logs[-50:]):
            log_type = log['type'].lower()
            message = log['message']
            
            if log_type == 'terminal':
                # Terminal output - preserve exact formatting
                log_html += f'<div class="log-terminal">{message}</div>'
            else:
                # System messages - compact format
                css_class = f"log-{log_type}"
                
                # Format message with icon
                if log_type == 'error':
                    icon = '❌'
                elif log_type == 'success':
                    icon = '✅'
                elif log_type == 'user':
                    icon = '👤'
                elif log_type == 'system':
                    icon = '⚙️'
                else:
                    icon = '📋'
                
                log_html += f'<div class="dev-log-entry {css_class}">'
                log_html += f'{icon} {message}'
                log_html += '</div>'
        
        log_html += '</div></div>'
        st.markdown(log_html, unsafe_allow_html=True)
