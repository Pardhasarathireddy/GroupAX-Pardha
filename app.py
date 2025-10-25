"""
AI Developer Ops Agent - Streamlit UI
"""
import streamlit as st
import os
from dotenv import load_dotenv
import time
from datetime import datetime

from utils.github_helper import GitHubHelper
from agents.analyzer import CodeAnalyzer
from agents.doc_generator import DocGenerator

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Developer Ops Agent",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# Header
st.title("🤖 AI Developer Ops Agent")
st.markdown("**Autonomous code analysis and improvement powered by Gemini Flash 2.5**")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    google_api_key = st.text_input(
        "Google API Key",
        value=os.getenv("GOOGLE_API_KEY", ""),
        type="password"
    )
    
    github_token = st.text_input(
        "GitHub Token",
        value=os.getenv("GITHUB_TOKEN", ""),
        type="password"
    )
    
    st.markdown("---")
    st.markdown("### 📊 Features")
    st.markdown("""
    - ✅ Code quality analysis
    - ✅ Documentation generation
    - ✅ Security vulnerability detection
    - ✅ Autonomous PR creation
    """)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    repo_url = st.text_input(
        "Enter GitHub Repository URL",
        placeholder="https://github.com/username/repo",
        help="Public repository URL to analyze"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = st.button("🔍 Analyze Repository", type="primary", use_container_width=True)

# Analysis workflow
if analyze_btn and repo_url:
    if not google_api_key or not github_token:
        st.error("⚠️ Please provide API keys in the sidebar")
    else:
        # Initialize helpers
        github_helper = GitHubHelper(github_token)
        analyzer = CodeAnalyzer(google_api_key)
        doc_gen = DocGenerator(google_api_key)
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Fetch repository
            status_text.text("📥 Fetching repository files...")
            progress_bar.progress(20)
            files = github_helper.get_repo_files(repo_url, max_files=30)
            
            if not files:
                st.error("❌ Could not fetch repository files. Check the URL and token permissions.")
            else:
                st.success(f"✅ Fetched {len(files)} files")
                
                # Step 2: Analyze code
                status_text.text("🔍 Analyzing code quality...")
                progress_bar.progress(40)
                time.sleep(0.5)  # Visual feedback
                
                analysis = analyzer.analyze_repository(files)
                
                progress_bar.progress(60)
                st.success("✅ Analysis complete")
                
                # Step 3: Generate documentation
                status_text.text("📝 Generating documentation improvements...")
                progress_bar.progress(80)
                
                repo_structure = github_helper.get_repo_structure(repo_url)
                updated_files = doc_gen.generate_missing_docstrings(files, repo_structure)
                
                progress_bar.progress(100)
                status_text.text("✅ All done!")
                
                # Store results
                st.session_state.analysis_results = {
                    'analysis': analysis,
                    'updated_files': updated_files,
                    'total_files': len(files)
                }
                st.session_state.analysis_complete = True
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            progress_bar.empty()
            status_text.empty()

# Display results
if st.session_state.analysis_complete and st.session_state.analysis_results:
    st.markdown("---")
    st.header("📊 Analysis Results")
    
    results = st.session_state.analysis_results
    analysis = results['analysis']
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Files Analyzed",
            results['total_files']
        )
    
    with col2:
        doc_issues = len(analysis.get('documentation_issues', []))
        st.metric(
            "Documentation Issues",
            doc_issues,
            delta=f"-{len(results['updated_files'])} fixed" if results['updated_files'] else None
        )
    
    with col3:
        code_issues = len(analysis.get('code_quality_issues', []))
        st.metric(
            "Code Quality Issues",
            code_issues
        )
    
    with col4:
        security_issues = len(analysis.get('security_issues', []))
        st.metric(
            "Security Issues",
            security_issues,
            delta="⚠️" if security_issues > 0 else "✅"
        )
    
    # Detailed issues
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Documentation",
        "🔧 Code Quality",
        "🔒 Security",
        "⚡ Performance"
    ])
    
    with tab1:
        doc_issues_list = analysis.get('documentation_issues', [])
        if doc_issues_list:
            for issue in doc_issues_list:
                st.warning(f"**{issue.get('file', 'Unknown')}**: {issue.get('issue', 'No description')}")
        else:
            st.success("✅ No documentation issues found!")
    
    with tab2:
        quality_issues = analysis.get('code_quality_issues', [])
        if quality_issues:
            for issue in quality_issues:
                st.info(f"**{issue.get('file', 'Unknown')}**: {issue.get('issue', 'No description')}")
        else:
            st.success("✅ No code quality issues found!")
    
    with tab3:
        sec_issues = analysis.get('security_issues', [])
        if sec_issues:
            for issue in sec_issues:
                st.error(f"**{issue.get('file', 'Unknown')}**: {issue.get('issue', 'No description')}")
        else:
            st.success("✅ No security issues found!")
    
    with tab4:
        perf_issues = analysis.get('performance_issues', [])
        if perf_issues:
            for issue in perf_issues:
                st.warning(f"**{issue.get('file', 'Unknown')}**: {issue.get('issue', 'No description')}")
        else:
            st.success("✅ No performance issues found!")
    
    # Auto-fix section
    if results['updated_files']:
        st.markdown("---")
        st.header("🤖 Autonomous Fixes Generated")
        
        st.info(f"✨ Generated improvements for {len(results['updated_files'])} files")
        
        # Preview fixes
        with st.expander("Preview generated documentation"):
            for filepath, content in list(results['updated_files'].items())[:3]:
                st.code(content[:500] + "..." if len(content) > 500 else content, language="python")
        
        # Create PR button
        st.markdown("### Create Pull Request")
        pr_title = st.text_input("PR Title", value="🤖 AI Agent: Documentation improvements")
        
        if st.button("✨ Create Pull Request", type="primary"):
            with st.spinner("Creating pull request..."):
                try:
                    github_helper = GitHubHelper(github_token)
                    branch_name = f"ai-agent-docs-{int(time.time())}"
                    
                    pr_url = github_helper.create_pull_request(
                        repo_url=repo_url,
                        branch_name=branch_name,
                        files_to_update=results['updated_files'],
                        pr_title=pr_title,
                        pr_body=f"""
## 🤖 AI-Generated Improvements

This PR was automatically created by the AI Developer Ops Agent.

### Changes Made:
- ✅ Added missing docstrings ({len(results['updated_files'])} files)
- ✅ Improved code documentation
- ✅ Enhanced readability

### Analysis Summary:
- **Files analyzed**: {results['total_files']}
- **Documentation issues**: {len(analysis.get('documentation_issues', []))}
- **Code quality issues**: {len(analysis.get('code_quality_issues', []))}

Generated with ❤️ by Gemini Flash 2.5
                        """
                    )
                    
                    if pr_url:
                        st.success(f"✅ Pull request created successfully!")
                        st.markdown(f"[View PR]({pr_url})")
                    else:
                        st.error("❌ Failed to create pull request")
                        
                except Exception as e:
                    st.error(f"❌ Error creating PR: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Powered by Google Gemini Flash 2.5 🚀 | Built for GenAIVersity Hackathon 2025</p>
</div>
""", unsafe_allow_html=True)
