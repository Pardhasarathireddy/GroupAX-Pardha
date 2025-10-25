"""
AI Developer Ops Agent - Streamlit UI with Deep Analysis
"""
import streamlit as st
import os
from dotenv import load_dotenv
import time
from datetime import datetime
import plotly.graph_objects as go

from utils.github_helper import GitHubHelper
from agents.deep_analyzer import DeepCodeAnalyzer
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

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(120deg, #2196F3, #00BCD4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2196F3;
    }
    .priority-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .critical { background: #f44336; color: white; }
    .high { background: #ff9800; color: white; }
    .medium { background: #ffc107; color: black; }
    .low { background: #4caf50; color: white; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🤖 AI Developer Ops Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Autonomous code analysis powered by Gemini Flash 2.5</div>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙ Configuration")
    
    google_api_key = st.text_input(
        "Google API Key",
        value=os.getenv("GOOGLE_API_KEY", ""),
        type="password",
        help="Get your key from: https://aistudio.google.com/app/apikey"
    )
    
    github_token = st.text_input(
        "GitHub Token",
        value=os.getenv("GITHUB_TOKEN", ""),
        type="password",
        help="Create token at: https://github.com/settings/tokens"
    )
    
    st.markdown("---")
    st.markdown("### 🎯 Analysis Features")
    st.markdown("""
    - 🔒 *Security Scanning*
    - ⚡ *Performance Analysis*
    - 🏗 *Architecture Review*
    - 📝 *Documentation Quality*
    - ✨ *Code Quality Metrics*
    - 📦 *Dependency Check*
    - ✅ *Best Practices*
    """)
    
    st.markdown("---")
    st.markdown("### 🚀 Autonomous Actions")
    st.markdown("""
    - Auto-generate documentation
    - Create pull requests
    - Fix common issues
    - Improve code quality
    """)
    
    st.markdown("---")
    st.info("💡 *Tip:* Use repos with actual code for best results!")
    def create_dimension_chart(scores):
        """Create professional radar chart with 0-100 scale"""
        dimensions = ['Security', 'Performance', 'Architecture', 'Code Quality', 
                    'Documentation', 'Dependencies', 'Best Practices']
        
        values = [
            scores.get('security', 0),
            scores.get('performance', 0),
            scores.get('architecture', 0),
            scores.get('code_quality', 0),
            scores.get('documentation', 0),
            scores.get('dependencies', 0),
            scores.get('best_practices', 0)
        ]
        
        # Add colors based on score ranges
        colors = []
        for v in values:
            if v >= 80:
                colors.append('#4caf50')  # Green - Excellent
            elif v >= 60:
                colors.append('#2196f3')  # Blue - Good
            elif v >= 40:
                colors.append('#ff9800')  # Orange - Needs work
            else:
                colors.append('#f44336')  # Red - Critical
        
        fig = go.Figure()
        
        # Main trace
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=dimensions,
            fill='toself',
            name='Scores',
            line=dict(color='#0070f3', width=3),
            fillcolor='rgba(0, 112, 243, 0.25)',
            marker=dict(size=10, color=colors, line=dict(color='white', width=2))
        ))
        
        # Add reference line at 70 (good threshold)
        fig.add_trace(go.Scatterpolar(
            r=[70, 70, 70, 70, 70, 70, 70],
            theta=dimensions,
            mode='lines',
            name='Target (70)',
            line=dict(color='rgba(76, 175, 80, 0.5)', width=2, dash='dash'),
            showlegend=False
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickmode='array',
                    tickvals=[0, 20, 40, 60, 80, 100],
                    ticktext=['0', '20', '40', '60', '80', '100'],
                    showticklabels=True,
                    gridcolor='rgba(128, 128, 128, 0.2)',
                    tickfont=dict(size=11, color='#666'),
                    showline=False
                ),
                angularaxis=dict(
                    gridcolor='rgba(128, 128, 128, 0.2)',
                    tickfont=dict(size=13, color='#333', weight='bold'),
                    linecolor='rgba(128, 128, 128, 0.3)'
                ),
                bgcolor='rgba(250, 250, 250, 0.3)'
            ),
            showlegend=False,
            height=550,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=100, r=100, t=50, b=50),
            font=dict(family='Inter, Arial, sans-serif')
        )
        
        return fig

# Main content
col1, col2 = st.columns([3, 1])

with col1:
    repo_url = st.text_input(
        "🔗 GitHub Repository URL",
        placeholder="https://github.com/username/repository",
        help="Enter a public repository URL to analyze"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = st.button("🔍 Analyze Repository", type="primary", use_container_width=True)

# Sample repos
with st.expander("📚 Need a test repository? Try these:"):
    col1, col2 = st.columns(2)
    with col1:
        st.code("https://github.com/mjhea0/flaskr-tdd", language="text")
        st.caption("✅ Flask Todo App - Good for testing")
    with col2:
        st.code("https://github.com/geekcomputers/Python", language="text")
        st.caption("✅ Python Scripts - Multiple issues")

# Analysis workflow
if analyze_btn and repo_url:
    if not google_api_key or not github_token:
        st.error("⚠ Please provide both API keys in the sidebar")
    else:
        # Initialize helpers
        github_helper = GitHubHelper(github_token)
        deep_analyzer = DeepCodeAnalyzer(google_api_key)
        doc_gen = DocGenerator(google_api_key)
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Fetch repository
            status_text.markdown("📥 *Fetching repository files...*")
            progress_bar.progress(15)
            time.sleep(0.3)
            
            files = github_helper.get_repo_files(repo_url, max_files=50)
            
            if not files:
                st.error("❌ Could not fetch repository files. Please check:")
                st.markdown("""
                - Repository URL is correct
                - Repository is public
                - GitHub token has proper permissions
                """)
            else:
                progress_bar.progress(25)
                st.success(f"✅ Fetched {len(files)} files from repository")
                
                # Step 2: Deep Analysis
                status_text.markdown("🔍 *Running deep multi-dimensional analysis...*")
                status_text.caption("Analyzing: Security • Performance • Architecture • Quality • Documentation")
                progress_bar.progress(35)
                time.sleep(0.5)
                
                repo_structure = github_helper.get_repo_structure(repo_url)
                
                with st.spinner("🧠 AI is analyzing your codebase in depth..."):
                    analysis = deep_analyzer.deep_analyze(files, repo_structure)
                
                progress_bar.progress(70)
                st.success("✅ Deep analysis complete - 7 dimensions analyzed!")
                
                # Step 3: Generate documentation
                status_text.markdown("📝 *Generating documentation improvements...*")
                progress_bar.progress(80)
                time.sleep(0.3)
                
                with st.spinner("📚 Generating missing docstrings..."):
                    updated_files = doc_gen.generate_missing_docstrings(files, repo_structure)
                
                progress_bar.progress(95)
                
                # Completion
                progress_bar.progress(100)
                status_text.markdown("✅ *Analysis complete!*")
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
                
                # Store results
                st.session_state.analysis_results = {
                    'analysis': analysis,
                    'updated_files': updated_files,
                    'total_files': len(files),
                    'repo_url': repo_url
                }
                st.session_state.analysis_complete = True
                
                st.balloons()
                
        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
            import traceback
            with st.expander("🔍 View error details"):
                st.code(traceback.format_exc())
            progress_bar.empty()
            status_text.empty()

# Display results
if st.session_state.analysis_complete and st.session_state.analysis_results:
    st.markdown("---")
    
    results = st.session_state.analysis_results
    analysis = results['analysis']
    
    # Executive Summary Section
    st.header("📊 Executive Summary")
    
    summary = analysis.get('summary', {})
    
    # Key Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        health_score = summary.get('overall_health_score', 0)
        score_color = "🟢" if health_score >= 80 else "🟡" if health_score >= 60 else "🔴"
        st.metric(
            "Health Score",
            f"{health_score}/100",
            delta=f"{score_color}"
        )
    
    with col2:
        total_issues = summary.get('total_issues_found', 0)
        st.metric(
            "Total Issues",
            total_issues
        )
    
    with col3:
        critical = summary.get('critical_security_issues', 0)
        st.metric(
            "Critical Security",
            critical,
            delta="🚨" if critical > 0 else "✅"
        )
    
    with col4:
        high_sec = summary.get('high_security_issues', 0)
        st.metric(
            "High Security",
            high_sec,
            delta="⚠" if high_sec > 0 else "✅"
        )
    
    with col5:
        perf_issues = summary.get('performance_bottlenecks', 0)
        st.metric(
            "Performance",
            perf_issues,
            delta="⚡" if perf_issues > 0 else "✅"
        )
    
    # Overall Recommendation
    recommendation = summary.get('recommendation', 'Analysis complete')
    if '🚨' in recommendation or 'URGENT' in recommendation:
        st.error(recommendation)
    elif '⚠' in recommendation:
        st.warning(recommendation)
    else:
        st.success(recommendation)
    
    st.markdown("---")
    
    # Priority Fixes Section
    st.header("🎯 Top Priority Fixes")
    
    priorities = analysis.get('priority_fixes', [])
    
    if priorities:
        for i, priority in enumerate(priorities[:5], 1):
            priority_level = priority.get('priority', 'MEDIUM')
            category = priority.get('category', 'General')
            action = priority.get('action', 'Review')
            issue = priority.get('issue', {})
            
            badge_class = priority_level.lower()
            
            with st.expander(f"{i}.** [{priority_level}] {category} - {action}", expanded=(i==1)):
                if isinstance(issue, dict):
                    # Display issue details
                    if 'description' in issue:
                        st.markdown(f"*Description:* {issue['description']}")
                    if 'file' in issue:
                        st.code(f"File: {issue['file']}", language="text")
                    if 'severity' in issue:
                        st.markdown(f"*Severity:* {issue['severity']}")
                    if 'fix_recommendation' in issue:
                        st.markdown("*Recommended Fix:*")
                        st.code(issue['fix_recommendation'], language="python")
                    
                    # Show full issue as JSON for details
                    with st.expander("View full details"):
                        st.json(issue)
                else:
                    st.write(issue)
    else:
        st.info("✅ No critical priority fixes identified!")
    
    st.markdown("---")
    
    # Detailed Analysis Tabs
   # Detailed Analysis Tabs
    st.header("🔬 Detailed Analysis")
    
    # Get scores
    scores = analysis.get('scores', {})
    
    # Show radar chart
    st.markdown("### 📊 Dimension Scores Overview")
    chart = create_dimension_chart(scores)
    st.plotly_chart(chart, use_container_width=True)
    
    st.markdown("---")
    
    tabs = st.tabs([
        "🔒 Security",
        "⚡ Performance",
        "🏗 Architecture",
        "📝 Documentation",
        "✨ Code Quality",
        "📦 Dependencies",
        "✅ Best Practices"
    ])
    
    # Security Tab
    with tabs[0]:
        st.subheader("🔒 Security Analysis")
        sec = analysis.get('security', {})
        sec_score = scores.get('security', 0)
        
        # Score display
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Security Score", f"{sec_score}/100")
        with col2:
            st.progress(sec_score / 100)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Issue counts
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            crit_count = len(sec.get('critical_issues', []))
            st.metric("Critical", crit_count)
        with col2:
            high_count = len(sec.get('high_severity', []))
            st.metric("High", high_count)
        with col3:
            med_count = len(sec.get('medium_severity', []))
            st.metric("Medium", med_count)
        with col4:
            low_count = len(sec.get('low_severity', []))
            st.metric("Low", low_count)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Display critical issues
        critical_issues = sec.get('critical_issues', [])
        if critical_issues:
            st.error(f"🚨 {len(critical_issues)} Critical Issues")
            for idx, issue in enumerate(critical_issues[:5], 1):
                with st.expander(f"Critical Issue {idx}: {issue.get('issue', 'Security vulnerability')}", expanded=(idx==1)):
                    st.markdown(f"*File:* {issue.get('file', 'Unknown')}")
                    if 'line' in issue:
                        st.markdown(f"*Location:* {issue.get('line')}")
                    st.markdown(f"*Description:* {issue.get('description', issue.get('issue', ''))}")
                    if 'exploit' in issue:
                        st.warning(f"*Risk:* {issue.get('exploit')}")
                    if 'fix' in issue:
                        st.success("💡 Fix:")
                        st.code(issue.get('fix'), language="python")
        
        # Display high severity
        high_issues = sec.get('high_severity', [])
        if high_issues:
            st.warning(f"⚠ {len(high_issues)} High Severity Issues")
            for idx, issue in enumerate(high_issues[:3], 1):
                with st.expander(f"High Severity {idx}: {issue.get('issue', 'Security issue')}"):
                    st.markdown(f"*File:* {issue.get('file', 'Unknown')}")
                    st.markdown(f"*Description:* {issue.get('description', '')}")
                    if 'fix' in issue:
                        st.code(issue.get('fix'), language="python")
        
        if not critical_issues and not high_issues:
            st.success("✅ No critical security issues found!")
    
    # Performance Tab
    with tabs[1]:
        st.subheader("⚡ Performance Analysis")
        perf = analysis.get('performance', {})
        perf_score = scores.get('performance', 0)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Performance Score", f"{perf_score}/100")
        with col2:
            st.progress(perf_score / 100)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        issues = perf.get('issues', [])
        st.metric("Performance Issues", len(issues))
        
        if issues:
            for idx, issue in enumerate(issues[:8], 1):
                impact = issue.get('impact', 'UNKNOWN')
                with st.expander(f"Issue {idx}: {issue.get('issue', 'Performance issue')} [{impact}]"):
                    st.markdown(f"*File:* {issue.get('file', 'Unknown')}")
                    if 'location' in issue:
                        st.markdown(f"*Location:* {issue.get('location')}")
                    st.markdown(f"*Impact:* {impact}")
                    if 'current_complexity' in issue:
                        st.markdown(f"*Complexity:* {issue.get('current_complexity')}")
                    st.markdown(f"*Description:* {issue.get('description', '')}")
                    if 'fix' in issue:
                        st.success("💡 Optimization:")
                        st.code(issue.get('fix'), language="python")
                    if 'improvement' in issue:
                        st.info(f"*Expected Gain:* {issue.get('improvement')}")
        else:
            st.success("✅ No performance issues found!")
    
    # Architecture Tab
    with tabs[2]:
        st.subheader("🏗 Architecture Analysis")
        arch = analysis.get('architecture', {})
        arch_score = scores.get('architecture', 0)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Architecture Score", f"{arch_score}/100")
        with col2:
            st.progress(arch_score / 100)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        pattern = arch.get('architecture_pattern', 'Unknown')
        st.info(f"*Pattern:* {pattern}")
        
        issues = arch.get('issues', [])
        if issues:
            for idx, issue in enumerate(issues[:8], 1):
                with st.expander(f"Issue {idx}: {issue.get('issue', 'Architecture concern')}"):
                    st.markdown(f"*Category:* {issue.get('category', 'Unknown')}")
                    st.markdown(f"*Severity:* {issue.get('severity', 'MEDIUM')}")
                    if 'file' in issue:
                        st.markdown(f"*File:* {issue.get('file')}")
                    st.markdown(f"*Description:* {issue.get('description', '')}")
                    if 'recommendation' in issue:
                        st.success(f"💡 Recommendation:** {issue.get('recommendation')}")
        else:
            st.success("✅ Good architecture!")
    
    # Documentation Tab
    with tabs[3]:
        st.subheader("📝 Documentation Analysis")
        docs = analysis.get('documentation', {})
        doc_score = scores.get('documentation', 0)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Documentation Score", f"{doc_score}%")
        with col2:
            st.progress(doc_score / 100)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Functions", docs.get('total_functions', 0))
        with col2:
            st.metric("Documented", docs.get('documented_functions', 0))
        with col3:
            st.metric("Missing Docs", docs.get('undocumented_functions', 0))
        
        issues = docs.get('issues', [])
        if issues:
            st.markdown("### Functions Needing Documentation")
            for idx, issue in enumerate(issues[:15], 1):
                st.markdown(f"{idx}. {issue.get('file', '')} → *{issue.get('function', '')}*")
        else:
            st.success("✅ All functions documented!")
    
    # Code Quality Tab
    with tabs[4]:
        st.subheader("✨ Code Quality Analysis")
        quality = analysis.get('code_quality', {})
        quality_score = scores.get('code_quality', 0)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Quality Score", f"{quality_score}/100")
        with col2:
            st.progress(quality_score / 100)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        issues = quality.get('issues', [])
        if issues:
            for idx, issue in enumerate(issues[:10], 1):
                with st.expander(f"Issue {idx}: {issue.get('issue', 'Quality concern')}"):
                    st.markdown(f"*Type:* {issue.get('type', 'Unknown')}")
                    st.markdown(f"*Severity:* {issue.get('severity', 'MEDIUM')}")
                    st.markdown(f"*File:* {issue.get('file', 'Unknown')}")
                    st.markdown(f"*Description:* {issue.get('description', '')}")
                    if 'suggestion' in issue:
                        st.success(f"💡 Suggestion:** {issue.get('suggestion')}")
        else:
            st.success("✅ Good code quality!")
    
    # Dependencies Tab
    with tabs[5]:
        st.subheader("📦 Dependencies Analysis")
        deps = analysis.get('dependencies', {})
        deps_score = scores.get('dependencies', 0)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Dependencies Score", f"{deps_score}/100")
        with col2:
            st.progress(deps_score / 100)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        issues = deps.get('issues', [])
        if issues:
            for idx, issue in enumerate(issues[:10], 1):
                with st.expander(f"Issue {idx}: {issue.get('package', 'Unknown')}"):
                    st.markdown(f"*Package:* {issue.get('package')}")
                    st.markdown(f"*Current:* {issue.get('current_version', 'Unknown')}")
                    st.markdown(f"*Issue:* {issue.get('issue', '')}")
                    if 'recommended_version' in issue:
                        st.success(f"💡 Update to:** {issue.get('recommended_version')}")
        else:
            st.success("✅ Dependencies up to date!")
    
    # Best Practices Tab
    with tabs[6]:
        st.subheader("✅ Best Practices Analysis")
        bp = analysis.get('best_practices', {})
        bp_score = scores.get('best_practices', 0)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Best Practices Score", f"{bp_score}/100")
        with col2:
            st.progress(bp_score / 100)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        issues = bp.get('issues', [])
        if issues:
            for idx, issue in enumerate(issues[:10], 1):
                with st.expander(f"Issue {idx}: {issue.get('issue', 'Best practice violation')}"):
                    st.markdown(f"*Category:* {issue.get('category', 'Unknown')}")
                    if 'file' in issue:
                        st.markdown(f"*File:* {issue.get('file')}")
                    st.markdown(f"*Issue:* {issue.get('issue', '')}")
                    if 'recommendation' in issue:
                        st.success(f"💡 Recommendation:** {issue.get('recommendation')}")
                    if 'example' in issue:
                        st.code(issue.get('example'), language="python")
        else:
            st.success("✅ Following best practices!")
    
    st.markdown("---")
    
    # Auto-fix section
    if results['updated_files']:
        st.header("🤖 Autonomous Fixes Generated")
        
        st.success(f"✨ Generated improvements for *{len(results['updated_files'])}* files")
        
        # Preview fixes
        with st.expander("👀 Preview generated documentation", expanded=True):
            for filepath, content in list(results['updated_files'].items())[:3]:
                st.markdown(f"*File:* {filepath}")
                preview_length = min(len(content), 800)
                st.code(content[:preview_length] + ("..." if len(content) > 800 else ""), language="python")
                st.markdown("---")
        
        # Create PR section
        st.markdown("### 📤 Create Pull Request")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            pr_title = st.text_input(
                "PR Title",
                value="🤖 AI Agent: Documentation improvements & code quality fixes"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            create_pr_btn = st.button("✨ Create Pull Request", type="primary", use_container_width=True)
        
        if create_pr_btn:
            with st.spinner("Creating pull request..."):
                try:
                    github_helper = GitHubHelper(github_token)
                    branch_name = f"ai-agent-improvements-{int(time.time())}"
                    
                    # Generate detailed PR body
                    pr_body = f"""## 🤖 AI-Generated Improvements

This PR was automatically created by the *AI Developer Ops Agent* powered by Gemini Flash 2.5.

### 📊 Analysis Summary
- *Files Analyzed:* {results['total_files']}
- *Health Score:* {summary.get('overall_health_score', 'N/A')}/100
- *Total Issues Found:* {summary.get('total_issues_found', 0)}
- *Critical Security Issues:* {summary.get('critical_security_issues', 0)}

### ✨ Changes Made
- ✅ Added missing docstrings ({len(results['updated_files'])} files)
- ✅ Improved code documentation
- ✅ Enhanced code readability

### 🎯 Priority Fixes Addressed
{chr(10).join([f"- {p.get('category')}: {p.get('action')}" for p in priorities[:5]])}

### 📝 Recommendation
{recommendation}

---
Generated with ❤ by AI Developer Ops Agent using Gemini Flash 2.5
Hackathon Project: GenAIVersity 2025
"""
                    
                    pr_url = github_helper.create_pull_request(
                        repo_url=results['repo_url'],
                        branch_name=branch_name,
                        files_to_update=results['updated_files'],
                        pr_title=pr_title,
                        pr_body=pr_body
                    )
                    
                    if pr_url:
                        st.success(f"✅ Pull request created successfully!")
                        st.markdown(f"### [🔗 View Pull Request]({pr_url})")
                        st.balloons()
                    else:
                        st.error("❌ Failed to create pull request. Check your GitHub token permissions.")
                        
                except Exception as e:
                    st.error(f"❌ Error creating PR: {str(e)}")
                    with st.expander("View error details"):
                        import traceback
                        st.code(traceback.format_exc())
    else:
        st.info("ℹ No automatic fixes generated. The code quality is good, or manual review is recommended for complex issues.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <h3>🚀 AI Developer Ops Agent</h3>
    <p>Powered by <strong>Google Gemini Flash 2.5</strong></p>
    <p>Built for <strong>GenAIVersity Hackathon 2025</strong></p>
    <p style='font-size: 0.9rem; margin-top: 1rem;'>
        🔒 Security • ⚡ Performance • 🏗 Architecture • 📝 Documentation
    </p>
</div>
""", unsafe_allow_html=True)
