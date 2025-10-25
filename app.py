"""
AI Developer Ops Agent - Streamlit UI with Deep Analysis
"""
import streamlit as st
import os
from dotenv import load_dotenv
import time
from datetime import datetime

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
    st.header("🔬 Detailed Analysis")
    
    tabs = st.tabs([
        "🔒 Security",
        "⚡ Performance",
        "🏗 Architecture",
        "📝 Documentation",
        "✨ Code Quality",
        "📦 Dependencies",
        "✅ Best Practices"
    ])
    
    with tabs[0]:  # Security
        st.subheader("🔒 Security Analysis")
        sec = analysis.get('security', {})
        
        if isinstance(sec, dict):
            # Critical Issues
            critical_issues = sec.get('critical_issues', [])
            if critical_issues:
                st.error(f"🚨 *{len(critical_issues)} Critical Security Issues Found*")
                for idx, issue in enumerate(critical_issues, 1):
                    with st.expander(f"Critical Issue {idx}", expanded=True):
                        st.json(issue)
            
            # High Severity
            high_issues = sec.get('high_severity', [])
            if high_issues:
                st.warning(f"⚠ *{len(high_issues)} High Severity Issues*")
                for idx, issue in enumerate(high_issues, 1):
                    with st.expander(f"High Severity {idx}"):
                        st.json(issue)
            
            # Medium and Low
            medium = sec.get('medium_severity', [])
            low = sec.get('low_severity', [])
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"Medium: {len(medium)}")
            with col2:
                st.success(f"Low: {len(low)}")
            
            # Full details
            with st.expander("📋 View complete security analysis"):
                st.json(sec)
        else:
            st.json(sec)
    
    with tabs[1]:  # Performance
        st.subheader("⚡ Performance Analysis")
        perf = analysis.get('performance', {})
        
        if isinstance(perf, dict) and 'issues' in perf:
            issues = perf.get('issues', [])
            st.metric("Performance Issues Found", len(issues))
            
            for idx, issue in enumerate(issues[:10], 1):
                if isinstance(issue, dict):
                    impact = issue.get('impact', 'UNKNOWN')
                    with st.expander(f"Issue {idx}: {impact} Impact"):
                        st.json(issue)
                else:
                    st.write(issue)
            
            with st.expander("📋 View complete performance analysis"):
                st.json(perf)
        else:
            st.json(perf)
    
    with tabs[2]:  # Architecture
        st.subheader("🏗 Architecture Analysis")
        arch = analysis.get('architecture', {})
        st.json(arch)
    
    with tabs[3]:  # Documentation
        st.subheader("📝 Documentation Analysis")
        docs = analysis.get('documentation', {})
        
        if isinstance(docs, dict):
            coverage = docs.get('coverage_percentage', 'N/A')
            st.metric("Documentation Coverage", f"{coverage}%")
            
            with st.expander("📋 View documentation analysis"):
                st.json(docs)
        else:
            st.json(docs)
    
    with tabs[4]:  # Code Quality
        st.subheader("✨ Code Quality Analysis")
        quality = analysis.get('code_quality', {})
        st.json(quality)
    
    with tabs[5]:  # Dependencies
        st.subheader("📦 Dependencies Analysis")
        deps = analysis.get('dependencies', {})
        st.json(deps)
    
    with tabs[6]:  # Best Practices
        st.subheader("✅ Best Practices Analysis")
        bp = analysis.get('best_practices', {})
        st.json(bp)
    
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
