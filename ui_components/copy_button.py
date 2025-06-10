"""
Copy Button Component for Streamlit
Provides an easy way to copy text to clipboard
"""

import streamlit as st
import streamlit.components.v1 as components

def copy_button(text_to_copy: str, button_text: str = "📋 Copy", key: str = None):
    """
    Creates a button that copies text to clipboard when clicked
    
    Args:
        text_to_copy: The text that will be copied
        button_text: Text to display on the button
        key: Unique key for the component
    """
    if key is None:
        key = f"copy_btn_{hash(text_to_copy[:50])}"
    
    # Create a unique key for the text area
    text_key = f"{key}_text"
    
    # Use columns to create a compact layout
    col1, col2 = st.columns([5, 1])
    
    with col1:
        # Show the text in a disabled text area (read-only)
        st.text_area(
            "Click to select all (Ctrl+A), then copy (Ctrl+C)",
            value=text_to_copy,
            height=200,
            key=text_key,
            disabled=False,  # Keep enabled so user can select
            label_visibility="visible"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        # Add copy instructions
        st.info("👆 Select all\n(Ctrl+A)\nthen copy\n(Ctrl+C)")
    
    return text_key


def copy_to_clipboard_button(text: str, label: str = "📋 Copy to Clipboard", key: str = None):
    """
    Alternative implementation using JavaScript for direct clipboard copy
    """
    if key is None:
        key = f"clipboard_{hash(text[:50])}"
    
    # Escape the text for JavaScript
    escaped_text = text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
    
    # HTML and JavaScript for copy functionality
    copy_button_html = f"""
    <style>
    .copy-button {{
        background-color: #0066CC;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        margin: 10px 0;
    }}
    .copy-button:hover {{
        background-color: #0051A2;
    }}
    .copy-success {{
        color: #28A745;
        font-size: 12px;
        margin-left: 10px;
    }}
    </style>
    <div>
        <button class="copy-button" onclick="copyToClipboard_{key}()">{label}</button>
        <span id="copy-success-{key}" class="copy-success" style="display: none;">✓ Copied!</span>
    </div>
    <script>
    function copyToClipboard_{key}() {{
        const text = "{escaped_text}";
        navigator.clipboard.writeText(text).then(function() {{
            document.getElementById('copy-success-{key}').style.display = 'inline';
            setTimeout(function() {{
                document.getElementById('copy-success-{key}').style.display = 'none';
            }}, 2000);
        }}, function(err) {{
            // Fallback for older browsers
            const textArea = document.createElement("textarea");
            textArea.value = text;
            textArea.style.position = "fixed";
            textArea.style.left = "-999999px";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {{
                document.execCommand('copy');
                document.getElementById('copy-success-{key}').style.display = 'inline';
                setTimeout(function() {{
                    document.getElementById('copy-success-{key}').style.display = 'none';
                }}, 2000);
            }} catch (err) {{
                console.error('Failed to copy text: ', err);
            }}
            document.body.removeChild(textArea);
        }});
    }}
    </script>
    """
    
    components.html(copy_button_html, height=50)


def error_display_with_copy(error_title: str, error_text: str, key: str = None):
    """
    Display an error with an easy copy button
    """
    st.error(f"❌ **{error_title}**")
    
    # Create markdown code block
    error_markdown = f"```\n{error_text}\n```"
    st.markdown(error_markdown)
    
    # Add copy button
    st.markdown("**To copy this error:**")
    copy_button(error_text, key=key)