import streamlit as st
import os
from dotenv import load_dotenv
import time
from datetime import datetime
import plotly.graph_objects as go

from utils.github_helper import GitHubHelper
from agents.deep_analyzer import DeepCodeAnalyzer
from agents.doc_generator import DocGenerator
from utils.history_manager import HistoryManager

load_dotenv()

st.set_page_config(
    page_title="AI DevOps Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'history_manager' not in st.session_state:
    st.session_state.history_manager = HistoryManager()
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header {visibility: hidden;}
.main { background: #fff; }
[data-testid="stSidebar"] {
    background-color: #f9fafb !important;
    border-right: 1px solid #e5e7eb !important;
}
.stTextInput > div > div > input {
    border-radius: 12px; border: 1px solid #e5e7eb;
    padding: 0.75rem 1rem; font-size: 0.95rem;
}
.stButton > button {
    background: #111827; color: white;
    border-radius: 12px; padding: 0.75rem 2rem;
    font-weight: 500; border: none;
}
.stButton > button:hover {background: #374151;}
[data-testid="stMetricValue"] { font-size: 1.75rem; font-weight: 600; }
.stTabs [data-baseweb="tab"] {
    border-radius: 8px; padding: 0.5rem 1rem;
    font-weight: 500; color: #6b7280;
}
.stTabs [aria-selected="true"] {
    background: #111827; color: white;
}
.streamlit-expanderHeader { background: #f9fafb; border-radius: 8px;}
</style>
""", unsafe_allow_html=True)

def load_icon():
    try:
        with open('icon.svg', 'r') as f:
            return f.read()
    except:
        return None

icon_svg = load_icon()

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if icon_svg:
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:center;gap:1rem;padding:2rem 0 1rem 0;">
            <div style="width:32px;height:32px;">{icon_svg}</div>
            <h1 style="font-size:2rem;font-weight:600;color:#111827;margin:0;">AI DevOps Agent</h1>
        </div>
        <p style="text-align:center;color:#6b7280;font-size:0.9rem;">Autonomous Code Analysis powered by Gemini Flash 2.5</p>
        """, unsafe_allow_html=True)
    else:
        st.markdown(
            '<h1 style="text-align:center;">🔍 AI DevOps Agent</h1><p style="text-align:center;color:#6b7280;">Autonomous Analysis powered by Gemini Flash 2.5</p>',
            unsafe_allow_html=True
        )
st.markdown("---")

with st.sidebar:
    st.markdown("### ⚙ Configuration")
    google_api_key = st.text_input(
        "Google API Key",
        value=os.getenv("GOOGLE_API_KEY", ""),
        type="password",
        help="Get from: https://aistudio.google.com/app/apikey"
    )
    github_token = st.text_input(
        "GitHub Token",
        value=os.getenv("GITHUB_TOKEN", ""),
        type="password",
        help="Get from: https://github.com/settings/tokens"
    )
    st.markdown("---")
    st.markdown("### 📜 Analysis History")
    history = st.session_state.history_manager.get_history()
    if history:
        for idx, entry in enumerate(history):
            cols = st.columns([5, 1])
            with cols[0]:
                if st.button(f"📊 {entry['repo_name']}", key=f"hist_{idx}", use_container_width=True):
                    st.info(f"Score: {entry.get('health_score', 0)}/100 | Issues: {entry.get('total_issues', 0)}")
                st.caption(f"⏰ {entry.get('timestamp', 'Unknown')}")
            with cols[1]:
                if st.button("🗑", key=f"del_{idx}", help="Delete"):
                    st.session_state.history_manager.delete_entry(entry.get('id', idx))
                    st.rerun()
        if st.button("🗑 Clear All History", use_container_width=True):
            st.session_state.history_manager.clear_history()
            st.rerun()
    else:
        st.info("No analysis history yet")

def create_dimension_chart(scores):
    dimensions = ['Security', 'Performance', 'Architecture', 'Code Quality',
                  'Documentation', 'Dependencies', 'Best Practices']
    values = [
        scores.get('security', 0), scores.get('performance', 0),
        scores.get('architecture', 0), scores.get('code_quality', 0),
        scores.get('documentation', 0), scores.get('dependencies', 0),
        scores.get('best_practices', 0)
    ]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values, theta=dimensions, fill='toself',
        line=dict(color='#111827', width=2),
        fillcolor='rgba(17, 24, 39, 0.25)'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False, height=500, paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=80, r=80, t=40, b=40)
    )
    return fig

col1, col2 = st.columns([4, 1])
with col1:
    repo_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/username/repository",
        label_visibility="collapsed"
    )
with col2:
    analyze_btn = st.button("🔍 Analyze", use_container_width=True)

with st.expander("📚 Sample Repositories"):
    col1, col2 = st.columns(2)
    with col1:
        st.code("https://github.com/we45/Vulnerable-Flask-App")
        st.caption("⚠ Intentionally vulnerable")
    with col2:
        st.code("https://github.com/pallets/flask")
        st.caption("✅ Well-maintained")

if analyze_btn and repo_url:
    if not google_api_key or not github_token:
        st.error("⚠ Please provide both API keys in the sidebar")
    else:
        github_helper = GitHubHelper(github_token)
        deep_analyzer = DeepCodeAnalyzer(google_api_key)
        doc_gen = DocGenerator(google_api_key)
        progress_bar = st.progress(0)
        status_text = st.empty()
        try:
            status_text.markdown("📥 *Fetching repository...*")
            progress_bar.progress(15)
            time.sleep(0.3)
            files = github_helper.get_repo_files(repo_url, max_files=40)
            if not files:
                st.error("❌ Could not fetch repository. Check URL and token.")
            else:
                progress_bar.progress(25)
                st.success(f"✅ Fetched {len(files)} files")
                status_text.markdown("🔍 *Running deep analysis...*")
                progress_bar.progress(35)
                repo_structure = github_helper.get_repo_structure(repo_url)
                analysis = deep_analyzer.deep_analyze(files, repo_structure)
                progress_bar.progress(70)
                status_text.markdown("📝 *Generating improvements...*")
                progress_bar.progress(85)
                updated_files = doc_gen.generate_missing_docstrings(files, repo_structure)
                progress_bar.progress(100)
                status_text.empty()
                progress_bar.empty()
                st.session_state.analysis_results = {
                    'analysis': analysis,
                    'updated_files': updated_files,
                    'repo_url': repo_url
                }
                st.session_state.analysis_complete = True
                summary = analysis.get('summary', {})
                st.session_state.history_manager.add_analysis(repo_url, summary)
                st.balloons()
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            progress_bar.empty()
            status_text.empty()

if st.session_state.analysis_complete and st.session_state.analysis_results:
    st.markdown("---")
    results = st.session_state.analysis_results
    analysis = results['analysis']
    summary = analysis.get('summary', {})
    scores = analysis.get('scores', {})
    st.header("📊 Executive Summary")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: st.metric("Health Score", f"{summary.get('overall_health_score', 0)}/100")
    with col2: st.metric("Total Issues", summary.get('total_issues_found', 0))
    with col3: st.metric("Critical", summary.get('critical_security_issues', 0))
    with col4: st.metric("High Risk", summary.get('high_security_issues', 0))
    with col5: st.metric("Performance", summary.get('performance_bottlenecks', 0))
    recommendation = summary.get('recommendation', '')
    if '🚨' in recommendation:
        st.error(recommendation)
    elif '⚠' in recommendation:
        st.warning(recommendation)
    else:
        st.success(recommendation)
    st.markdown("---")
    st.header("🔬 Analysis Overview")
    chart = create_dimension_chart(scores)
    st.plotly_chart(chart, use_container_width=True)
    st.markdown("---")
    tabs = st.tabs([
        "🔒 Security", "⚡ Performance", "🏗 Architecture", "📝 Documentation",
        "✨ Quality", "📦 Dependencies", "✅ Practices"
    ])
    with tabs[0]:
        st.subheader("🔒 Security Analysis")
        sec = analysis.get('security', {})
        col1, col2 = st.columns([1, 4])
        with col1: st.metric("Score", f"{scores.get('security', 0)}/100")
        with col2: st.progress(scores.get('security', 0) / 100)
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Critical", len(sec.get('critical_issues', [])))
        with col2: st.metric("High", len(sec.get('high_severity', [])))
        with col3: st.metric("Medium", len(sec.get('medium_severity', [])))
        with col4: st.metric("Low", len(sec.get('low_severity', [])))
        critical_issues = sec.get('critical_issues', [])
        if critical_issues:
            st.error(f"🚨 {len(critical_issues)} Critical Issues")
            for idx, issue in enumerate(critical_issues[:5], 1):
                with st.expander(f"Issue {idx}: {issue.get('issue', 'Security vulnerability')}", expanded=(idx==1)):
                    st.markdown(f"*File:* {issue.get('file', 'Unknown')}")
                    st.markdown(f"*Description:* {issue.get('description', '')}")
                    if 'fix' in issue:
                        st.success("💡 Fix:")
                        st.code(issue['fix'], language="python")
        else:
            st.success("✅ No critical security issues!")
    with tabs[1]:
        st.subheader("⚡ Performance Analysis")
        perf = analysis.get('performance', {})
        col1, col2 = st.columns([1, 4])
        with col1: st.metric("Score", f"{scores.get('performance', 0)}/100")
        with col2: st.progress(scores.get('performance', 0) / 100)
        st.markdown("<br>", unsafe_allow_html=True)
        issues = perf.get('issues', [])
        st.metric("Performance Issues", len(issues))
        if issues:
            for idx, issue in enumerate(issues[:5], 1):
                impact = issue.get('impact', 'UNKNOWN')
                with st.expander(f"Issue {idx}: {issue.get('issue', 'Performance concern')} [{impact}]"):
                    st.markdown(f"*File:* {issue.get('file', 'Unknown')}")
                    st.markdown(f"*Impact:* {impact}")
                    st.markdown(f"*Description:* {issue.get('description', '')}")
                    if 'fix' in issue:
                        st.success("💡 Fix:")
                        st.code(issue['fix'], language="python")
        else:
            st.success("✅ No performance issues!")
    with tabs[2]:
        st.subheader("🏗 Architecture Analysis")
        arch = analysis.get('architecture', {})
        col1, col2 = st.columns([1, 4])
        with col1: st.metric("Score", f"{scores.get('architecture', 0)}/100")
        with col2: st.progress(scores.get('architecture', 0) / 100)
        st.markdown("<br>", unsafe_allow_html=True)
        pattern = arch.get('architecture_pattern', 'Unknown')
        st.info(f"*Pattern:* {pattern}")
        issues = arch.get('issues', [])
        if issues:
            for idx, issue in enumerate(issues[:5], 1):
                with st.expander(f"Issue {idx}: {issue.get('issue', 'Architecture concern')}"):
                    st.markdown(f"*Category:* {issue.get('category', 'Unknown')}")
                    st.markdown(f"*Severity:* {issue.get('severity', 'MEDIUM')}")
                    if 'file' in issue:
                        st.markdown(f"*File:* {issue.get('file')}")
                    if 'recommendation' in issue:
                        st.success(f"💡 Recommendation: {issue.get('recommendation')}")
        else:
            st.success("✅ Good architecture!")
    with tabs[3]:
        st.subheader("📝 Documentation Analysis")
        docs = analysis.get('documentation', {})
        col1, col2 = st.columns([1, 4])
        with col1: st.metric("Score", f"{scores.get('documentation', 0)}%")
        with col2: st.progress(scores.get('documentation', 0) / 100)
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Total Functions", docs.get('total_functions', 0))
        with col2: st.metric("Documented", docs.get('documented_functions', 0))
        with col3: st.metric("Missing", docs.get('undocumented_functions', 0))
        issues = docs.get('issues', [])
        if issues:
            st.markdown("### Functions Needing Documentation")
            for idx, issue in enumerate(issues[:10], 1):
                st.markdown(f"{idx}. {issue.get('file', '')} → *{issue.get('function', '')}*")
        else:
            st.success("✅ All functions documented!")
    with tabs[4]:
        st.subheader("✨ Code Quality Analysis")
        quality = analysis.get('code_quality', {})
        col1, col2 = st.columns([1, 4])
        with col1: st.metric("Score", f"{scores.get('code_quality', 0)}/100")
        with col2: st.progress(scores.get('code_quality', 0) / 100)
        st.markdown("<br>", unsafe_allow_html=True)
        issues = quality.get('issues', [])
        if issues:
            for idx, issue in enumerate(issues[:5], 1):
                with st.expander(f"Issue {idx}: {issue.get('issue', 'Quality concern')}"):
                    st.markdown(f"*Type:* {issue.get('type', 'Unknown')}")
                    st.markdown(f"*File:* {issue.get('file', 'Unknown')}")
                    if 'suggestion' in issue:
                        st.success(f"💡 Suggestion: {issue.get('suggestion')}")
        else:
            st.success("✅ Good code quality!")
    with tabs[5]:
        st.subheader("📦 Dependencies Analysis")
        deps = analysis.get('dependencies', {})
        col1, col2 = st.columns([1, 4])
        with col1: st.metric("Score", f"{scores.get('dependencies', 0)}/100")
        with col2: st.progress(scores.get('dependencies', 0) / 100)
        st.markdown("<br>", unsafe_allow_html=True)
        issues = deps.get('issues', [])
        if issues:
            for idx, issue in enumerate(issues[:5], 1):
                with st.expander(f"Issue {idx}: {issue.get('package', 'Unknown')}"):
                    st.markdown(f"*Package:* {issue.get('package')}")
                    st.markdown(f"*Issue:* {issue.get('issue', '')}")
                    if 'recommended_version' in issue:
                        st.success(f"💡 Update to: {issue.get('recommended_version')}")
        else:
            st.success("✅ Dependencies up to date!")
    with tabs[6]:
        st.subheader("✅ Best Practices Analysis")
        bp = analysis.get('best_practices', {})
        col1, col2 = st.columns([1, 4])
        with col1: st.metric("Score", f"{scores.get('best_practices', 0)}/100")
        with col2: st.progress(scores.get('best_practices', 0) / 100)
        st.markdown("<br>", unsafe_allow_html=True)
        issues = bp.get('issues', [])
        if issues:
            for idx, issue in enumerate(issues[:5], 1):
                with st.expander(f"Issue {idx}: {issue.get('issue', 'Best practice violation')}"):
                    st.markdown(f"*Category:* {issue.get('category', 'Unknown')}")
                    if 'recommendation' in issue:
                        st.success(f"💡 Recommendation: {issue.get('recommendation')}")
                    if 'example' in issue:
                        st.code(issue['example'], language="python")
        else:
            st.success("✅ Following best practices!")
    st.markdown("---")
    if results['updated_files']:
        st.header("🤖 Generated Fixes")
        st.success(f"✨ Improved {len(results['updated_files'])} files")
        with st.expander("📄 Preview Documentation"):
            for fp, content in list(results['updated_files'].items())[:2]:
                st.markdown(f"{fp}")
                st.code(content[:500] + ("..." if len(content) > 500 else ""), language="python")
        if st.button("✨ Create Pull Request", type="primary"):
            try:
                github_helper = GitHubHelper(github_token)
                branch_name = f"ai-fixes-{int(time.time())}"
                pr_body = f"""## 🤖 AI-Generated Improvements

Health Score: {summary.get('overall_health_score')}/100
Issues Fixed: {len(results['updated_files'])} files

{summary.get('recommendation', '')}

Generated by AI DevOps Agent
"""
                pr_url = github_helper.create_pull_request(
                    repo_url=results['repo_url'],
                    branch_name=branch_name,
                    files_to_update=results['updated_files'],
                    pr_title="🤖 AI Agent: Code improvements",
                    pr_body=pr_body
                )
                if pr_url:
                    st.success("✅ Pull request created!")
                    st.markdown(f"[🔗 View PR]({pr_url})")
                else:
                    st.error("❌ PR creation failed")
            except Exception as e:
                st.error(f"❌ Error: {e}")

st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#9ca3af;padding:2rem 0;'>
    <p style='font-size:0.9rem;'>AI Developer Ops Agent • Powered by Gemini Flash 2.5</p>
    <p style='font-size:0.8rem;'>Built for GenAIVersity Hackathon 2025</p>
</div>
""", unsafe_allow_html=True)
